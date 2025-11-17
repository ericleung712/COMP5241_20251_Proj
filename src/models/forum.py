from src.database import db
from datetime import datetime

class ForumPost(db.Model):
    """论坛帖子模型"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_pinned = db.Column(db.Boolean, default=False)
    reply_count = db.Column(db.Integer, default=0)
    
    # 关系
    replies = db.relationship('ForumReply', backref='post', lazy=True, cascade='all, delete-orphan', order_by='ForumReply.created_at')
    
    def __repr__(self):
        return f'<ForumPost {self.title} by {self.user.full_name if self.user else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_pinned': self.is_pinned,
            'reply_count': self.reply_count
        }

class ForumReply(db.Model):
    """论坛回复模型 - 支持线程化回复"""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_reply_id = db.Column(db.Integer, db.ForeignKey('forum_reply.id'), nullable=True)  # 用于线程化回复
    
    # 关系
    child_replies = db.relationship('ForumReply', backref=db.backref('parent_reply', remote_side=[id]), lazy=True, cascade='all, delete-orphan', order_by='ForumReply.created_at')
    
    def __repr__(self):
        return f'<ForumReply by {self.user.full_name if self.user else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'parent_reply_id': self.parent_reply_id
        }

class UserForumRead(db.Model):
    """用户论坛阅读记录 - 用于通知"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to ensure one record per user per course
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_read'),)
    
    def __repr__(self):
        return f"UserForumRead(user={self.user_id}, course={self.course_id})"