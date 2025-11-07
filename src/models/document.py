from src.database import db
from datetime import datetime

class Document(db.Model):
    """课程文档模型"""
    __tablename__ = 'document'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    stored_filename = db.Column(db.String(255), nullable=False)  # 存储的文件名
    file_path = db.Column(db.String(500), nullable=False)  # 文件存储路径
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小（字节）
    file_type = db.Column(db.String(50), nullable=False)  # 文件类型（pdf, docx, etc.）
    title = db.Column(db.String(200), nullable=True)  # 文档标题
    description = db.Column(db.Text, nullable=True)  # 文档描述
    is_active = db.Column(db.Boolean, default=True)  # 是否可用（下架功能）
    download_count = db.Column(db.Integer, default=0)  # 下载次数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    course = db.relationship('Course', backref='documents', lazy=True)
    uploader = db.relationship('User', backref='uploaded_documents', lazy=True)
    
    def __repr__(self):
        return f'<Document {self.filename} for Course {self.course_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else None,
            'uploader_id': self.uploader_id,
            'uploader_name': self.uploader.full_name if self.uploader else None,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2),
            'file_type': self.file_type,
            'title': self.title or self.filename,
            'description': self.description,
            'is_active': self.is_active,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

