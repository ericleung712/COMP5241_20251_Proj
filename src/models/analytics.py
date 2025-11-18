from src.database import db
from datetime import datetime
import json

class Leaderboard(db.Model):
    """排行榜模型"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 排行榜名称
    description = db.Column(db.Text, nullable=True)
    
    # 排行榜配置
    config = db.Column(db.JSON, nullable=True)  # JSON格式存储配置
    
    # 时间范围
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_config(self, config_dict):
        """设置排行榜配置"""
        self.config = config_dict
    
    def get_config(self):
        """获取排行榜配置"""
        return self.config or {}
    
    def __repr__(self):
        return f'<Leaderboard {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else None,
            'name': self.name,
            'description': self.description,
            'config': self.get_config(),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityAnalytics(db.Model):
    """活动分析模型"""
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    
    # 分析数据（JSON格式）
    analytics_data = db.Column(db.JSON, nullable=False)
    
    # AI生成的分析报告
    ai_report = db.Column(db.JSON, nullable=True)
    
    # 分析时间
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_analytics_data(self, data_dict):
        """设置分析数据"""
        self.analytics_data = data_dict
    
    def get_analytics_data(self):
        """获取分析数据"""
        return self.analytics_data or {}
    
    def set_ai_report(self, report_dict):
        """设置AI报告"""
        self.ai_report = report_dict
    
    def get_ai_report(self):
        """获取AI报告"""
        return self.ai_report or {}
    
    def __repr__(self):
        return f'<ActivityAnalytics {self.activity.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'activity_title': self.activity.title if self.activity else None,
            'analytics_data': self.get_analytics_data(),
            'ai_report': self.get_ai_report(),
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }
