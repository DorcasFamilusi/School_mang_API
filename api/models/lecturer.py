from .user import User
from ..utils import db


class Lecturer(User):
    __tablename__ = 'lecturer'

    id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    employee_no = db.Column(db.String(18))
    courses = db.relationship('Course', backref='lecturer_course')

    __mapper_args__ = {
        'polymorphic_identity': 'lecturer'
    }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
