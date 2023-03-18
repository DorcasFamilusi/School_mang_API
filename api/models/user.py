from datetime import datetime

from ..utils import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    identifier = db.Column(db.String(55), nullable=False, unique=True)
    email = db.Column(db.String(70), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(70), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    password_reset_token = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime)
    user_type = db.Column(db.String(10))

    __mapper_args__ = {
        'polymorphic_on': user_type,
        'polymorphic_identity': 'user'
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

    def __repr__(self) -> str:
        return self.email
