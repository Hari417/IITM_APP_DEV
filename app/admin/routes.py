from datetime import datetime

from flask import abort, flash, redirect, render_template, url_for

from app.admin import admin
from app.admin.forms import (
    CourseForm,
    CriterionForm,
    ExaminerAssignmentForm,
    ExaminationForm,
    RubricForm,
)
from app.decorators import role_required
from app.extensions import db
from app.models import (
    Course,
    Examination,
    ExaminerAssignment,
    ExaminerProfile,
    Rubric,
    RubricCriterion,
    User,
)


@admin.get("/")
@role_required("admin")
def dashboard():
    examiners = (
        db.session.query(ExaminerProfile)
        .join(ExaminerProfile.user)
        .order_by(User.created_at.desc())
        .all()
    )
    statistics = {
        "users": db.session.query(User).count(),
        "students": db.session.query(User).filter_by(role="student").count(),
        "examiners": db.session.query(User).filter_by(role="examiner").count(),
        "pending_examiners": (
            db.session.query(ExaminerProfile)
            .filter_by(approval_status="pending")
            .count()
        ),
    }
    return render_template(
        "admin/dashboard.html",
        examiners=examiners,
        statistics=statistics
    )


@admin.route("/courses", methods=["GET", "POST"])
@role_required("admin")
def courses():
    form = CourseForm()
    if form.validate_on_submit():
        code = form.course_code.data.strip().upper()
        if db.session.query(Course).filter_by(course_code=code).first():
            form.course_code.errors.append("Course code already exists.")
        else:
            db.session.add(Course(
                course_code=code,
                course_name=form.course_name.data.strip(),
                description=form.description.data.strip() or None
            ))
            db.session.commit()
            flash("Course created successfully.", "success")
            return redirect(url_for("admin.courses"))

    course_list = db.session.query(Course).order_by(Course.course_code).all()
    return render_template(
        "admin/courses.html",
        form=form,
        courses=course_list
    )


@admin.post("/courses/<int:course_id>/toggle")
@role_required("admin")
def toggle_course(course_id):
    course = db.session.get(Course, course_id)
    if course is None:
        abort(404)
    course.is_active = not course.is_active
    db.session.commit()
    flash(
        f"Course {'activated' if course.is_active else 'deactivated'}.",
        "success"
    )
    return redirect(url_for("admin.courses"))


@admin.route("/examinations", methods=["GET", "POST"])
@role_required("admin")
def examinations():
    form = ExaminationForm()
    courses = (
        db.session.query(Course)
        .filter_by(is_active=True)
        .order_by(Course.course_code)
        .all()
    )
    form.course_id.choices = [(course.course_id, course.course_code)
                              for course in courses]
    if form.validate_on_submit():
        if db.session.get(Course, form.course_id.data) is None:
            form.course_id.errors.append("Select a valid course.")
        else:
            db.session.add(Examination(
                course_id=form.course_id.data,
                exam_name=form.exam_name.data.strip(),
                exam_type=form.exam_type.data,
                duration_minutes=form.duration_minutes.data,
                maximum_marks=form.maximum_marks.data,
                slot_creation_start=form.slot_creation_start.data,
                slot_creation_end=form.slot_creation_end.data,
                booking_start=form.booking_start.data,
                booking_end=form.booking_end.data,
                status=form.status.data
            ))
            db.session.commit()
            flash("Examination created successfully.", "success")
            return redirect(url_for("admin.examinations"))

    exam_list = (
        db.session.query(Examination)
        .join(Examination.course)
        .order_by(Examination.created_at.desc())
        .all()
    )
    return render_template(
        "admin/examinations.html",
        form=form,
        examinations=exam_list
    )


@admin.route(
    "/examinations/<int:exam_id>/assign-examiner",
    methods=["GET", "POST"]
)
@role_required("admin")
def assign_examiner(exam_id):
    exam = db.session.get(Examination, exam_id)
    if exam is None:
        abort(404)

    form = ExaminerAssignmentForm()
    available_examiners = (
        db.session.query(ExaminerProfile)
        .join(ExaminerProfile.user)
        .filter(
            ExaminerProfile.approval_status == "approved",
            User.is_active.is_(True)
        )
        .order_by(User.full_name)
        .all()
    )
    form.examiner_id.choices = [
        (profile.examiner_id, profile.user.full_name)
        for profile in available_examiners
    ]

    if form.validate_on_submit():
        already_assigned = db.session.query(ExaminerAssignment).filter_by(
            exam_id=exam.exam_id,
            examiner_id=form.examiner_id.data
        ).first()
        if already_assigned:
            form.examiner_id.errors.append(
                "This examiner is already assigned to this examination."
            )
        else:
            db.session.add(ExaminerAssignment(
                exam_id=exam.exam_id,
                examiner_id=form.examiner_id.data,
                assigned_by=current_admin_id()
            ))
            db.session.commit()
            flash("Examiner assigned successfully.", "success")
            return redirect(url_for(
                "admin.assign_examiner",
                exam_id=exam.exam_id
            ))

    assignments = (
        db.session.query(ExaminerAssignment)
        .join(ExaminerAssignment.examiner)
        .filter(ExaminerAssignment.exam_id == exam.exam_id)
        .order_by(User.full_name)
        .all()
    )
    return render_template(
        "admin/assign_examiner.html",
        exam=exam,
        form=form,
        assignments=assignments
    )


@admin.route("/examinations/<int:exam_id>/rubric", methods=["GET", "POST"])
@role_required("admin")
def rubric(exam_id):
    exam = db.session.get(Examination, exam_id)
    if exam is None:
        abort(404)

    rubric_form = RubricForm()
    criterion_form = CriterionForm()
    active_rubric = (
        db.session.query(Rubric)
        .filter_by(exam_id=exam.exam_id, is_active=True)
        .order_by(Rubric.version.desc())
        .first()
    )

    if rubric_form.validate_on_submit():
        existing = db.session.query(Rubric).filter_by(
            exam_id=exam.exam_id,
            version=rubric_form.version.data
        ).first()
        if existing:
            rubric_form.version.errors.append(
                "This rubric version already exists."
            )
        else:
            if active_rubric:
                active_rubric.is_active = False
            active_rubric = Rubric(
                exam_id=exam.exam_id,
                version=rubric_form.version.data,
                is_active=True
            )
            db.session.add(active_rubric)
            db.session.commit()
            flash("Rubric created successfully.", "success")
            return redirect(url_for("admin.rubric", exam_id=exam.exam_id))

    return render_template(
        "admin/rubric.html",
        exam=exam,
        rubric_form=rubric_form,
        criterion_form=criterion_form,
        rubric=active_rubric
    )


@admin.post("/rubrics/<int:rubric_id>/criteria")
@role_required("admin")
def add_criterion(rubric_id):
    rubric = db.session.get(Rubric, rubric_id)
    if rubric is None:
        abort(404)

    form = CriterionForm()
    if form.validate_on_submit():
        db.session.add(RubricCriterion(
            rubric_id=rubric.rubric_id,
            criterion_name=form.criterion_name.data.strip(),
            description=form.description.data.strip() or None,
            maximum_marks=form.maximum_marks.data,
            weightage=form.weightage.data
        ))
        db.session.commit()
        flash("Rubric criterion added successfully.", "success")
    else:
        flash("Please correct the criterion details.", "danger")
    return redirect(url_for("admin.rubric", exam_id=rubric.exam_id))


@admin.post("/examiners/<int:examiner_id>/approve")
@role_required("admin")
def approve_examiner(examiner_id):
    profile = db.session.get(ExaminerProfile, examiner_id)
    if profile is None:
        abort(404)

    profile.approval_status = "approved"
    profile.approved_by = current_admin_id()
    profile.approved_at = datetime.utcnow()
    profile.user.is_active = True
    db.session.commit()
    flash("Examiner approved successfully.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.post("/examiners/<int:examiner_id>/reject")
@role_required("admin")
def reject_examiner(examiner_id):
    profile = db.session.get(ExaminerProfile, examiner_id)
    if profile is None:
        abort(404)

    profile.approval_status = "rejected"
    profile.approved_by = current_admin_id()
    profile.approved_at = datetime.utcnow()
    profile.user.is_active = False
    db.session.commit()
    flash("Examiner rejected and deactivated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.post("/examiners/<int:examiner_id>/deactivate")
@role_required("admin")
def deactivate_examiner(examiner_id):
    profile = db.session.get(ExaminerProfile, examiner_id)
    if profile is None:
        abort(404)

    profile.user.is_active = False
    db.session.commit()
    flash("Examiner account deactivated.", "success")
    return redirect(url_for("admin.dashboard"))


def current_admin_id():
    from flask_login import current_user

    return current_user.user_id
