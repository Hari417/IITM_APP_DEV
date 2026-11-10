# PROJECT HANDOFF — EXAMINATION MANAGEMENT PORTAL (EMP)

> Current decision: user IDs use a normal auto-incrementing integer primary key
> (`1`, `2`, `3`, etc.). The earlier `YY_NNNN` custom-ID design is retired.

## 1. Project Overview

I am developing an **Examination Management Portal (EMP)** as part of my IITM Application Development coursework.

The next AI agent must act as my:
- Senior Python/Flask Developer
- Software Architect
- Database Designer
- Technical Mentor
- Testing and Debugging Assistant
- Viva Preparation Mentor

The objective is to build a complete, functional application that satisfies the uploaded coursework guidelines.

**Important:** The coursework guideline document is the single source of truth. Do not invent requirements or replace mandatory requirements with optional features.

## 2. Mandatory Technology Stack

| Component | Technology |
|---|---|
| Backend | Python + Flask |
| Frontend | HTML, CSS, Bootstrap 5, Jinja2 |
| Database | SQLite ONLY |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Forms and CSRF | Flask-WTF |
| Password security | Werkzeug |
| Testing | pytest |
| Development environment | VS Code |
| Execution | Local machine |

Strict restrictions:
- No React, Vue, Angular, or alternative CSS frameworks.
- No PostgreSQL or MySQL.
- JavaScript must not implement core application requirements.
- Database must be initialized programmatically.
- Application must run locally.

## 3. Coursework Requirements

### Admin
- Pre-created administrator account.
- No public Admin registration.
- Create, update, and manage courses and examinations.
- Create and manage examination rubrics.
- Approve or deactivate examiners.
- Configure examination timelines.
- Open and close slot creation and booking periods.
- View all examination slots and bookings.
- Reschedule student bookings.
- Change examiner assignments.
- Search and view users, examinations, and bookings.
- Dashboard statistics and historical records.

### Examiner
- Self-registration and login.
- Account approval by Admin.
- View assigned examinations.
- Create examination slots within permitted periods.
- Update or delete slots before bookings begin, subject to applicable rules.
- View students booked into assigned slots.
- Evaluate students using examination rubrics.
- Enter marks and remarks.
- Submit evaluations.
- Examiner must only evaluate students assigned to their own examination slots.

### Student
- Self-registration and login.
- Discover, search, and filter examinations.
- View available examination slots.
- Book examination slots.
- Cancel bookings before the applicable deadline.
- View booking and examination history.
- View upcoming examination schedule.
- View published results and feedback.
- Edit profile information.
- Student dashboard.

### Mandatory business rules
- Slot creation must respect the configured creation period.
- Booking must respect the configured booking period.
- Slot capacity must never be exceeded.
- Slot status must reflect whether it is available or full.
- Students cannot create duplicate bookings for the same examination.
- Cancellation must respect the deadline.
- Unapproved examiners cannot perform examiner operations.
- Examiners can evaluate only their own booked students.
- Historical bookings and events must be retained.
- Admin must be able to reschedule bookings and change examiner assignments.
- Role-based authorization and server-side validation are mandatory.

Optional features such as APIs, charts, email notifications, and scorecards should not take priority over mandatory requirements.

## 4. Approved Architecture

The user approved a simple Flask application architecture.

Decisions:
- Flask application factory.
- Flask-SQLAlchemy.
- Flask-Login.
- Flask-WTF.
- One initial `models.py` file.
- Simple role-based Flask blueprints.
- Bootstrap 5 and Jinja2 templates.
- SQLite database initialized programmatically.
- No unnecessary service or repository abstractions.
- Implement one module at a time.

### Approved folder structure

```text
EMP/
├── run.py
├── config.py
├── requirements.txt
├── PROJECT_STATUS.md
├── TECHNICAL_DECISIONS.md
├── README.md
├── instance/
│   └── emp.db
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── decorators.py
│   ├── routes.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── examiner/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── student/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── examiner/
│   │   ├── student/
│   │   └── errors/
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── images/
└── tests/
    ├── test_auth.py
    ├── test_booking.py
    └── test_roles.py
```

Add files only when required.

## 5. Approved Database Design

The approved application schema contains 13 core tables.

| No. | Table | Purpose |
|---:|---|---|
| 1 | users | Common user authentication and roles |
| 2 | student_profiles | Student-specific information |
| 3 | examiner_profiles | Examiner-specific information and approval |
| 4 | courses | Course information |
| 5 | examinations | Examination details and timelines |
| 6 | examiner_assignments | Examiner-to-examination assignments |
| 7 | rubrics | Examination evaluation rubrics |
| 8 | rubric_criteria | Individual rubric criteria |
| 9 | exam_slots | Slots created for examinations |
| 10 | bookings | Student examination bookings |
| 11 | evaluations | Examination evaluation records |
| 12 | evaluation_scores | Marks awarded per criterion |
| 13 | booking_events | Booking, cancellation, and rescheduling history |

An additional `user_id_sequence` table was introduced to generate the custom user IDs.

### Important User ID requirement

The user explicitly requires the **actual primary key** to use this format:

`YY_NNNN`

Examples:

```text
26_0001
26_0002
26_0003
27_0004
27_0005
28_0006
```

Rules:
- First two digits represent the registration year.
- The number after the underscore is a global sequence.
- The sequence MUST NOT reset when the year changes.
- The ID must be generated automatically.
- The ID must be the actual primary key, not merely a display field.
- All foreign keys referencing `users.user_id` must use a string type.
- The Admin account must also be considered when implementing ID generation. Its exact ID allocation has not yet been finalized.

The implementation currently uses:
- `users.user_id`: `String(20)` primary key.
- `user_id_sequence.last_number`: persistent global counter.
- `generate_user_id()`: creates IDs using the current two-digit year and the next global sequence number.

Example:

```python
user_id = generate_user_id()
```

The counter must persist across application restarts.

Generate the ID, create the user, and create the corresponding profile in the same database transaction. Roll back the transaction if registration fails.

### Important foreign key changes

The following fields must use `String(20)`:

- `student_profiles.student_id`
- `examiner_profiles.examiner_id`
- `examiner_profiles.approved_by`
- `examiner_assignments.examiner_id`
- `examiner_assignments.assigned_by`
- `bookings.student_id`
- `evaluations.examiner_id`
- `booking_events.performed_by`

Do not accidentally leave any foreign key to `users.user_id` as an integer.

### Other approved schema decisions

- Student and examiner profiles remain separate tables.
- Booking capacity is calculated from active bookings rather than maintaining a separate available-seat counter.
- A student cannot have multiple active/completed bookings for the same examination.
- A booking must reference a slot belonging to the same examination.
- Booking events preserve historical actions.
- Evaluation scores must be linked to rubric criteria.
- Database foreign key enforcement must be enabled in SQLite.

## 6. Current Implementation Status

The user is working in VS Code on a fresh project.

### Completed or previously working

- Flask project environment setup.
- Initial Flask application.
- Flask application factory.
- Basic home page.
- `/health` route.
- Flask-SQLAlchemy initialization.
- Flask-Login initialization.
- CSRF protection initialization.
- Flask-Login user loader issue was previously fixed.

### Current files previously provided

`config.py`:

```python
import os

class Config:
    SECRET_KEY = os.environ.get(
        "EMP_SECRET_KEY",
        "dev-only-change-this-key"
    )
    SQLALCHEMY_DATABASE_URI = "sqlite:///emp.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

`app/extensions.py` includes SQLAlchemy, Flask-Login, CSRF protection, and a SQLite foreign-key pragma listener.

The user loader must use the new string primary key:

```python
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, user_id)
```

`run.py`:

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

`requirements.txt`:

```text
Flask>=3.0,<4.0
Flask-SQLAlchemy>=3.1,<4.0
Flask-Login>=0.6,<1.0
Flask-WTF>=1.2,<2.0
pytest>=8.0,<10.0
```

### Latest code provided

A complete `app/models.py` was provided in the previous conversation.

It defines:
- `UserIdSequence`
- `User`
- `StudentProfile`
- `ExaminerProfile`
- `Course`
- `Examination`
- `ExaminerAssignment`
- `Rubric`
- `RubricCriterion`
- `ExamSlot`
- `Booking`
- `Evaluation`
- `EvaluationScore`
- `BookingEvent`

This is 14 tables total: 13 core tables plus the ID sequence table.

**Critical status:** The complete model file has been provided, but the user has NOT confirmed that it runs successfully. Do not claim it has been tested.

## 7. Important Checks Before Continuing

The next agent must inspect the actual current project files before making changes.

Do not assume the user copied every previous code block correctly.

In particular, inspect:

1. `app/models.py`
2. `app/extensions.py`
3. `app/__init__.py`
4. `config.py`
5. `run.py`
6. `instance/emp.db`, if it exists.

### Potential issues to verify in the latest model code

- All SQLAlchemy relationships resolve without mapper errors.
- All foreign keys referencing `users.user_id` use string columns.
- Composite foreign keys for slot/examination and assignment/examination are valid.
- SQLite partial unique index for active/completed bookings is created correctly.
- `generate_user_id()` works inside a transaction and does not skip numbers on rollback.
- The sequence row is initialized exactly once.
- SQLite foreign key enforcement is enabled.
- `ExamSlot` and `Booking` relationships work.
- The examiner assignment relationships work.
- All 14 tables are actually created.

Do not make unnecessary changes to the approved design merely to avoid fixing a small implementation issue.

### Database migration warning

The previous database was created using an integer user primary key.

`db.create_all()` does not migrate existing tables.

If the old database contains only disposable test data:
- Stop Flask.
- Back up the database.
- Delete `instance/emp.db`.
- Restart the application to create the new schema.

If it contains important data, do not delete it. Plan a proper migration.

## 8. Unresolved Business Decisions

Do not silently invent answers for these:

1. Whether the Admin receives an ID from the same global sequence or a special fixed ID.
2. Whether a student can hold simultaneous bookings for different examinations.
3. Whether examiners can edit or resubmit submitted evaluations.
4. Whether rubric weightage is a percentage or another calculation method.
5. Who has authority to publish results.
6. What happens to existing bookings when a slot is cancelled or an examiner is reassigned.
7. Whether courses and examinations should be soft-deleted or archived.

Ask only when a decision is necessary for the next implementation step.

## 9. Required Development Roadmap

Follow this order strictly:

1. Requirements verification.
2. Architecture confirmation.
3. Database schema and relationship verification.
4. Authentication and registration.
5. Admin module.
6. Examiner module.
7. Student module.
8. Integration.
9. Testing.
10. Documentation.
11. Submission preparation.

Do not skip dependencies.

### Immediate next task

The immediate task is:

**Verify and test the complete database model implementation.**

Recommended tests:
- Start the Flask application.
- Confirm all 14 tables exist.
- Confirm `users.user_id` is a string primary key.
- Generate several IDs.
- Confirm the sequence continues when the year prefix changes (use a controlled test rather than waiting for a new year).
- Confirm the counter persists after restarting Flask.
- Create a student and student profile.
- Create an examiner and examiner profile.
- Verify foreign key relationships.
- Verify that invalid foreign key references are rejected.

Only after the database models are verified should authentication implementation begin.

## 10. Project Documentation

Maintain two files throughout development:

### PROJECT_STATUS.md
Record:
- Completed features.
- Tested features.
- Untested features.
- Pending features.
- Known bugs.
- Current development stage.

### TECHNICAL_DECISIONS.md
Record:
- Database design decisions.
- User ID generation logic.
- Authentication decisions.
- Booking constraints.
- Evaluation and rubric decisions.
- Any justified deviations from the initial architecture.

Update these files after significant milestones.

## 11. How to Work With Me

I am a student learning Flask and application development.

Please:
- Explain implementation decisions clearly.
- Prefer simple, readable code.
- Work incrementally, one module at a time.
- Provide complete executable files when modifying files.
- Include file paths and run instructions.
- Explain how to test each feature.
- Clearly distinguish implemented, tested, and untested functionality.
- Explain important concepts so I can defend the design during my viva.
- Inspect existing code before modifying it.
- Preserve working functionality.
- Avoid unnecessary dependencies and abstractions.
- Do not generate the entire application at once.
- Do not start coding a dependent module before its prerequisites are verified.

**Most important:** Mandatory coursework requirements must be retained, even when choosing simpler implementations.

## 12. First Response Expected From the Next Agent

Start by acknowledging this handoff.

Then ask me to provide or inspect my current project files, especially the latest `app/models.py`, `app/extensions.py`, and `app/__init__.py`.

Continue with database verification. Do not jump straight into authentication or generate another complete application.