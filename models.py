from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# User roles
class Role:
    ADMIN = 'admin'
    CUSTOMER = 'customer'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default=Role.CUSTOMER)  # Default to customer role
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('ClothingItem', backref='owner', lazy='dynamic')
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == Role.ADMIN
    
    def is_customer(self):
        return self.role == Role.CUSTOMER
    
    def __repr__(self):
        return f'<User {self.username}>'

class ClothingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255), nullable=False)
    sustainability_score = db.Column(db.Float, default=0.0)
    sustainability_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    votes = db.relationship('Vote', backref='item', lazy='dynamic')
    
    def get_vote_score(self):
        votes = self.votes.all()
        if not votes:
            return 0
        return sum(vote.value for vote in votes) / len(votes)
    
    def __repr__(self):
        return f'<ClothingItem {self.name}>'

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # 1-5 rating
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('clothing_item.id'))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_id', name='unique_user_item_vote'),
    )
    
    def __repr__(self):
        return f'<Vote {self.value} by User {self.user_id} for Item {self.item_id}>'

class SustainabilityFactor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    weight = db.Column(db.Float, default=1.0)  # Weight in sustainability calculation
    
    def __repr__(self):
        return f'<SustainabilityFactor {self.name}>' 