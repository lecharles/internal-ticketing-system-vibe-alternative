from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='developer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_tickets = db.relationship('Ticket', backref='assignee', lazy='dynamic',
                                     foreign_keys='Ticket.assignee_id')
    created_tickets = db.relationship('Ticket', backref='creator', lazy='dynamic',
                                    foreign_keys='Ticket.creator_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='project', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='open')
    priority = db.Column(db.String(20), nullable=False, default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic')

    def __repr__(self):
        return f'<Ticket {self.id}: {self.title}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id} on Ticket {self.ticket_id}>' 