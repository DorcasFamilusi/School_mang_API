# from ..utils import db
# from datetime import datetime


# class Grade(db.Model):
#     __tablename__ = 'grades'

#     id = db.Column(db.Integer(), primary_key=True)
#     course_id = db.Column(db.Integer(), db.ForeignKey('courses.id'), nullable =False)
#     student_id = db.Column(db.Integer(), db.ForeignKey('students.id'), nullable=False)
#     score = db.Column(db.Float, nullable= False)
#     grade = db.Column(db.String(5) , nullable=True )
#     created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

#     def delete(self):
#         db.session.delete(self)
#         db.session.commit()

#     @classmethod
#     def get_by_id(cls, id):
#         return cls.query.get_or_404(id)
