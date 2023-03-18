from datetime import datetime

from ..models.course import Course
from ..models.student import Student
from ..utils import db


class StudentCourse(db.Model):
    __tablename__ = 'student_course'

    id = db.Column(db.Integer(), primary_key=True)
    student_id = db.Column(db.Integer(), db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer(), db.ForeignKey('courses.id'))
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_students_in_course_by(cls, course_id):
        students = (
            Student.query.join(StudentCourse)
            .join(Course).filter(Course.id == course_id).all()
        )
        return students

    @classmethod
    def get_student_courses(cls, student_id):
        courses = (
            Course.query.join(StudentCourse)
            .join(Student).filter(Student.id == student_id).all()
        )
        return courses
