
# EMP - Project Status

## Project
Examination Management Portal

## Current User ID Decision
- User IDs use a normal auto-incrementing integer primary key: `1`, `2`, `3`, etc.
- User-related foreign keys also use integer types.

## Technology Stack
- Python
- Flask
- HTML and CSS
- Bootstrap 5
- Jinja2
- SQLite
- Flask-SQLAlchemy

## Current Phase
Phase 4 - Examiner Module

## Completed
- [x] Architecture approved
- [x] Database schema designed
- [x] Project structure planned
- [x] Authentication and registration foundation
- [x] Student and examiner registration
- [x] Password hashing, login, logout, and CSRF protection
- [x] Pre-created admin account
- [x] Admin dashboard and examiner approval/deactivation
- [x] Admin course and examination creation
- [x] Admin rubric and criterion creation
- [x] Admin examiner assignment
- [x] Examiner dashboard and slot creation

## Completed Setup
- [x] Python environment setup
- [x] Flask application setup
- [x] SQLite configuration

## Pending
- [x] Database models
- [x] Programmatic database initialization
- [x] Admin account creation
- [ ] Authentication role-specific dashboards
- [ ] Admin course and examination editing
- [ ] Admin rubric editing
- [ ] Examiner slot editing and deletion
- [ ] Student module
- [ ] Integration and testing
- [ ] Documentation and submission

## Known Issues
- A proper permanent pytest test suite has not been created yet.
- Invalid foreign-key rejection still needs a dedicated runtime test.
- The previous custom-ID database is preserved as
  `instance/emp.db.custom-id-backup`; the active database uses integer IDs.

## Next Task
Implement examiner booking list and evaluation.
