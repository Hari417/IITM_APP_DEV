from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.fields import DateField, TimeField
from wtforms.validators import DataRequired, NumberRange


class SlotForm(FlaskForm):
    assignment_id = IntegerField(
        "Assignment",
        validators=[DataRequired()]
    )
    slot_date = DateField(
        "Date",
        validators=[DataRequired()],
        format="%Y-%m-%d"
    )
    start_time = TimeField(
        "Start time",
        validators=[DataRequired()],
        format="%H:%M"
    )
    end_time = TimeField(
        "End time",
        validators=[DataRequired()],
        format="%H:%M"
    )
    capacity = IntegerField(
        "Capacity",
        validators=[DataRequired(), NumberRange(min=1)]
    )
    submit = SubmitField("Create slot")
