from ..models.user import User
from ..utils import db


class Student(User):
    __tablename__ = 'students'

    id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    matriculation_no = db.Column(db.String(30))
    courses = db.relationship('Course', secondary='student_course')
    score = db.relationship('Score', backref='student_course', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'student'
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
