from src.database import db
from datetime import datetime
import json

class ActivityResponse(db.Model):
    """活动响应模型"""
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 响应内容（JSON格式存储不同类型的答案）
    response_data = db.Column(db.Text, nullable=False)
    
    # AI分析结果
    ai_analysis = db.Column(db.Text, nullable=True)  # AI对答案的分析
    similarity_score = db.Column(db.Float, nullable=True)  # 与其他答案的相似度
    
    # 评分和反馈
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # 时间信息
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent_seconds = db.Column(db.Integer, nullable=True)
    
    def set_response_data(self, data_dict):
        """设置响应数据"""
        self.response_data = json.dumps(data_dict)
    
    def get_response_data(self):
        """获取响应数据"""
        if self.response_data:
            return json.loads(self.response_data)
        return {}
    
    def set_ai_analysis(self, analysis_dict):
        """设置AI分析结果"""
        self.ai_analysis = json.dumps(analysis_dict)
    
    def get_ai_analysis(self):
        """获取AI分析结果"""
        if self.ai_analysis:
            return json.loads(self.ai_analysis)
        return {}
    
    def __repr__(self):
        return f'<ActivityResponse {self.student.username} -> {self.activity.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'activity_title': self.activity.title if self.activity else None,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'student_username': self.student.username if self.student else None,
            'response_data': self.get_response_data(),
            'ai_analysis': self.get_ai_analysis(),
            'similarity_score': self.similarity_score,
            'score': self.score,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'time_spent_seconds': self.time_spent_seconds
        }
