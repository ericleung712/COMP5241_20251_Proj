from src.database import db
from datetime import datetime

class Course(db.Model):
    """课程模型"""
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)  # 课程代码
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    semester = db.Column(db.String(20), nullable=False)  # 学期
    academic_year = db.Column(db.String(10), nullable=False)  # 学年
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    activities = db.relationship('Activity', backref='course', lazy=True, cascade='all, delete-orphan')
    forum_posts = db.relationship('ForumPost', backref='course', lazy=True, cascade='all, delete-orphan')
    forum_reads = db.relationship('UserForumRead', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.course_code}: {self.course_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.full_name if self.teacher else None,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'is_active': self.is_active,
            'student_count': len(self.students),
            'activity_count': len(self.activities),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 课程注册关联表
course_enrollments = db.Table('course_enrollments',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)
