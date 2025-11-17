from src.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """用户模型 - 支持教师、学生、管理员"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # teacher, student, admin
    student_id = db.Column(db.String(50), unique=True, nullable=True)  # PolyU学生ID
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 关系
    courses_taught = db.relationship('Course', backref='teacher', lazy=True, foreign_keys='Course.teacher_id')
    courses_enrolled = db.relationship('Course', secondary='course_enrollments', backref='students')
    activities_created = db.relationship('Activity', backref='creator', lazy=True)
    responses = db.relationship('ActivityResponse', backref='student', lazy=True)
    forum_posts = db.relationship('ForumPost', backref='user', lazy=True)
    forum_replies = db.relationship('ForumReply', backref='user', lazy=True)
    forum_reads = db.relationship('UserForumRead', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'student_id': self.student_id,
            'full_name': self.full_name,
            'department': self.department,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }