from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(70))
    password = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    character = db.relationship('Character', backref = 'user', lazy='dynamic')

    def __init__(self, name, email, password):
        super().__init__()
        self.name = name
        self.email = email
        self.password = password
        self.generate_password(self.password)

    def check_password(self, password_to_check):
        return check_password_hash(self.password, password_to_check)

    def generate_password(self, password_create_salt_from):
        self.password = generate_password_hash(password_create_salt_from)

    def __repr__(self):
        return f'User: {self.email}'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    comics_appeared_in = db.Column(db.Integer)
    image = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, description, comics_appeared_in, image, user_id):
        super().__init__()
        self.name = name
        self.description = description
        self.comics_appeared_in = comics_appeared_in
        self.image = image
        self.user_id = user_id

    def __repr__(self):
        return f'Character: {self.name}'

