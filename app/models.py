
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Numeric,
    UniqueConstraint,
    text,
)

from flask_login import UserMixin
from app.extensions import db


# ============================================================
# 1. USERS
# ============================================================

class User(db.Model, UserMixin):

    __tablename__ = "users"

    user_id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    examiner_profile = db.relationship(
        "ExaminerProfile",
        foreign_keys="ExaminerProfile.examiner_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    approved_examiners = db.relationship(
        "ExaminerProfile",
        foreign_keys="ExaminerProfile.approved_by",
        back_populates="approver"
    )

    examiner_assignments = db.relationship(
        "ExaminerAssignment",
        foreign_keys="ExaminerAssignment.examiner_id",
        back_populates="examiner"
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'examiner', 'student')",
            name="check_user_role"
        ),
    )

    def get_id(self):
        return str(self.user_id)


# ============================================================
# 2. STUDENT PROFILES
# ============================================================

class StudentProfile(db.Model):

    __tablename__ = "student_profiles"

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        primary_key=True
    )

    registration_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    programme = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    user = db.relationship(
        "User",
        back_populates="student_profile"
    )


# ============================================================
# 3. EXAMINER PROFILES
# ============================================================

class ExaminerProfile(db.Model):

    __tablename__ = "examiner_profiles"

    examiner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        primary_key=True
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    approval_status = db.Column(
        db.String(20),
        default="pending",
        nullable=False
    )

    approved_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=True
    )

    approved_at = db.Column(
        db.DateTime,
        nullable=True
    )

    user = db.relationship(
        "User",
        foreign_keys=[examiner_id],
        back_populates="examiner_profile"
    )

    approver = db.relationship(
        "User",
        foreign_keys=[approved_by],
        back_populates="approved_examiners"
    )

    __table_args__ = (
        CheckConstraint(
            "approval_status IN ('pending', 'approved', 'rejected')",
            name="check_examiner_approval_status"
        ),
    )


# ============================================================
# 5. COURSES
# ============================================================

class Course(db.Model):

    __tablename__ = "courses"

    course_id = db.Column(
        db.Integer,
        primary_key=True
    )

    course_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    course_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    examinations = db.relationship(
        "Examination",
        back_populates="course"
    )


# ============================================================
# 6. EXAMINATIONS
# ============================================================

class Examination(db.Model):

    __tablename__ = "examinations"

    exam_id = db.Column(
        db.Integer,
        primary_key=True
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.course_id"),
        nullable=False
    )

    exam_name = db.Column(
        db.String(150),
        nullable=False
    )

    exam_type = db.Column(
        db.String(30),
        nullable=False
    )

    duration_minutes = db.Column(
        db.Integer,
        nullable=False
    )

    maximum_marks = db.Column(
        Numeric(8, 2),
        nullable=False
    )

    slot_creation_start = db.Column(
        db.DateTime,
        nullable=False
    )

    slot_creation_end = db.Column(
        db.DateTime,
        nullable=False
    )

    booking_start = db.Column(
        db.DateTime,
        nullable=False
    )

    booking_end = db.Column(
        db.DateTime,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Draft",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    course = db.relationship(
        "Course",
        back_populates="examinations"
    )

    assignments = db.relationship(
        "ExaminerAssignment",
        back_populates="exam"
    )

    rubrics = db.relationship(
        "Rubric",
        back_populates="exam",
        cascade="all, delete-orphan"
    )

    slots = db.relationship(
        "ExamSlot",
        back_populates="exam"
    )

    bookings = db.relationship(
        "Booking",
        back_populates="exam"
    )

    __table_args__ = (
        CheckConstraint(
            "exam_type IN "
            "('Viva', 'Practical', 'Project Demo', 'Assessment')",
            name="check_exam_type"
        ),
        CheckConstraint(
            "duration_minutes > 0",
            name="check_exam_duration"
        ),
        CheckConstraint(
            "maximum_marks > 0",
            name="check_exam_maximum_marks"
        ),
        CheckConstraint(
            "slot_creation_start <= slot_creation_end",
            name="check_slot_creation_dates"
        ),
        CheckConstraint(
            "booking_start <= booking_end",
            name="check_booking_dates"
        ),
        CheckConstraint(
            "status IN "
            "('Draft', 'Slot Creation', 'Booking Open', "
            "'Closed', 'Completed')",
            name="check_exam_status"
        ),
    )


# ============================================================
# 7. EXAMINER ASSIGNMENTS
# ============================================================

class ExaminerAssignment(db.Model):

    __tablename__ = "examiner_assignments"

    assignment_id = db.Column(
        db.Integer,
        primary_key=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("examinations.exam_id"),
        nullable=False
    )

    examiner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    assigned_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    assigned_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    exam = db.relationship(
        "Examination",
        back_populates="assignments"
    )

    examiner = db.relationship(
        "User",
        foreign_keys=[examiner_id],
        back_populates="examiner_assignments"
    )

    slots = db.relationship(
        "ExamSlot",
        back_populates="assignment",
        overlaps="exam,slots"
    )

    __table_args__ = (
        UniqueConstraint(
            "exam_id",
            "examiner_id",
            name="unique_examiner_per_exam"
        ),
        UniqueConstraint(
            "assignment_id",
            "exam_id",
            name="unique_assignment_exam_pair"
        ),
    )


# ============================================================
# 8. RUBRICS
# ============================================================

class Rubric(db.Model):

    __tablename__ = "rubrics"

    rubric_id = db.Column(
        db.Integer,
        primary_key=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("examinations.exam_id"),
        nullable=False
    )

    version = db.Column(
        db.Integer,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    exam = db.relationship(
        "Examination",
        back_populates="rubrics"
    )

    criteria = db.relationship(
        "RubricCriterion",
        back_populates="rubric",
        cascade="all, delete-orphan"
    )

    evaluations = db.relationship(
        "Evaluation",
        back_populates="rubric"
    )

    __table_args__ = (
        UniqueConstraint(
            "exam_id",
            "version",
            name="unique_rubric_version"
        ),
        CheckConstraint(
            "version > 0",
            name="check_rubric_version"
        ),
    )


# ============================================================
# 9. RUBRIC CRITERIA
# ============================================================

class RubricCriterion(db.Model):

    __tablename__ = "rubric_criteria"

    criterion_id = db.Column(
        db.Integer,
        primary_key=True
    )

    rubric_id = db.Column(
        db.Integer,
        db.ForeignKey("rubrics.rubric_id"),
        nullable=False
    )

    criterion_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    maximum_marks = db.Column(
        Numeric(8, 2),
        nullable=False
    )

    weightage = db.Column(
        Numeric(5, 2),
        nullable=False
    )

    rubric = db.relationship(
        "Rubric",
        back_populates="criteria"
    )

    evaluation_scores = db.relationship(
        "EvaluationScore",
        back_populates="criterion"
    )

    __table_args__ = (
        CheckConstraint(
            "maximum_marks > 0",
            name="check_criterion_maximum_marks"
        ),
        CheckConstraint(
            "weightage >= 0 AND weightage <= 100",
            name="check_criterion_weightage"
        ),
    )


# ============================================================
# 10. EXAM SLOTS
# ============================================================

class ExamSlot(db.Model):

    __tablename__ = "exam_slots"

    slot_id = db.Column(
        db.Integer,
        primary_key=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("examinations.exam_id"),
        nullable=False
    )

    assignment_id = db.Column(
        db.Integer,
        nullable=False
    )

    slot_date = db.Column(
        db.Date,
        nullable=False
    )

    start_time = db.Column(
        db.Time,
        nullable=False
    )

    end_time = db.Column(
        db.Time,
        nullable=False
    )

    capacity = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Available",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["assignment_id", "exam_id"],
            [
                "examiner_assignments.assignment_id",
                "examiner_assignments.exam_id"
            ],
            name="fk_slot_examiner_assignment"
        ),
        UniqueConstraint(
            "slot_id",
            "exam_id",
            name="unique_slot_exam_pair"
        ),
        CheckConstraint(
            "capacity > 0",
            name="check_slot_capacity"
        ),
        CheckConstraint(
            "start_time < end_time",
            name="check_slot_time"
        ),
        CheckConstraint(
            "status IN "
            "('Available', 'Full', 'Cancelled', 'Completed')",
            name="check_slot_status"
        ),
    )

    exam = db.relationship(
        "Examination",
        back_populates="slots",
        overlaps="slots"
    )

    assignment = db.relationship(
        "ExaminerAssignment",
        back_populates="slots",
        overlaps="exam,slots"
    )

    bookings = db.relationship(
        "Booking",
        back_populates="slot",
        overlaps="bookings,exam"
    )

    old_booking_events = db.relationship(
        "BookingEvent",
        foreign_keys="BookingEvent.old_slot_id",
        back_populates="old_slot"
    )

    new_booking_events = db.relationship(
        "BookingEvent",
        foreign_keys="BookingEvent.new_slot_id",
        back_populates="new_slot"
    )


# ============================================================
# 11. BOOKINGS
# ============================================================

class Booking(db.Model):

    __tablename__ = "bookings"

    booking_id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("examinations.exam_id"),
        nullable=False
    )

    slot_id = db.Column(
        db.Integer,
        nullable=False
    )

    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Booked",
        nullable=False
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["slot_id", "exam_id"],
            ["exam_slots.slot_id", "exam_slots.exam_id"],
            name="fk_booking_slot_exam"
        ),
        CheckConstraint(
            "status IN ('Booked', 'Cancelled', 'Completed')",
            name="check_booking_status"
        ),
        # A student cannot have two active/completed bookings
        # for the same examination.
        Index(
            "unique_active_student_exam_booking",
            "student_id",
            "exam_id",
            unique=True,
            sqlite_where=text(
                "status IN ('Booked', 'Completed')"
            )
        ),
    )

    student = db.relationship("User")

    exam = db.relationship(
        "Examination",
        back_populates="bookings",
        overlaps="bookings,slot"
    )

    slot = db.relationship(
        "ExamSlot",
        back_populates="bookings",
        overlaps="bookings,exam"
    )

    evaluation = db.relationship(
        "Evaluation",
        back_populates="booking",
        uselist=False
    )

    events = db.relationship(
        "BookingEvent",
        back_populates="booking"
    )


# ============================================================
# 12. EVALUATIONS
# ============================================================

class Evaluation(db.Model):

    __tablename__ = "evaluations"

    evaluation_id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.booking_id"),
        unique=True,
        nullable=False
    )

    rubric_id = db.Column(
        db.Integer,
        db.ForeignKey("rubrics.rubric_id"),
        nullable=False
    )

    examiner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    total_marks = db.Column(
        Numeric(8, 2),
        nullable=True
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Draft",
        nullable=False
    )

    evaluated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    published_at = db.Column(
        db.DateTime,
        nullable=True
    )

    booking = db.relationship(
        "Booking",
        back_populates="evaluation"
    )

    rubric = db.relationship(
        "Rubric",
        back_populates="evaluations"
    )

    examiner = db.relationship("User")

    scores = db.relationship(
        "EvaluationScore",
        back_populates="evaluation"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Draft', 'Submitted', 'Published')",
            name="check_evaluation_status"
        ),
        CheckConstraint(
            "total_marks IS NULL OR total_marks >= 0",
            name="check_evaluation_total_marks"
        ),
    )


# ============================================================
# 13. EVALUATION SCORES
# ============================================================

class EvaluationScore(db.Model):

    __tablename__ = "evaluation_scores"

    score_id = db.Column(
        db.Integer,
        primary_key=True
    )

    evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("evaluations.evaluation_id"),
        nullable=False
    )

    criterion_id = db.Column(
        db.Integer,
        db.ForeignKey("rubric_criteria.criterion_id"),
        nullable=False
    )

    marks_awarded = db.Column(
        Numeric(8, 2),
        nullable=False
    )

    evaluation = db.relationship(
        "Evaluation",
        back_populates="scores"
    )

    criterion = db.relationship(
        "RubricCriterion",
        back_populates="evaluation_scores"
    )

    __table_args__ = (
        UniqueConstraint(
            "evaluation_id",
            "criterion_id",
            name="unique_evaluation_criterion"
        ),
        CheckConstraint(
            "marks_awarded >= 0",
            name="check_marks_awarded"
        ),
    )


# ============================================================
# 14. BOOKING EVENTS
# ============================================================

class BookingEvent(db.Model):

    __tablename__ = "booking_events"

    event_id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.booking_id"),
        nullable=False
    )

    action = db.Column(
        db.String(30),
        nullable=False
    )

    old_slot_id = db.Column(
        db.Integer,
        db.ForeignKey("exam_slots.slot_id"),
        nullable=True
    )

    new_slot_id = db.Column(
        db.Integer,
        db.ForeignKey("exam_slots.slot_id"),
        nullable=True
    )

    performed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    booking = db.relationship(
        "Booking",
        back_populates="events"
    )

    old_slot = db.relationship(
        "ExamSlot",
        foreign_keys=[old_slot_id],
        back_populates="old_booking_events"
    )

    new_slot = db.relationship(
        "ExamSlot",
        foreign_keys=[new_slot_id],
        back_populates="new_booking_events"
    )

    performer = db.relationship("User")

    __table_args__ = (
        CheckConstraint(
            "action IN ('Booked', 'Cancelled', 'Rescheduled')",
            name="check_booking_event_action"
        ),
    )
