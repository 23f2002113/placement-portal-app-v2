from datetime import datetime, timezone
from extensions import db
from flask_security import UserMixin, RoleMixin


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class User(BaseModel, UserMixin):
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    
    # Flask-Security 
    fs_uniquifier = db.Column(db.String(250), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True)
    
    # Relationships
    roles = db.relationship('Role', backref = 'bearers', secondary='user_roles')
    student_profile = db.relationship('StudentProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship('CompanyProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")


class Role(BaseModel, RoleMixin):
    name = db.Column(db.String(80), unique=True, nullable=False) 
    description = db.Column(db.String(250))

class UserRoles(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class StudentProfile(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    cgpa = db.Column(db.Numeric(4,2), nullable=False)
    education = db.Column(db.String(100))
    department = db.Column(db.String(100))
    skills = db.Column(db.Text) 
    resume_path = db.Column(db.String(255))
    is_blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='student_profile')
    applications = db.relationship('Application', back_populates='student_profile')
    placements = db.relationship('Placement', back_populates='student')

class CompanyProfile(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(100))
    location = db.Column(db.String(100))
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')

    user = db.relationship('User', back_populates='company_profile')
    drives = db.relationship('PlacementDrive', back_populates='company_profile')
    placements = db.relationship('Placement', back_populates='company')

class PlacementDrive(BaseModel):
    company_id = db.Column(db.Integer, db.ForeignKey('company_profile.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text)
    package_details = db.Column(db.String(50)) 
    min_cgpa_criteria = db.Column(db.Numeric(4,2), default=0.0)
    deadline = db.Column(db.DateTime(timezone=True))
    drive_status = db.Column(db.Enum('pending', 'approved', 'closed'), default='pending')

    company_profile = db.relationship('CompanyProfile', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive')

class Application(BaseModel):
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    status = db.Column(db.Enum('applied', 'shortlisted', 'interview','offer', 'rejected','placed'), default='applied')

    student_profile = db.relationship('StudentProfile', back_populates='applications')
    drive = db.relationship('PlacementDrive', back_populates='applications')
    placement = db.relationship('Placement', back_populates='application', uselist=False)


class Placement(BaseModel):
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profile.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), unique=True, nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    offer_letter_path = db.Column(db.String(255))
    joining_date = db.Column(db.DateTime(timezone=True))
    student = db.relationship('StudentProfile', back_populates='placements')
    company = db.relationship('CompanyProfile', back_populates='placements')
    application = db.relationship('Application', back_populates='placement')


