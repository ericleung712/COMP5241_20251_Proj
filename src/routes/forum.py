from flask import Blueprint, request, jsonify, session
from src.models.forum import ForumPost, ForumReply, UserForumRead
from src.models.course import Course, course_enrollments
from src.models.user import User
from src.database import db
from datetime import datetime
from sqlalchemy import or_, and_

forum_bp = Blueprint('forum', __name__)

def require_auth():
    """验证用户是否已登录"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

def check_course_access(user, course_id):
    """Check if user has permission to access course forum"""
    course = Course.query.get_or_404(course_id)
    
    # Teachers can access courses they teach
    if user.role == 'teacher' and course.teacher_id == user.id:
        return True
    
    # Students must be enrolled in the course
    if user.role == 'student':
        enrollment = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id == course_id,
            course_enrollments.c.user_id == user.id
        ).first()
        return enrollment is not None
    
    # Admins can access all courses
    if user.role == 'admin':
        return True
    
    return False

def can_modify_post(user, post):
    """Check if user can modify the post"""
    return user.id == post.user_id or (user.role == 'teacher' and post.course.teacher_id == user.id)

def can_modify_reply(user, reply):
    """Check if user can modify the reply"""
    return user.id == reply.user_id or (user.role == 'teacher' and reply.post.course.teacher_id == user.id)

@forum_bp.route('/<int:course_id>', methods=['GET'])
def get_forum_posts(course_id):
    """获取课程论坛帖子列表"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    if not check_course_access(user, course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('q', '').strip()
    
    query = ForumPost.query.filter_by(course_id=course_id)
    
    # 搜索功能
    if search:
        query = query.filter(
            or_(
                ForumPost.title.contains(search),
                ForumPost.content.contains(search)
            )
        )
    
    # 置顶帖子优先，然后按创建时间倒序
    query = query.order_by(ForumPost.is_pinned.desc(), ForumPost.created_at.desc())
    
    # 分页
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Add can_delete field to each post
    posts_data = []
    for post in posts.items:
        post_dict = post.to_dict()
        post_dict['can_delete'] = can_modify_post(user, post)
        posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': posts.page,
        'has_next': posts.has_next,
        'has_prev': posts.has_prev
    })

@forum_bp.route('/<int:course_id>', methods=['POST'])
def create_forum_post(course_id):
    """创建新帖子"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    if not check_course_access(user, course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    data = request.get_json()
    if not data or not all(k in data for k in ['title', 'content']):
        return jsonify({'error': 'Missing title or content'}), 400
    
    if len(data['title'].strip()) == 0 or len(data['content'].strip()) == 0:
        return jsonify({'error': 'Title and content cannot be empty'}), 400
    
    post = ForumPost(
        course_id=course_id,
        user_id=user.id,
        title=data['title'].strip(),
        content=data['content'].strip()
    )
    
    db.session.add(post)
    db.session.commit()
    
    post_dict = post.to_dict()
    post_dict['can_delete'] = can_modify_post(user, post)
    
    return jsonify({
        'message': 'Post created successfully',
        'post': post_dict
    }), 201

@forum_bp.route('/post/<int:post_id>', methods=['PUT'])
def update_forum_post(post_id):
    """更新帖子"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    post = ForumPost.query.get_or_404(post_id)
    
    if not check_course_access(user, post.course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    if not can_modify_post(user, post):
        return jsonify({'error': 'No permission to modify this post'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' in data:
        title = data['title'].strip()
        if len(title) == 0:
            return jsonify({'error': 'Title cannot be empty'}), 400
        post.title = title
    
    if 'content' in data:
        content = data['content'].strip()
        if len(content) == 0:
            return jsonify({'error': 'Content cannot be empty'}), 400
        post.content = content
    
    if 'is_pinned' in data and user.role == 'teacher' and post.course.teacher_id == user.id:
        post.is_pinned = bool(data['is_pinned'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Post updated successfully',
        'post': post.to_dict()
    })

@forum_bp.route('/post/<int:post_id>', methods=['DELETE'])
def delete_forum_post(post_id):
    """软删除帖子"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    post = ForumPost.query.get_or_404(post_id)
    
    if not check_course_access(user, post.course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    if not can_modify_post(user, post):
        return jsonify({'error': 'No permission to delete this post'}), 403
    
    # Soft delete: replace content with deletion message based on user role
    if user.role == 'teacher':
        post.content = 'The post is deleted by the teacher'
    else:
        post.content = 'The post is deleted by owner'
    post.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'})

@forum_bp.route('/post/<int:post_id>/replies', methods=['GET'])
def get_forum_replies(post_id):
    """获取帖子的回复列表"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    post = ForumPost.query.get_or_404(post_id)
    
    if not check_course_access(user, post.course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    # 获取所有回复，按线程化方式组织
    all_replies = ForumReply.query.filter_by(post_id=post_id).order_by(ForumReply.created_at).all()
    
    # 构建线程化结构
    reply_dict = {reply.id: reply.to_dict() for reply in all_replies}
    threaded_replies = []
    
    for reply in all_replies:
        if reply.parent_reply_id is None:
            # 顶级回复
            reply_data = reply_dict[reply.id]
            reply_data['child_replies'] = []
            reply_data['can_delete'] = can_modify_reply(user, reply)
            threaded_replies.append(reply_data)
        else:
            # 子回复
            parent = reply_dict.get(reply.parent_reply_id)
            if parent:
                if 'child_replies' not in parent:
                    parent['child_replies'] = []
                reply_dict[reply.id]['can_delete'] = can_modify_reply(user, reply)
                parent['child_replies'].append(reply_dict[reply.id])
    
    # Add can_delete to post
    post_data = post.to_dict()
    post_data['can_delete'] = can_modify_post(user, post)
    
    return jsonify({
        'post': post_data,
        'replies': threaded_replies
    })

@forum_bp.route('/post/<int:post_id>/reply', methods=['POST'])
def create_forum_reply(post_id):
    """创建回复"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    post = ForumPost.query.get_or_404(post_id)
    
    if not check_course_access(user, post.course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing reply content'}), 400
    
    content = data['content'].strip()
    if len(content) == 0:
        return jsonify({'error': '回复Content cannot be empty'}), 400
    
    parent_reply_id = data.get('parent_reply_id')
    if parent_reply_id:
        # 检查父回复是否存在且属于同一帖子
        parent_reply = ForumReply.query.filter_by(id=parent_reply_id, post_id=post_id).first()
        if not parent_reply:
            return jsonify({'error': 'Parent reply does not exist'}), 400
        
        # 检查回复深度是否超过3层
        def get_reply_depth(reply_id):
            """计算回复的深度（0表示顶级回复）"""
            reply = ForumReply.query.get(reply_id)
            depth = 0
            while reply and reply.parent_reply_id:
                depth += 1
                reply = ForumReply.query.get(reply.parent_reply_id)
            return depth
        
        parent_depth = get_reply_depth(parent_reply_id)
        if parent_depth >= 2:  # 如果父回复已经是第3层，则不能再回复
            return jsonify({'error': 'Cannot reply to this comment. Maximum nesting depth (3 levels) exceeded.'}), 400
    
    reply = ForumReply(
        post_id=post_id,
        user_id=user.id,
        content=content,
        parent_reply_id=parent_reply_id
    )
    
    db.session.add(reply)
    
    # 更新帖子回复计数
    post.reply_count += 1
    post.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    reply_dict = reply.to_dict()
    reply_dict['can_delete'] = can_modify_reply(user, reply)
    
    return jsonify({
        'message': 'Reply created successfully',
        'reply': reply_dict
    }), 201

@forum_bp.route('/reply/<int:reply_id>', methods=['PUT'])
def update_forum_reply(reply_id):
    """更新回复"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    reply = ForumReply.query.get_or_404(reply_id)
    
    if not check_course_access(user, reply.post.course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    if not can_modify_reply(user, reply):
        return jsonify({'error': 'No permission to modify this reply'}), 403
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing reply content'}), 400
    
    content = data['content'].strip()
    if len(content) == 0:
        return jsonify({'error': '回复Content cannot be empty'}), 400
    
    reply.content = content
    reply.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Reply updated successfully',
        'reply': reply.to_dict()
    })

@forum_bp.route('/reply/<int:reply_id>', methods=['DELETE'])
def delete_forum_reply(reply_id):
    """软删除回复"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    reply = ForumReply.query.get_or_404(reply_id)
    
    if not check_course_access(user, reply.post.course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    if not can_modify_reply(user, reply):
        return jsonify({'error': 'No permission to delete this reply'}), 403
    
    # Soft delete: replace content with deletion message based on user role
    if user.role == 'teacher':
        reply.content = 'The reply is deleted by the teacher'
    else:
        reply.content = 'The reply is deleted by owner'
    reply.updated_at = datetime.utcnow()
    
    # Note: We preserve the reply count to maintain thread structure
    # post.reply_count remains unchanged
    
    db.session.commit()
    
    return jsonify({'message': 'Reply deleted successfully'})

@forum_bp.route('/<int:course_id>/notifications', methods=['GET'])
def get_forum_notifications(course_id):
    """检查是否有未读论坛内容"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    if not check_course_access(user, course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    # 获取用户的最后阅读时间
    read_record = UserForumRead.query.filter_by(user_id=user.id, course_id=course_id).first()
    last_read_at = read_record.last_read_at if read_record else datetime.min
    
    # 检查是否有新的帖子或回复 (排除用户自己的内容)
    has_new_posts = ForumPost.query.filter(
        ForumPost.course_id == course_id,
        ForumPost.created_at > last_read_at,
        ForumPost.user_id != user.id  # 排除用户自己的帖子
    ).count() > 0
    
    has_new_replies = ForumReply.query.join(ForumPost).filter(
        ForumPost.course_id == course_id,
        ForumReply.created_at > last_read_at,
        ForumReply.user_id != user.id  # 排除用户自己的回复
    ).count() > 0
    
    return jsonify({
        'has_unread': has_new_posts or has_new_replies,
        'last_read_at': last_read_at.isoformat() if last_read_at != datetime.min else None
    })

@forum_bp.route('/<int:course_id>/mark-read', methods=['POST'])
def mark_forum_read(course_id):
    """标记论坛为已读"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    if not check_course_access(user, course_id):
        return jsonify({'error': 'No permission to access this course forum'}), 403
    
    # 更新或创建阅读记录
    read_record = UserForumRead.query.filter_by(user_id=user.id, course_id=course_id).first()
    if read_record:
        read_record.last_read_at = datetime.utcnow()
    else:
        read_record = UserForumRead(
            user_id=user.id,
            course_id=course_id,
            last_read_at=datetime.utcnow()
        )
        db.session.add(read_record)
    
    db.session.commit()
    
    return jsonify({'message': 'Forum marked as read'})
