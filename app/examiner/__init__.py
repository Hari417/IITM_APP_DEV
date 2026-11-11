from flask import Blueprint


examiner = Blueprint("examiner", __name__, url_prefix="/examiner")

from app.examiner import routes
