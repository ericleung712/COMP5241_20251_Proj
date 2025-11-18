from flask import Blueprint, request, jsonify, session
from src.models.user import User
from src.models.course import Course, course_enrollments
from src.models.activity import Activity
from src.models.response import ActivityResponse
from src.database import db
from datetime import datetime, timedelta
from src.utils.email_validator import validate_polyu_email
import pandas as pd
import io

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """验证管理员权限"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None
    return user

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """获取所有用户（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role_filter = request.args.get('role')
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """创建新用户（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    # 验证必需字段
    required_fields = ['username', 'email', 'full_name', 'role', 'password']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
    
    # 验证邮箱格式
    is_valid, error_msg = validate_polyu_email(data['email'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # 验证角色
    if data['role'] not in ['teacher', 'student', 'admin']:
        return jsonify({'error': '无效的用户角色'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 如果是学生，验证student_id
    if data['role'] == 'student':
        if not data.get('student_id'):
            return jsonify({'error': '学生角色必须提供student_id'}), 400
        # 检查student_id是否已被使用
        if User.query.filter_by(student_id=data['student_id']).first():
            return jsonify({'error': '学生ID已存在'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        role=data['role'],
        department=data.get('department'),
        student_id=data.get('student_id') if data['role'] == 'student' else None
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '用户创建成功',
        'user': user.to_dict()
    }), 201

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取特定用户信息（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        # 验证邮箱格式
        is_valid, error_msg = validate_polyu_email(data['email'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        user.email = data['email']
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'role' in data:
        if data['role'] in ['teacher', 'student', 'admin']:
            user.role = data['role']
    if 'student_id' in data:
        user.student_id = data['student_id']
    if 'department' in data:
        user.department = data['department']
    
    db.session.commit()
    
    return jsonify({
        'message': '用户信息更新成功',
        'user': user.to_dict()
    })

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == admin.id:
        return jsonify({'error': '不能删除自己的账户'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'})

@admin_bp.route('/courses', methods=['GET'])
def get_all_courses():
    """获取所有课程（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])

@admin_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """获取特定课程信息（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    return jsonify(course.to_dict())

@admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """更新课程信息（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    if 'course_code' in data:
        # 检查课程代码是否已被其他课程使用
        existing_course = Course.query.filter_by(course_code=data['course_code']).first()
        if existing_course and existing_course.id != course_id:
            return jsonify({'error': '课程代码已被使用'}), 400
        course.course_code = data['course_code']
    if 'course_name' in data:
        course.course_name = data['course_name']
    if 'description' in data:
        course.description = data['description']
    if 'is_active' in data:
        course.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': '课程信息更新成功',
        'course': course.to_dict()
    })

@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """删除课程（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({'message': '课程删除成功'})

@admin_bp.route('/activities', methods=['GET'])
def get_all_activities():
    """获取所有活动（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    activities = Activity.query.all()
    return jsonify([activity.to_dict() for activity in activities])

@admin_bp.route('/activities/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    """删除活动（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({'message': '活动删除成功'})

@admin_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """获取系统统计信息（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    # 基本统计
    total_users = User.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    total_courses = Course.query.count()
    total_activities = Activity.query.count()
    total_responses = ActivityResponse.query.count()
    
    # 活跃用户（最近7天登录）
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = User.query.filter(User.last_login >= week_ago).count()
    
    # 最近活动统计
    recent_activities = Activity.query.filter(
        Activity.created_at >= week_ago
    ).count()
    
    # AI生成活动统计
    ai_activities = Activity.query.filter_by(is_ai_generated=True).count()
    
    return jsonify({
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_activities': total_activities,
        'total_responses': total_responses,
        'active_users': active_users,
        'recent_activities': recent_activities,
        'ai_activities': ai_activities
    })

@admin_bp.route('/system-overview', methods=['GET'])
def get_system_overview():
    """获取系统概览数据分析（仅管理员）"""
    admin = require_admin()
    if not admin:
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
    
    # 获取所有课程
    courses = Course.query.all()
    
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
            'completion_rate': float(round(completion_rate, 2)),
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'total_time_spent_seconds': total_time,
            'avg_time_per_user_seconds': float(round(avg_time_per_user, 2)),
            'users_with_responses': users_with_responses,
            'avg_quiz_score': float(round(avg_quiz_score, 2)),
            'quiz_responses': quiz_responses
        })
        
        total_completion_rate += completion_rate
        total_time_spent += total_time
        total_quiz_score += avg_quiz_score
        course_count += 1
    
    # 系统级汇总
    system_aggregates = {
        'avg_completion_rate': float(round(total_completion_rate / course_count, 2)) if course_count > 0 else 0.0,
        'total_time_spent_seconds': total_time_spent,
        'avg_quiz_score': float(round(total_quiz_score / course_count, 2)) if course_count > 0 else 0.0,
        'total_courses_analyzed': course_count
    }
    
    # 用户活动时间序列数据
    user_activity_data = []
    
    # 获取用户注册和登录数据
    users = User.query.with_entities(
        User.created_at,
        User.last_login
    ).all()
    
    # 创建时间序列数据（按月）
    from collections import defaultdict
    import calendar
    
    # 初始化每月数据
    monthly_data = defaultdict(lambda: {'total_users': 0, 'active_users': 0})
    
    # 计算每月累计用户数
    cumulative_users = 0
    
    # 生成月份列表
    current_date = start_date.replace(day=1)
    months_list = []
    while current_date <= end_date:
        months_list.append(current_date)
        # 移动到下个月
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    for month_start in months_list:
        month_end = datetime(month_start.year, month_start.month, 
                           calendar.monthrange(month_start.year, month_start.month)[1], 
                           23, 59, 59)
        
        month_key = f"{month_start.year}-{month_start.month:02d}"
        
        # 当月注册的用户数
        monthly_registrations = sum(1 for user in users 
                                  if month_start <= user.created_at <= month_end)
        cumulative_users += monthly_registrations
        
        # 当月活跃用户数（有登录记录的用户）
        monthly_active = sum(1 for user in users 
                           if user.last_login and month_start <= user.last_login <= month_end)
        
        monthly_data[month_key] = {
            'total_users': cumulative_users,
            'active_users': monthly_active,
            'month': month_key
        }
    
    # 转换为列表格式
    user_activity_data = [
        {
            'month': key,
            'total_users': value['total_users'],
            'active_users': value['active_users']
        }
        for key, value in sorted(monthly_data.items())
    ]
    
    return jsonify({
        'system_aggregates': system_aggregates,
        'course_breakdown': course_data,
        'user_activity': user_activity_data,
        'date_range': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    })

@admin_bp.route('/backup', methods=['POST'])
def create_backup():
    """创建系统备份（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    # 这里可以实现数据库备份逻辑
    # 目前返回成功消息
    return jsonify({
        'message': '备份创建成功',
        'backup_id': f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    })

@admin_bp.route('/logs', methods=['GET'])
def get_system_logs():
    """获取系统日志（仅管理员）"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    # 这里可以实现日志查看逻辑
    # 目前返回示例日志
    logs = [
        {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'INFO',
            'message': '系统启动',
            'user': 'system'
        },
        {
            'timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            'level': 'INFO',
            'message': '用户登录',
            'user': admin.username
        }
    ]
    
    return jsonify({
        'logs': logs,
        'total': len(logs)
    })

@admin_bp.route('/import-users-excel', methods=['POST'])
def import_users_excel():
    """通过Excel文件批量导入用户（学生和教师）- 仅管理员"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': '权限不足'}), 403
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 检查文件扩展名
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': '只支持Excel文件(.xlsx, .xls)'}), 400
    
    try:
        # 读取Excel文件
        file_content = file.read()
        df = pd.read_excel(io.BytesIO(file_content))
        
        # 检查必需的列
        required_columns = ['username', 'full_name', 'email', 'role']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': f'Excel文件缺少必需的列: {", ".join(missing_columns)}',
                'required_columns': required_columns,
                'found_columns': list(df.columns)
            }), 400
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        enrolled_count = 0
        errors = []
        
        # 处理每一行数据
        for index, row in df.iterrows():
            try:
                # 获取用户信息
                username = str(row['username']).strip()
                full_name = str(row['full_name']).strip()
                email = str(row['email']).strip()
                role = str(row['role']).strip().lower()
                department = str(row.get('department', '')).strip() if pd.notna(row.get('department')) else ''
                student_id = str(row.get('student_id', '')).strip() if pd.notna(row.get('student_id')) else ''
                course_code = str(row.get('course_code', '')).strip() if pd.notna(row.get('course_code')) else ''
                
                # 验证必需字段
                if not username or not full_name or not email or not role:
                    errors.append(f"第{index+2}行: 用户名、姓名、邮箱或角色为空")
                    skipped_count += 1
                    continue
                
                # 验证邮箱格式
                is_valid, error_msg = validate_polyu_email(email)
                if not is_valid:
                    errors.append(f"第{index+2}行: {error_msg} (邮箱: {email})")
                    skipped_count += 1
                    continue
                
                # 验证角色
                if role not in ['student', 'teacher']:
                    errors.append(f"第{index+2}行: 角色必须是 'student' 或 'teacher'，当前为: {role}")
                    skipped_count += 1
                    continue
                
                # 如果是学生，必须有student_id
                if role == 'student' and not student_id:
                    errors.append(f"第{index+2}行: 学生角色必须提供student_id")
                    skipped_count += 1
                    continue
                
                # 检查用户是否已存在
                user = User.query.filter_by(username=username).first()
                if not user:
                    # 检查邮箱是否已被使用
                    existing_email = User.query.filter_by(email=email).first()
                    if existing_email:
                        errors.append(f"第{index+2}行: 邮箱已被使用 (用户名: {username})")
                        skipped_count += 1
                        continue
                    
                    # 如果是学生，检查student_id是否已被使用
                    if role == 'student' and student_id:
                        existing_student = User.query.filter_by(student_id=student_id).first()
                        if existing_student:
                            errors.append(f"第{index+2}行: 学生ID已被使用 (用户名: {username})")
                            skipped_count += 1
                            continue
                    
                    # 创建新用户账户
                    user = User(
                        username=username,
                        email=email,
                        full_name=full_name,
                        role=role,
                        department=department
                    )
                    
                    if role == 'student':
                        user.student_id = student_id
                    
                    user.set_password('123456')  # 默认密码
                    db.session.add(user)
                    db.session.flush()  # 获取ID
                    imported_count += 1
                else:
                    # 更新现有用户信息（如果需要）
                    if user.full_name != full_name:
                        user.full_name = full_name
                    if user.email != email:
                        # 验证邮箱格式
                        is_valid, error_msg = validate_polyu_email(email)
                        if not is_valid:
                            errors.append(f"第{index+2}行: {error_msg} (邮箱: {email})")
                            skipped_count += 1
                            continue
                        # 检查新邮箱是否已被使用
                        existing_email = User.query.filter_by(email=email).first()
                        if existing_email and existing_email.id != user.id:
                            errors.append(f"第{index+2}行: 邮箱已被其他用户使用 (用户名: {username})")
                            skipped_count += 1
                            continue
                        user.email = email
                    if department and user.department != department:
                        user.department = department
                    if role == 'student' and student_id and user.student_id != student_id:
                        # 检查新student_id是否已被使用
                        existing_student = User.query.filter_by(student_id=student_id).first()
                        if existing_student and existing_student.id != user.id:
                            errors.append(f"第{index+2}行: 学生ID已被其他用户使用 (用户名: {username})")
                            skipped_count += 1
                            continue
                        user.student_id = student_id
                    updated_count += 1
                
                # 如果Excel中有course_code，注册到对应课程（仅学生）
                if course_code and role == 'student':
                    course = Course.query.filter_by(course_code=course_code).first()
                    if course:
                        # 检查是否已经注册该课程
                        enrollment = db.session.query(course_enrollments).filter(
                            course_enrollments.c.course_id == course.id,
                            course_enrollments.c.user_id == user.id
                        ).first()
                        
                        if not enrollment:
                            db.session.execute(course_enrollments.insert().values(
                                course_id=course.id,
                                user_id=user.id,
                                enrolled_at=datetime.utcnow()
                            ))
                            enrolled_count += 1
                    else:
                        errors.append(f"第{index+2}行: 课程代码 {course_code} 不存在")
                
            except Exception as e:
                errors.append(f"第{index+2}行: 处理失败 - {str(e)}")
                skipped_count += 1
                continue
        
        db.session.commit()
        
        return jsonify({
            'message': f'Excel导入完成',
            'imported_count': imported_count,
            'updated_count': updated_count,
            'enrolled_count': enrolled_count,
            'skipped_count': skipped_count,
            'total_rows': len(df),
            'errors': errors[:20]  # 只返回前20个错误
        })
        
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'Excel文件为空'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'处理Excel文件时出错: {str(e)}'}), 500
