from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models import ExaminerProfile, StudentProfile, User


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if db.session.query(User).filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            full_name=form.full_name.data.strip(),
            email=email,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.flush()

        if user.role == "student":
            if not form.registration_number.data.strip():
                form.registration_number.errors.append(
                    "Registration number is required for students."
                )
                db.session.rollback()
                return render_template("auth/register.html", form=form)
            if not form.programme.data.strip():
                form.programme.errors.append(
                    "Programme is required for students."
                )
                db.session.rollback()
                return render_template("auth/register.html", form=form)
            profile = StudentProfile(
                student_id=user.user_id,
                registration_number=form.registration_number.data.strip(),
                department=form.department.data.strip(),
                programme=form.programme.data.strip(),
                phone=form.phone.data.strip() or None
            )
        else:
            profile = ExaminerProfile(
                examiner_id=user.user_id,
                department=form.department.data.strip(),
                phone=form.phone.data.strip() or None,
                approval_status="pending"
            )

        db.session.add(profile)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        if user.role == "examiner":
            flash(
                "Registration successful. An administrator must approve "
                "your examiner account before examiner operations are available.",
                "success"
            )
        else:
            flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.query(User).filter_by(email=email).first()
        if user is None or not check_password_hash(
            user.password_hash, form.password.data
        ):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_active:
            flash("This account is inactive.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user)
        if user.role == "examiner" and (
            user.examiner_profile is None
            or user.examiner_profile.approval_status != "approved"
        ):
            flash("Your examiner account is awaiting administrator approval.", "warning")
        return redirect(url_for("main.index"))

    return render_template("auth/login.html", form=form)


@auth.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("main.index"))
