from flask import Blueprint, request, jsonify, session
from src.models.analytics import Leaderboard, ActivityAnalytics
from src.models.course import Course
from src.models.activity import Activity
from src.models.response import ActivityResponse
from src.models.user import User
from src.database import db
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

def require_auth():
    """验证用户是否已登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """获取仪表板数据"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    if user.role == 'teacher':
        # 教师仪表板数据
        courses = Course.query.filter_by(teacher_id=user.id).all()
        activities = Activity.query.filter_by(creator_id=user.id).all()
        
        # 统计信息
        total_courses = len(courses)
        total_activities = len(activities)
        active_activities = len([a for a in activities if a.status == 'active'])
        completed_activities = len([a for a in activities if a.status == 'completed'])
        
        # 最近活动
        recent_activities = Activity.query.filter_by(creator_id=user.id)\
            .order_by(Activity.created_at.desc()).limit(5).all()
        
        # 学生参与度统计
        participation_stats = []
        for course in courses:
            total_students = len(course.students)
            if total_students > 0:
                avg_participation = db.session.query(ActivityResponse)\
                    .join(Activity)\
                    .filter(Activity.course_id == course.id)\
                    .count() / total_students
                participation_stats.append({
                    'course_name': course.course_name,
                    'participation_rate': min(avg_participation, 1.0)
                })
        
        return jsonify({
            'role': 'teacher',
            'stats': {
                'total_courses': total_courses,
                'total_activities': total_activities,
                'active_activities': active_activities,
                'completed_activities': completed_activities
            },
            'recent_activities': [activity.to_dict() for activity in recent_activities],
            'participation_stats': participation_stats
        })
    
    elif user.role == 'student':
        # 学生仪表板数据
        enrolled_courses = Course.query.join(Course.students).filter(
            User.id == user.id
        ).all()
        
        # 参与的活动
        participated_activities = db.session.query(Activity)\
            .join(ActivityResponse)\
            .filter(ActivityResponse.student_id == user.id)\
            .all()
        
        # 统计信息
        total_courses = len(enrolled_courses)
        total_participations = len(participated_activities)
        avg_score = db.session.query(db.func.avg(ActivityResponse.score)).filter(ActivityResponse.student_id == user.id).scalar() or 0
        
        # 最近参与的活动
        recent_responses = ActivityResponse.query.filter_by(student_id=user.id)\
            .order_by(ActivityResponse.submitted_at.desc()).limit(5).all()
        
        return jsonify({
            'role': 'student',
            'stats': {
                'total_courses': total_courses,
                'total_participations': total_participations,
                'avg_score': round(avg_score, 2)
            },
            'recent_responses': [response.to_dict() for response in recent_responses]
        })
    
    elif user.role == 'admin':
        # 管理员仪表板数据
        total_users = User.query.count()
        total_courses = Course.query.count()
        total_activities = Activity.query.count()
        total_responses = ActivityResponse.query.count()
        
        # 活跃用户（最近30天有提交响应的用户）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.session.query(ActivityResponse.student_id)\
            .filter(ActivityResponse.submitted_at >= thirty_days_ago)\
            .distinct().count()
        
        # AI活动数量
        ai_activities = Activity.query.filter(Activity.is_ai_generated == True).count()
        
        # 用户角色分布
        role_stats = db.session.query(User.role, db.func.count(User.id))\
            .group_by(User.role).all()
        
        # 最近注册的用户
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        return jsonify({
            'role': 'admin',
            'stats': {
                'total_users': total_users,
                'total_courses': total_courses,
                'total_activities': total_activities,
                'total_responses': total_responses,
                'active_users': active_users,
                'ai_activities': ai_activities
            },
            'role_stats': [{'role': role, 'count': count} for role, count in role_stats],
            'recent_users': [user.to_dict() for user in recent_users]
        })

@analytics_bp.route('/leaderboard/<int:course_id>', methods=['GET'])
def get_leaderboard(course_id):
    """获取课程排行榜"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    course = Course.query.get_or_404(course_id)
    
    # 权限检查
    if user.role == 'teacher' and course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    elif user.role == 'student':
        # 检查学生是否注册了该课程
        enrollment = db.session.query(course.students).filter(
            User.id == user.id
        ).first()
        if not enrollment:
            return jsonify({'error': '未注册该课程'}), 403
    
    # 计算学生积分
    student_scores = []
    for student in course.students:
        # 计算参与度分数
        participation_count = ActivityResponse.query.join(Activity)\
            .filter(Activity.course_id == course_id)\
            .filter(ActivityResponse.student_id == student.id)\
            .count()
        
        # 计算平均分数
        avg_score = db.session.query(db.func.avg(ActivityResponse.score))\
            .join(Activity)\
            .filter(Activity.course_id == course_id)\
            .filter(ActivityResponse.student_id == student.id)\
            .scalar() or 0
        
        total_score = participation_count * 10 + avg_score
        
        student_scores.append({
            'student_id': student.id,
            'student_name': student.full_name,
            'student_id_number': student.student_id,
            'participation_count': participation_count,
            'avg_score': round(avg_score, 2),
            'total_score': round(total_score, 2)
        })
    
    # 按总分排序
    student_scores.sort(key=lambda x: x['total_score'], reverse=True)
    
    return jsonify({
        'course_name': course.course_name,
        'leaderboard': student_scores
    })

@analytics_bp.route('/activity/<int:activity_id>/analytics', methods=['GET'])
def get_activity_analytics(activity_id):
    """获取活动分析数据（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    responses = ActivityResponse.query.filter_by(activity_id=activity_id).all()
    
    # 基本统计
    total_responses = len(responses)
    avg_score = sum(r.score or 0 for r in responses) / total_responses if total_responses > 0 else 0
    avg_time = sum(r.time_spent_seconds or 0 for r in responses) / total_responses if total_responses > 0 else 0
    
    # 按时间分布
    time_distribution = {}
    for response in responses:
        hour = response.submitted_at.hour
        time_distribution[hour] = time_distribution.get(hour, 0) + 1
    
    # 分数分布
    score_distribution = {}
    for response in responses:
        if response.score is not None:
            score_range = int(response.score // 10) * 10
            score_distribution[f"{score_range}-{score_range+9}"] = score_distribution.get(f"{score_range}-{score_range+9}", 0) + 1
    
    return jsonify({
        'activity_title': activity.title,
        'total_responses': total_responses,
        'avg_score': round(avg_score, 2),
        'avg_time_seconds': round(avg_time, 2),
        'time_distribution': time_distribution,
        'score_distribution': score_distribution,
        'responses': [response.to_dict() for response in responses]
    })

@analytics_bp.route('/course/<int:course_id>/analytics', methods=['GET'])
def get_course_analytics(course_id):
    """获取课程分析数据（仅教师）"""
    user = require_auth()
    if not user or user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    # 课程活动统计
    activities = Activity.query.filter_by(course_id=course_id).all()
    activity_stats = []
    
    for activity in activities:
        responses = ActivityResponse.query.filter_by(activity_id=activity.id).all()
        activity_stats.append({
            'activity_id': activity.id,
            'activity_title': activity.title,
            'activity_type': activity.activity_type,
            'response_count': len(responses),
            'avg_score': sum(r.score or 0 for r in responses) / len(responses) if responses else 0,
            'status': activity.status
        })
    
    # 学生参与度
    student_participation = []
    for student in course.students:
        participation_count = ActivityResponse.query.join(Activity)\
            .filter(Activity.course_id == course_id)\
            .filter(ActivityResponse.student_id == student.id)\
            .count()
        
        student_participation.append({
            'student_id': student.id,
            'student_name': student.full_name,
            'participation_count': participation_count,
            'participation_rate': participation_count / len(activities) if activities else 0
        })
    
    return jsonify({
        'course_name': course.course_name,
        'total_activities': len(activities),
        'total_students': len(course.students),
        'activity_stats': activity_stats,
        'student_participation': student_participation
    })

@analytics_bp.route('/teacher/system-overview', methods=['GET'])
def get_teacher_system_overview():
    """获取教师系统概览数据分析（仅教师）"""
    user = require_auth()
    if not user:
        return jsonify({'error': '未登录'}), 401
    if user.role != 'teacher':
        return jsonify({'error': '权限不足'}), 403
    
    from sqlalchemy import func
    
    # 获取日期范围参数
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # 解析日期参数
    try:
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        else:
            start_date = datetime.utcnow().replace(day=1) - timedelta(days=365)  # 默认过去12个月
        
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        else:
            end_date = datetime.utcnow()  # 默认当前时间
    except ValueError:
        return jsonify({'error': '无效的日期格式，请使用ISO格式 (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    # 确保开始日期不晚于结束日期
    if start_date > end_date:
        return jsonify({'error': '开始日期不能晚于结束日期'}), 400
    
    # 获取教师的课程
    courses = Course.query.filter_by(teacher_id=user.id).all()
    
    course_data = []
    total_completion_rate = 0
    total_time_spent = 0
    total_quiz_score = 0
    course_count = 0
    
    for course in courses:
        # 课程活动总数
        total_activities = Activity.query.filter_by(course_id=course.id).count()
        
        if total_activities == 0:
            continue
        
        # 已完成的活动数（有响应的活动）
        completed_activities = db.session.query(Activity.id).join(
            ActivityResponse, Activity.id == ActivityResponse.activity_id
        ).filter(Activity.course_id == course.id).distinct().count()
        
        completion_rate = (completed_activities / total_activities) * 100 if total_activities > 0 else 0
        
        # 时间花费统计
        time_stats = db.session.query(
            func.sum(ActivityResponse.time_spent_seconds).label('total_time'),
            func.avg(ActivityResponse.time_spent_seconds).label('avg_time'),
            func.count(ActivityResponse.student_id.distinct()).label('user_count')
        ).filter(
            ActivityResponse.activity_id.in_(
                db.session.query(Activity.id).filter_by(course_id=course.id)
            )
        ).first()
        
        total_time = time_stats.total_time or 0
        avg_time_per_user = time_stats.avg_time or 0
        users_with_responses = time_stats.user_count or 0
        
        # 测验分数统计（仅测验活动）
        quiz_stats = db.session.query(
            func.avg(ActivityResponse.score).label('avg_score'),
            func.count(ActivityResponse.id).label('response_count')
        ).filter(
            ActivityResponse.activity_id.in_(
                db.session.query(Activity.id).filter_by(course_id=course.id, activity_type='quiz')
            )
        ).first()
        
        avg_quiz_score = quiz_stats.avg_score or 0
        quiz_responses = quiz_stats.response_count or 0
        
        course_data.append({
            'course_id': course.id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'completion_rate': round(completion_rate, 2),
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'total_time_spent_seconds': total_time,
            'avg_time_per_user_seconds': float(round(avg_time_per_user, 2)),
            'users_with_responses': users_with_responses,
            'avg_quiz_score': round(avg_quiz_score, 2),
            'quiz_responses': quiz_responses
        })
        
        total_completion_rate += completion_rate
        total_time_spent += total_time
        total_quiz_score += avg_quiz_score
        course_count += 1
    
    # 系统级汇总
    system_aggregates = {
        'avg_completion_rate': round(total_completion_rate / course_count, 2) if course_count > 0 else 0,
        'total_time_spent_seconds': total_time_spent,
        'avg_quiz_score': round(total_quiz_score / course_count, 2) if course_count > 0 else 0,
        'total_courses_analyzed': course_count
    }
    
    return jsonify({
        'system_aggregates': system_aggregates,
        'course_breakdown': course_data,
        'date_range': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    })
