from src.database import db
from datetime import datetime
import json

class Activity(db.Model):
    """学习活动模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    activity_type = db.Column(db.String(50), nullable=False)  # poll, quiz, word_cloud, short_answer, mini_game
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 活动配置（JSON格式存储）
    config = db.Column(db.JSON, nullable=True)  # 存储活动特定配置
    
    # AI生成相关
    is_ai_generated = db.Column(db.Boolean, default=False)
    ai_prompt = db.Column(db.Text, nullable=True)
    ai_refined = db.Column(db.Boolean, default=False)
    
    # 状态和时间
    status = db.Column(db.String(20), default='draft')  # draft, active, completed, archived
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, default=10)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    responses = db.relationship('ActivityResponse', backref='activity', lazy=True, cascade='all, delete-orphan')
    
    def set_config(self, config_dict):
        """设置活动配置"""
        self.config = config_dict
    
    def get_config(self):
        """获取活动配置"""
        return self.config or {}
    
    def __repr__(self):
        return f'<Activity {self.title} ({self.activity_type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'activity_type': self.activity_type,
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else None,
            'creator_id': self.creator_id,
            'creator_name': self.creator.full_name if self.creator else None,
            'config': self.get_config(),
            'is_ai_generated': self.is_ai_generated,
            'ai_prompt': self.ai_prompt,
            'ai_refined': self.ai_refined,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'response_count': len(self.responses),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
