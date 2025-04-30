from datetime import datetime, timedelta
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import re
from app import db, login_manager
import secrets
import jwt
from flask import current_app

# Initialize Argon2 hasher with recommended parameters
ph = PasswordHasher(
    time_cost=3,  # Number of iterations
    memory_cost=65536,  # 64MB in KiB
    parallelism=4,  # Number of parallel threads
    hash_len=32,  # Length of the hash in bytes
    salt_len=16  # Length of the salt in bytes
)

class ActivityLog(db.Model):
    """Model for storing user activity logs."""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    resource_type = db.Column(db.String(50), nullable=True)  # e.g., 'ticket', 'project'
    resource_id = db.Column(db.Integer, nullable=True)
    additional_data = db.Column(db.JSON, nullable=True)

    # Relationship to user
    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic'))

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicitly set the table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length for Argon2 hash
    role = db.Column(db.String(20), nullable=False, default='developer', server_default='developer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    account_locked_until = db.Column(db.DateTime)
    
    # Relationships
    assigned_tickets = db.relationship('Ticket', backref='assignee', lazy='dynamic',
                                     foreign_keys='Ticket.assignee_id')
    created_tickets = db.relationship('Ticket', backref='creator', lazy='dynamic',
                                    foreign_keys='Ticket.creator_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    teams = db.relationship('Team', secondary='team_members', lazy='dynamic',
                           backref=db.backref('members', lazy='dynamic'))

    def __init__(self, username, email, password=None, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        if password:
            self.set_password(password)

    @staticmethod
    def is_password_complex(password):
        """
        Validate password complexity requirements:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one number
        - Contains at least one special character
        """
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    def set_password(self, password):
        """Set password with Argon2 hashing."""
        if not self.is_password_complex(password):
            raise ValueError("Password does not meet complexity requirements")
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        """Verify password using Argon2."""
        if self.is_account_locked():
            return False
        try:
            is_valid = ph.verify(self.password_hash, password)
            if is_valid:
                self.reset_failed_login_attempts()
            return is_valid
        except VerifyMismatchError:
            self.increment_failed_login_attempts()
            return False

    def is_account_locked(self):
        """Check if account is temporarily locked due to failed login attempts."""
        if self.account_locked_until and datetime.utcnow() < self.account_locked_until:
            return True
        return False

    def increment_failed_login_attempts(self):
        """Increment failed login attempts and lock account if threshold reached."""
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        self.last_failed_login = datetime.utcnow()
        
        # Lock account for increasing periods based on number of failures
        if self.failed_login_attempts >= 5:
            lock_minutes = min(2 ** (self.failed_login_attempts - 5), 60)  # Max 1 hour
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
        
        db.session.commit()

    def reset_failed_login_attempts(self):
        """Reset failed login attempts after successful login."""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_locked_until = None
        db.session.commit()

    def generate_reset_token(self):
        """Generate a secure token for password reset."""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if the reset token is valid and not expired."""
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return True

    def clear_reset_token(self):
        """Clear the reset token after it's been used."""
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def get_teams(self):
        """Get all teams that the user is a member of."""
        return self.teams.all()

    def get_team_role(self, team):
        """Get the user's role in a specific team."""
        if team not in self.teams:
            return None
        return team.get_member_role(self)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='SET NULL'))
    tickets = db.relationship('Ticket', backref='project', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='open')
    priority = db.Column(db.String(20), nullable=False, default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic')

    def __repr__(self):
        return f'<Ticket {self.id}: {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id} on Ticket {self.ticket_id}>'

# Team membership association table
team_members = db.Table('team_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role', db.String(20), nullable=False, server_default='developer')
)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    leader = db.relationship('User', foreign_keys=[leader_id], backref='led_teams')
    projects = db.relationship('Project', backref='team', lazy='dynamic')
    
    def __init__(self, name, description=None, leader=None):
        if not name or len(name) > 64:
            raise ValueError('Team name must be between 1 and 64 characters')
        if description and len(description) > 256:
            raise ValueError('Team description must not exceed 256 characters')
            
        self.name = name
        self.description = description
        if leader:
            self.leader = leader
            # Add leader as a member with team_lead role
            self.members.append(leader)
            db.session.flush()  # Ensure team.id is available
            stmt = team_members.insert().values(
                user_id=leader.id,
                team_id=self.id,
                role='team_lead'
            )
            db.session.execute(stmt)
            db.session.flush()  # Ensure the role is set
    
    def add_member(self, user, role='developer'):
        """Add a member to the team with an optional role."""
        if role not in ['developer', 'team_lead', 'project_manager']:
            raise ValueError('Invalid role specified')
            
        if user not in self.members:
            self.members.append(user)
            db.session.flush()  # Ensure team.id is available
            stmt = team_members.insert().values(
                user_id=user.id,
                team_id=self.id,
                role=role
            )
            db.session.execute(stmt)
            db.session.flush()  # Ensure the role is set
            
    def remove_member(self, user):
        if user in self.members:
            if user == self.leader:
                raise ValueError('Cannot remove team leader')
            self.members.remove(user)
            
    def has_member(self, user):
        return user in self.members
        
    def __repr__(self):
        return f'<Team {self.name}>'

    def get_member_role(self, user):
        """Get the role of a team member."""
        if user not in self.members:
            return None
        
        result = db.session.execute(
            db.select([team_members.c.role]).where(
                db.and_(
                    team_members.c.team_id == self.id,
                    team_members.c.user_id == user.id
                )
            )
        ).scalar()
        db.session.flush()  # Ensure the query is executed
        return result or 'developer'  # Default to developer if no role set

    def update_member_role(self, user, new_role):
        """Update the role of a team member."""
        if new_role not in ['developer', 'team_lead', 'project_manager']:
            raise ValueError('Invalid role specified')
        
        if user not in self.members:
            raise ValueError('User is not a member of this team')
        
        stmt = team_members.update().where(
            db.and_(
                team_members.c.team_id == self.id,
                team_members.c.user_id == user.id
            )
        ).values(role=new_role)
        db.session.execute(stmt)
        db.session.flush()  # Ensure the update is executed

    def add_project(self, project):
        """Add a project to the team."""
        if project not in self.projects:
            self.projects.append(project)

    def remove_project(self, project):
        """Remove a project from the team."""
        if project in self.projects:
            self.projects.remove(project)

# Update User model to include team-related methods
def get_teams(self):
    """Get all teams that the user is a member of."""
    return self.teams.all()

def get_team_role(self, team):
    """Get the user's role in a specific team."""
    if team not in self.teams:
        return None
    return team.get_member_role(self)

# Add methods to User class
User.get_teams = get_teams
User.get_team_role = get_team_role 