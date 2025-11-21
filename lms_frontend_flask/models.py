from .extensions import db
from datetime import datetime

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_ext_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: A Course has many Modules
    # cascade="all, delete-orphan": if a course is deleted, its modules are also deleted.
    modules = db.relationship('Module', backref='course', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Course {self.title}>'

class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    module_ext_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: A Module has many Activities
    activities = db.relationship('Activity', backref='module', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Module {self.title}>'

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    activity_ext_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    ai_activity_key = db.Column(db.String(255), nullable=True) # Key to link to AI Assistant Service activity
    content_type = db.Column(db.String(50), nullable=True) # e.g., 'reading_passage', 'ai_interaction', 'quiz'
    content = db.Column(db.Text, nullable=True) # Could be markdown, JSON config for a quiz, or direct text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Activity {self.title}>'

# Note: The SQL DDL provided in the prompt uses SERIAL for primary keys,
# which is PostgreSQL specific for auto-incrementing integers.
# db.Column(db.Integer, primary_key=True) in SQLAlchemy is the generic way
# and will translate to SERIAL for PostgreSQL.
# TIMESTAMPTZ is handled by db.DateTime(timezone=True) in SQLAlchemy if explicit timezone is needed,
# but default=datetime.utcnow usually stores in UTC by convention.
# For simplicity, using db.DateTime which is often sufficient if the application consistently uses UTC.
# Added index=True for *_ext_id fields as they are likely to be used in lookups.
