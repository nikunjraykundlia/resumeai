from extensions import db
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # OTP verification fields
    otp_secret = db.Column(db.String(32), nullable=True)
    otp_verified = db.Column(db.Boolean, default=False)
    otp_created_at = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, default=0)
    is_locked_out = db.Column(db.Boolean, default=False)
    
    # Relationships
    candidates = db.relationship('Candidate', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_otp(self):
        """Generate a time-based OTP"""
        self.otp_secret = pyotp.random_base32()
        self.otp_created_at = datetime.utcnow()
        self.otp_attempts = 0
        self.is_locked_out = False
        db.session.commit()
        
        # Create TOTP object with 5-minute validity
        totp = pyotp.TOTP(self.otp_secret, interval=300)
        return totp.now()
    
    def verify_otp(self, otp_code):
        """Verify the provided OTP code"""
        # Check for lockout
        if self.is_locked_out:
            return False
            
        # Check for expired OTP (older than 5 minutes)
        if not self.otp_created_at or \
           (datetime.utcnow() - self.otp_created_at) > timedelta(minutes=5):
            return False
            
        # Increment attempts counter
        self.otp_attempts += 1
        
        # Check if maximum attempts reached (3 attempts)
        if self.otp_attempts >= 3:
            self.is_locked_out = True
            db.session.commit()
            return False
            
        # Verify OTP
        totp = pyotp.TOTP(self.otp_secret, interval=300)
        is_valid = totp.verify(otp_code)
        
        if is_valid:
            self.otp_verified = True
            
        db.session.commit()
        return is_valid
    
    def __repr__(self):
        return f'<User {self.username}>'

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with skills
    skills = db.relationship('CandidateSkill', backref='candidate', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Candidate {self.name}>'

class CandidateSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    skill_level = db.Column(db.Integer, default=0)  # 0-100 skill level
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CandidateSkill {self.skill_name}>'

class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobListing {self.title}>'

class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    resume_text = db.Column(db.Text, nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)
    ats_score = db.Column(db.Float, nullable=True)
    improvement_suggestions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    candidate = db.relationship('Candidate', backref=db.backref('analyses', lazy=True))
    
    def __repr__(self):
        return f'<ResumeAnalysis {self.id}>'
