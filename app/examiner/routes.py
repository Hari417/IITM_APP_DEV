from datetime import datetime

from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from app.decorators import approved_examiner_required
from app.examiner import examiner
from app.examiner.forms import SlotForm
from app.extensions import db
from app.models import ExamSlot, ExaminerAssignment


@examiner.get("/")
@approved_examiner_required
def dashboard():
    assignments = (
        db.session.query(ExaminerAssignment)
        .filter_by(examiner_id=current_user.user_id, is_active=True)
        .order_by(ExaminerAssignment.assigned_at.desc())
        .all()
    )
    return render_template(
        "examiner/dashboard.html",
        assignments=assignments
    )


@examiner.route("/assignments/<int:assignment_id>/slots", methods=["GET", "POST"])
@approved_examiner_required
def slots(assignment_id):
    assignment = db.session.get(ExaminerAssignment, assignment_id)
    if assignment is None or (
        assignment.examiner_id != current_user.user_id
        or not assignment.is_active
    ):
        return "Assignment not found.", 404

    form = SlotForm()
    form.assignment_id.data = assignment.assignment_id
    if form.validate_on_submit():
        exam = assignment.exam
        now = datetime.utcnow()
        slot_start = datetime.combine(
            form.slot_date.data,
            form.start_time.data
        )
        slot_end = datetime.combine(
            form.slot_date.data,
            form.end_time.data
        )

        if not (
            exam.slot_creation_start <= now <= exam.slot_creation_end
        ):
            form.slot_date.errors.append(
                "Slots can only be created during the configured period."
            )
        elif slot_start >= slot_end:
            form.end_time.errors.append(
                "End time must be after start time."
            )
        elif slot_start < exam.booking_start or slot_end > exam.booking_end:
            form.slot_date.errors.append(
                "Slot time must be within the examination booking period."
            )
        else:
            conflict = (
                db.session.query(ExamSlot)
                .join(ExamSlot.assignment)
                .filter(
                    ExaminerAssignment.examiner_id == current_user.user_id,
                    ExamSlot.slot_date == form.slot_date.data,
                    ExamSlot.start_time < form.end_time.data,
                    ExamSlot.end_time > form.start_time.data,
                    ExamSlot.status != "Cancelled"
                )
                .first()
            )
            if conflict:
                form.start_time.errors.append(
                    "This time overlaps another slot."
                )
            else:
                db.session.add(ExamSlot(
                    exam_id=assignment.exam_id,
                    assignment_id=assignment.assignment_id,
                    slot_date=form.slot_date.data,
                    start_time=form.start_time.data,
                    end_time=form.end_time.data,
                    capacity=form.capacity.data,
                    status="Available"
                ))
                db.session.commit()
                flash("Examination slot created successfully.", "success")
                return redirect(url_for(
                    "examiner.slots",
                    assignment_id=assignment.assignment_id
                ))

    existing_slots = (
        db.session.query(ExamSlot)
        .filter_by(assignment_id=assignment.assignment_id)
        .order_by(ExamSlot.slot_date, ExamSlot.start_time)
        .all()
    )
    return render_template(
        "examiner/slots.html",
        form=form,
        assignment=assignment,
        slots=existing_slots
    )
