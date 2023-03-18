from ..models.user import User
from ..utils import db


class Admin(User):
    __tablename__ = 'admin'

    id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    designation = db.Column(db.String(300))

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
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
