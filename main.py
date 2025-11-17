from flask import Flask, render_template_string
from src.database import db
from src.models.user import User
from src.models.course import Course, course_enrollments
from src.models.activity import Activity
from src.models.response import ActivityResponse
from src.models.analytics import Leaderboard, ActivityAnalytics
from src.models.document import Document
from src.models.forum import ForumPost, ForumReply, UserForumRead
from src.routes.auth import auth_bp
from src.routes.course import course_bp
from src.routes.activity import activity_bp
from src.routes.response import response_bp
from src.routes.analytics import analytics_bp
from src.routes.admin import admin_bp
from src.routes.document import document_bp
from src.routes.ai_qa import ai_qa_bp
from src.routes.forum import forum_bp
import os

def create_app():
    app = Flask(__name__, static_folder='src/static', template_folder='src/static')
    
    # 确保数据库目录存在
    os.makedirs('database', exist_ok=True)
    
    # 配置数据库 - 使用绝对路径
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'smart-classroom-secret-key-2024'
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(course_bp, url_prefix='/api/courses')
    app.register_blueprint(activity_bp, url_prefix='/api/activities')
    app.register_blueprint(response_bp, url_prefix='/api/responses')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    app.register_blueprint(ai_qa_bp, url_prefix='/api/ai-qa')
    app.register_blueprint(forum_bp, url_prefix='/api/forum')
    
    # 主页路由
    @app.route('/')
    def index():
        with open('src/static/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # 教师仪表板
    @app.route('/teacher')
    def teacher_dashboard():
        with open('src/static/teacher.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # 学生仪表板
    @app.route('/student')
    def student_dashboard():
        with open('src/static/student.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # 管理员仪表板
    @app.route('/admin')
    def admin_dashboard():
        with open('src/static/admin.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # 登录页面
    @app.route('/login')
    def login_page():
        with open('src/static/login.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # 登出页面（重定向到首页）
    @app.route('/logout')
    def logout_page():
        with open('src/static/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员账户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@polyu.edu.hk',
                full_name='System Administrator',
                role='admin',
                department='IT Services'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)