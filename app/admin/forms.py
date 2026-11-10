from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange


class CourseForm(FlaskForm):
    course_code = StringField(
        "Course code",
        validators=[DataRequired(), Length(max=30)]
    )
    course_name = StringField(
        "Course name",
        validators=[DataRequired(), Length(max=150)]
    )
    description = StringField("Description", validators=[Length(max=500)])
    submit = SubmitField("Save course")


class ExaminationForm(FlaskForm):
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    exam_name = StringField(
        "Examination name",
        validators=[DataRequired(), Length(max=150)]
    )
    exam_type = SelectField(
        "Examination type",
        choices=[
            ("Viva", "Viva"),
            ("Practical", "Practical"),
            ("Project Demo", "Project Demo"),
            ("Assessment", "Assessment"),
        ],
        validators=[DataRequired()]
    )
    duration_minutes = IntegerField(
        "Duration (minutes)",
        validators=[DataRequired(), NumberRange(min=1)]
    )
    maximum_marks = DecimalField(
        "Maximum marks",
        validators=[DataRequired(), NumberRange(min=0.01)]
    )
    slot_creation_start = DateTimeLocalField(
        "Slot creation starts",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    slot_creation_end = DateTimeLocalField(
        "Slot creation ends",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    booking_start = DateTimeLocalField(
        "Booking starts",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    booking_end = DateTimeLocalField(
        "Booking ends",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    status = SelectField(
        "Status",
        choices=[
            ("Draft", "Draft"),
            ("Slot Creation", "Slot Creation"),
            ("Booking Open", "Booking Open"),
            ("Closed", "Closed"),
            ("Completed", "Completed"),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Save examination")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        periods = [
            (self.slot_creation_start, self.slot_creation_end,
             "Slot creation must end after it starts."),
            (self.booking_start, self.booking_end,
             "Booking must end after it starts."),
        ]
        valid = True
        for start, end, message in periods:
            if start.data > end.data:
                end.errors.append(message)
                valid = False
        if self.slot_creation_end.data > self.booking_start.data:
            self.booking_start.errors.append(
                "Booking must start after slot creation ends."
            )
            valid = False
        return valid


class RubricForm(FlaskForm):
    version = IntegerField(
        "Version",
        validators=[DataRequired(), NumberRange(min=1)]
    )
    submit = SubmitField("Create rubric")


class CriterionForm(FlaskForm):
    criterion_name = StringField(
        "Criterion name",
        validators=[DataRequired(), Length(max=150)]
    )
    description = StringField("Description", validators=[Length(max=500)])
    maximum_marks = DecimalField(
        "Maximum marks",
        validators=[DataRequired(), NumberRange(min=0.01)]
    )
    weightage = DecimalField(
        "Weightage (%)",
        validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    submit = SubmitField("Add criterion")
