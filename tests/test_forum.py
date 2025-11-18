import pytest
from src.models.forum import ForumPost, ForumReply, UserForumRead
from src.models.course import Course
from src.models.user import User
from src.database import db
from datetime import datetime, timedelta


class TestForumModels:
    """测试论坛模型"""

    def test_forum_post_creation(self, app, test_users, test_course):
        with app.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Test Post',
                content='This is a test post content'
            )
            db.session.add(post)
            db.session.commit()

            assert post.id is not None
            assert post.title == 'Test Post'
            assert post.content == 'This is a test post content'
            assert post.is_pinned == False
            assert post.reply_count == 0
            assert post.user.full_name == 'Test Teacher'

    def test_forum_reply_creation(self, app, test_users, test_course):
        with app.app_context():
            # 创建帖子
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Test Post',
                content='This is a test post content'
            )
            db.session.add(post)
            db.session.commit()

            # 创建回复
            reply = ForumReply(
                post_id=post.id,
                user_id=test_users['student1_id'],
                content='This is a test reply'
            )
            db.session.add(reply)
            db.session.commit()

            assert reply.id is not None
            assert reply.content == 'This is a test reply'
            assert reply.parent_reply_id is None
            assert reply.user.full_name == 'Test Student 1'
            assert reply.post.title == 'Test Post'

    def test_threaded_replies(self, app, test_users, test_course):
        with app.app_context():
            # 创建帖子
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Test Post',
                content='This is a test post content'
            )
            db.session.add(post)
            db.session.commit()

            # 创建顶级回复
            parent_reply = ForumReply(
                post_id=post.id,
                user_id=test_users['student1_id'],
                content='Parent reply'
            )
            db.session.add(parent_reply)
            db.session.commit()

            # 创建子回复
            child_reply = ForumReply(
                post_id=post.id,
                user_id=test_users['student2_id'],
                content='Child reply',
                parent_reply_id=parent_reply.id
            )
            db.session.add(child_reply)
            db.session.commit()

            assert child_reply.parent_reply_id == parent_reply.id
            assert parent_reply.child_replies == [child_reply]

    def test_user_forum_read(self, app, test_users, test_course):
        with app.app_context():
            read_record = UserForumRead(
                user_id=test_users['student1_id'],
                course_id=test_course,
                last_read_at=datetime.utcnow()
            )
            db.session.add(read_record)
            db.session.commit()

            assert read_record.id is not None
            assert read_record.user_id == test_users['student1_id']
            assert read_record.course_id == test_course

            # 测试唯一约束
            duplicate = UserForumRead(
                user_id=test_users['student1_id'],
                course_id=test_course,
                last_read_at=datetime.utcnow()
            )
            db.session.add(duplicate)
            with pytest.raises(Exception):  # 唯一约束违反
                db.session.commit()


class TestForumRoutes:
    """测试论坛路由"""

    def test_get_forum_posts_unauthorized(self, client):
        """测试未登录用户访问论坛"""
        response = client.get('/api/forum/1')
        assert response.status_code == 401

    def test_get_forum_posts_no_access(self, auth_client, test_users):
        """测试无权限用户访问论坛"""
        # 创建一个不属于任何人的课程 - 使用另一个教师ID
        with auth_client['teacher'].application.app_context():
            # Create another teacher user for this test
            other_teacher = User(
                username='other_teacher',
                email='other@example.com',
                full_name='Other Teacher',
                role='teacher'
            )
            other_teacher.set_password('password123')
            db.session.add(other_teacher)
            db.session.commit()
            
            course = Course(
                course_name='Private Course',
                course_code='PRIV101',
                teacher_id=other_teacher.id,  # Different teacher
                semester='Fall 2025',
                academic_year='2025-26'
            )
            db.session.add(course)
            db.session.commit()
            course_id = course.id

        response = auth_client['student1'].get(f'/api/forum/{course_id}')
        assert response.status_code == 403

    def test_create_forum_post(self, auth_client, test_course):
        """测试创建帖子"""
        data = {
            'title': 'Test Forum Post',
            'content': 'This is the content of the forum post.'
        }
        response = auth_client['teacher'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201

        response_data = response.get_json()
        assert 'post' in response_data
        assert response_data['post']['title'] == 'Test Forum Post'
        assert response_data['post']['user_name'] == 'Test Teacher'

    def test_create_forum_post_student(self, auth_client, test_course):
        """测试学生创建帖子"""
        data = {
            'title': 'Student Post',
            'content': 'Posted by a student.'
        }
        response = auth_client['student1'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201

        response_data = response.get_json()
        assert response_data['post']['user_name'] == 'Test Student 1'

    def test_create_forum_post_invalid_data(self, auth_client, test_course):
        """测试创建帖子时提供无效数据"""
        # 缺少标题
        data = {'content': 'Content only'}
        response = auth_client['teacher'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 400

        # 空标题
        data = {'title': '', 'content': 'Content'}
        response = auth_client['teacher'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 400

    def test_get_forum_posts(self, auth_client, test_course, test_users):
        """测试获取论坛帖子"""
        # 先创建一些帖子
        with auth_client['teacher'].application.app_context():
            post1 = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Post 1',
                content='Content 1'
            )
            post2 = ForumPost(
                course_id=test_course,
                user_id=test_users['student1_id'],  # student1
                title='Post 2',
                content='Content 2'
            )
            db.session.add_all([post1, post2])
            db.session.commit()

        response = auth_client['student1'].get(f'/api/forum/{test_course}')
        assert response.status_code == 200

        data = response.get_json()
        assert 'posts' in data
        assert len(data['posts']) >= 2
        assert data['posts'][0]['title'] in ['Post 1', 'Post 2']

    def test_update_forum_post(self, auth_client, test_course, test_users):
        """测试更新帖子"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Original Title',
                content='Original content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 更新帖子
        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        response = auth_client['teacher'].put(f'/api/forum/post/{post_id}', json=update_data)
        assert response.status_code == 200

        # 验证更新
        with auth_client['teacher'].application.app_context():
            updated_post = ForumPost.query.get(post_id)
            assert updated_post.title == 'Updated Title'
            assert updated_post.content == 'Updated content'

    def test_update_forum_post_no_permission(self, auth_client, test_course, test_users):
        """测试无权限更新帖子"""
        # 创建帖子（教师创建）
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Teacher Post',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 学生尝试更新
        update_data = {'title': 'Hacked Title'}
        response = auth_client['student1'].put(f'/api/forum/post/{post_id}', json=update_data)
        assert response.status_code == 403

    def test_delete_forum_post(self, auth_client, test_course, test_users):
        """测试软删除帖子"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Post to Delete',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 删除帖子
        response = auth_client['teacher'].delete(f'/api/forum/post/{post_id}')
        assert response.status_code == 200

        # 验证软删除 - 帖子仍然存在但内容被替换
        with auth_client['teacher'].application.app_context():
            deleted_post = ForumPost.query.get(post_id)
            assert deleted_post is not None
            assert deleted_post.content == 'The post is deleted by the teacher'
            assert deleted_post.title == 'Post to Delete'  # 标题保持不变

    def test_create_forum_reply(self, auth_client, test_course, test_users):
        """测试创建回复"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Post for Reply',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 创建回复
        reply_data = {'content': 'This is a reply'}
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201

        response_data = response.get_json()
        assert 'reply' in response_data
        assert response_data['reply']['content'] == 'This is a reply'

        # 验证回复计数更新
        with auth_client['student1'].application.app_context():
            updated_post = ForumPost.query.get(post_id)
            assert updated_post.reply_count == 1

    def test_threaded_replies_api(self, auth_client, test_course, test_users):
        """测试线程化回复API"""
        # 创建帖子和回复
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Threaded Post',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()

            parent_reply = ForumReply(
                post_id=post.id,
                user_id=test_users['student1_id'],  # student1
                content='Parent reply'
            )
            db.session.add(parent_reply)
            db.session.commit()

            child_reply = ForumReply(
                post_id=post.id,
                user_id=test_users['student2_id'],  # student2
                content='Child reply',
                parent_reply_id=parent_reply.id
            )
            db.session.add(child_reply)
            db.session.commit()

            post_id = post.id

        # 获取回复
        response = auth_client['student1'].get(f'/api/forum/post/{post_id}/replies')
        assert response.status_code == 200

        data = response.get_json()
        assert 'replies' in data
        assert len(data['replies']) == 1  # 一个顶级回复
        assert 'child_replies' in data['replies'][0]
        assert len(data['replies'][0]['child_replies']) == 1

    def test_create_reply_to_reply(self, auth_client, test_course, test_users):
        """测试回复其他回复的功能"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Post for Nested Reply',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 创建顶级回复
        reply_data = {'content': 'Parent reply'}
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201
        parent_reply_data = response.get_json()['reply']
        parent_reply_id = parent_reply_data['id']

        # 回复上面的回复
        child_reply_data = {
            'content': 'Reply to parent reply',
            'parent_reply_id': parent_reply_id
        }
        response = auth_client['student2'].post(f'/api/forum/post/{post_id}/reply', json=child_reply_data)
        assert response.status_code == 201

        child_reply_data_response = response.get_json()['reply']
        assert child_reply_data_response['content'] == 'Reply to parent reply'
        assert child_reply_data_response['parent_reply_id'] == parent_reply_id

        # 验证线程化结构
        response = auth_client['student1'].get(f'/api/forum/post/{post_id}/replies')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['replies']) == 1  # 一个顶级回复
        parent_reply = data['replies'][0]
        assert len(parent_reply['child_replies']) == 1
        assert parent_reply['child_replies'][0]['content'] == 'Reply to parent reply'

    def test_create_reply_to_reply_invalid_parent(self, auth_client, test_course, test_users):
        """测试回复不存在的父回复"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Post for Invalid Parent',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 尝试回复不存在的父回复
        reply_data = {
            'content': 'Reply to non-existent parent',
            'parent_reply_id': 99999  # 不存在的回复ID
        }
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 400
        assert 'Parent reply does not exist' in response.get_json()['error']

    def test_create_reply_to_reply_wrong_post(self, auth_client, test_course, test_users):
        """测试回复其他帖子的回复"""
        # 创建两个帖子
        with auth_client['teacher'].application.app_context():
            post1 = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Post 1',
                content='Content 1'
            )
            post2 = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Post 2',
                content='Content 2'
            )
            db.session.add_all([post1, post2])
            db.session.commit()

            # 在post1上创建回复
            reply = ForumReply(
                post_id=post1.id,
                user_id=test_users['student1_id'],
                content='Reply on post 1'
            )
            db.session.add(reply)
            db.session.commit()
            reply_id = reply.id
            post2_id = post2.id

        # 尝试在post2上回复post1的回复
        reply_data = {
            'content': 'Reply to wrong post reply',
            'parent_reply_id': reply_id
        }
        response = auth_client['student1'].post(f'/api/forum/post/{post2_id}/reply', json=reply_data)
        assert response.status_code == 400
        assert 'Parent reply does not exist' in response.get_json()['error']

    def test_forum_search(self, auth_client, test_course, test_users):
        """测试论坛搜索功能"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post1 = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Python Programming',
                content='Learn Python basics'
            )
            post2 = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='JavaScript Tips',
                content='Advanced JS techniques'
            )
            db.session.add_all([post1, post2])
            db.session.commit()

        # 搜索标题
        response = auth_client['student1'].get(f'/api/forum/{test_course}?q=Python')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['posts']) == 1
        assert data['posts'][0]['title'] == 'Python Programming'

        # 搜索内容
        response = auth_client['student1'].get(f'/api/forum/{test_course}?q=techniques')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['posts']) == 1
        assert data['posts'][0]['title'] == 'JavaScript Tips'

    def test_forum_notifications(self, auth_client, test_course, test_users):
        """测试论坛通知功能"""
        # 初始状态应该没有未读
        response = auth_client['student1'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == False

        # 创建新帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='New Post',
                content='New content'
            )
            db.session.add(post)
            db.session.commit()

        # 现在应该有未读
        response = auth_client['student1'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == True

        # 标记为已读
        response = auth_client['student1'].post(f'/api/forum/{test_course}/mark-read')
        assert response.status_code == 200

        # 现在应该没有未读
        response = auth_client['student1'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == False

    def test_forum_notifications_exclude_own_content(self, auth_client, test_course, test_users):
        """测试论坛通知不包括用户自己的内容"""
        # 标记为已读以确保干净的状态
        response = auth_client['student1'].post(f'/api/forum/{test_course}/mark-read')
        assert response.status_code == 200

        # 学生1创建自己的帖子
        data = {
            'title': 'My Own Post',
            'content': 'Content from student1'
        }
        response = auth_client['student1'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201

        # 应该没有未读通知（因为是自己的帖子）
        response = auth_client['student1'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == False

        # 学生1创建自己的回复
        with auth_client['student1'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['student1_id'],  # student1
                title='Post for Reply',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        reply_data = {'content': 'My own reply'}
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201

        # 仍然应该没有未读通知（因为是自己的回复）
        response = auth_client['student1'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == False

        # 现在教师创建新内容
        with auth_client['teacher'].application.app_context():
            teacher_post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Teacher Post',
                content='Content from teacher'
            )
            db.session.add(teacher_post)
            db.session.commit()

        # 现在应该有未读通知（来自其他用户的内容）
        response = auth_client['student1'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == True

    def test_reply_depth_limit(self, auth_client, test_course, test_users):
        """测试回复深度限制为3层"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Post for Depth Test',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 创建第1层回复
        reply_data = {'content': 'Level 1 reply'}
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201
        level1_reply = response.get_json()['reply']
        print(f"Level 1 reply created: {level1_reply['id']}")

        # 创建第2层回复
        reply_data = {
            'content': 'Level 2 reply',
            'parent_reply_id': level1_reply['id']
        }
        response = auth_client['student2'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201
        level2_reply = response.get_json()['reply']
        print(f"Level 2 reply created: {level2_reply['id']}, parent: {level2_reply['parent_reply_id']}")

        # 创建第3层回复
        reply_data = {
            'content': 'Level 3 reply',
            'parent_reply_id': level2_reply['id']
        }
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201
        level3_reply = response.get_json()['reply']
        print(f"Level 3 reply created: {level3_reply['id']}, parent: {level3_reply['parent_reply_id']}")

        # 尝试创建第4层回复（应该失败）
        reply_data = {
            'content': 'Level 4 reply (should fail)',
            'parent_reply_id': level3_reply['id']
        }
        response = auth_client['student2'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        print(f"Level 4 reply response: {response.status_code}")
        if response.status_code != 400:
            print(f"Response data: {response.get_json()}")
        assert response.status_code == 400
        assert 'Maximum nesting depth (3 levels) exceeded' in response.get_json()['error']

    def test_forum_pagination(self, auth_client, test_course, test_users):
        """测试分页功能"""
        # 创建多个帖子
        with auth_client['teacher'].application.app_context():
            posts = []
            for i in range(5):
                post = ForumPost(
                    course_id=test_course,
                    user_id=test_users['teacher_id'],
                    title=f'Post {i+1}',
                    content=f'Content {i+1}'
                )
                posts.append(post)
            db.session.add_all(posts)
            db.session.commit()

        # 获取第一页（每页2个）
        response = auth_client['student1'].get(f'/api/forum/{test_course}?per_page=2&page=1')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['posts']) == 2
        assert data['total'] == 5
        assert data['pages'] == 3
        assert data['has_next'] == True
        assert data['has_prev'] == False

        # 获取第二页
        response = auth_client['student1'].get(f'/api/forum/{test_course}?per_page=2&page=2')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['posts']) == 2
        assert data['has_next'] == True
        assert data['has_prev'] == True

    def test_teacher_forum_access_and_unread_status(self, auth_client, test_course):
        """测试教师可以访问论坛功能且未读状态正确计算"""
        # 教师应该可以访问自己课程的论坛
        response = auth_client['teacher'].get(f'/api/forum/{test_course}')
        assert response.status_code == 200

        # 教师应该可以创建帖子
        data = {
            'title': 'Teacher Forum Post',
            'content': 'This is a post created by teacher.'
        }
        response = auth_client['teacher'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201

        response_data = response.get_json()
        assert response_data['post']['user_name'] == 'Test Teacher'

        # 测试教师的论坛未读状态
        # 首先标记教师为已读
        response = auth_client['teacher'].post(f'/api/forum/{test_course}/mark-read')
        assert response.status_code == 200

        # 验证未读状态为False
        response = auth_client['teacher'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == False

        # 学生创建新帖子
        data = {
            'title': 'Student Post for Teacher Test',
            'content': 'Content from student'
        }
        response = auth_client['student1'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201

        # 教师现在应该有未读通知
        response = auth_client['teacher'].get(f'/api/forum/{test_course}/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_unread'] == True

        # 测试教师的课程列表包含正确的forum_unread状态
        response = auth_client['teacher'].get('/api/courses/')
        assert response.status_code == 200
        courses_data = response.get_json()

        # 找到测试课程
        test_course_data = None
        for course in courses_data:
            if course['id'] == test_course:
                test_course_data = course
                break

        assert test_course_data is not None
        assert 'forum_unread' in test_course_data
        assert test_course_data['forum_unread'] == True

        # 教师标记为已读后，未读状态应该变为False
        response = auth_client['teacher'].post(f'/api/forum/{test_course}/mark-read')
        assert response.status_code == 200

        response = auth_client['teacher'].get('/api/courses/')
        assert response.status_code == 200
        courses_data = response.get_json()

        test_course_data = None
        for course in courses_data:
            if course['id'] == test_course:
                test_course_data = course
                break

        assert test_course_data is not None
        assert test_course_data['forum_unread'] == False

    def test_teacher_forum_reply_functionality(self, auth_client, test_course, test_users):
        """测试教师的论坛回复功能"""
        # 创建帖子
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Post for Teacher Reply Test',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        # 教师创建回复
        reply_data = {'content': 'Teacher reply to post'}
        response = auth_client['teacher'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201

        response_data = response.get_json()
        assert response_data['reply']['content'] == 'Teacher reply to post'
        assert response_data['reply']['user_name'] == 'Test Teacher'

        # 教师回复其他回复（线程化回复）
        reply_data = {
            'content': 'Teacher reply to reply',
            'parent_reply_id': response_data['reply']['id']
        }
        response = auth_client['teacher'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201

        child_reply_data = response.get_json()['reply']
        assert child_reply_data['content'] == 'Teacher reply to reply'
        assert child_reply_data['parent_reply_id'] == response_data['reply']['id']

        # 获取回复列表，验证线程化结构
        response = auth_client['teacher'].get(f'/api/forum/post/{post_id}/replies')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['replies']) == 1  # 一个顶级回复
        parent_reply = data['replies'][0]
        assert len(parent_reply['child_replies']) == 1
        assert parent_reply['child_replies'][0]['content'] == 'Teacher reply to reply'

    def test_soft_delete_forum_post_by_owner(self, auth_client, test_course):
        """Test that post owner can soft delete their own post"""
        # Create a post as student1
        data = {'title': 'Post to Delete', 'content': 'Original content'}
        response = auth_client['student1'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201
        post_data = response.get_json()['post']
        post_id = post_data['id']
        
        # Delete the post as the owner
        response = auth_client['student1'].delete(f'/api/forum/post/{post_id}')
        assert response.status_code == 200
        
        # Verify the post content is replaced
        response = auth_client['student1'].get(f'/api/forum/{test_course}')
        assert response.status_code == 200
        posts = response.get_json()['posts']
        deleted_post = next(p for p in posts if p['id'] == post_id)
        assert deleted_post['content'] == 'The post is deleted by owner'
        assert deleted_post['title'] == 'Post to Delete'  # Title remains unchanged

    def test_soft_delete_forum_reply_by_owner(self, auth_client, test_course, test_users):
        """Test that reply owner can soft delete their own reply"""
        # Create a post first
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Post for Reply Delete',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id
        
        # Create a reply as student1
        reply_data = {'content': 'Original reply content'}
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201
        reply_data_response = response.get_json()['reply']
        reply_id = reply_data_response['id']
        
        # Delete the reply as the owner
        response = auth_client['student1'].delete(f'/api/forum/reply/{reply_id}')
        assert response.status_code == 200
        
        # Verify the reply content is replaced
        response = auth_client['student1'].get(f'/api/forum/post/{post_id}/replies')
        assert response.status_code == 200
        replies = response.get_json()['replies']
        deleted_reply = self._find_reply_in_threaded_structure(replies, reply_id)
        assert deleted_reply['content'] == 'The reply is deleted by owner'

    def test_soft_delete_forum_post_by_teacher(self, auth_client, test_course):
        """Test that teacher can soft delete any post in their course"""
        # Create a post as student1
        data = {'title': 'Student Post', 'content': 'Student content'}
        response = auth_client['student1'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201
        post_data = response.get_json()['post']
        post_id = post_data['id']
        
        # Delete the post as teacher
        response = auth_client['teacher'].delete(f'/api/forum/post/{post_id}')
        assert response.status_code == 200
        
        # Verify the post content is replaced
        response = auth_client['teacher'].get(f'/api/forum/{test_course}')
        assert response.status_code == 200
        posts = response.get_json()['posts']
        deleted_post = next(p for p in posts if p['id'] == post_id)
        assert deleted_post['content'] == 'The post is deleted by the teacher'

    def test_soft_delete_forum_reply_by_teacher(self, auth_client, test_course, test_users):
        """Test that teacher can soft delete any reply in their course"""
        # Create a post and reply as student1
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Post for Teacher Delete',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id
            
            reply = ForumReply(
                post_id=post_id,
                user_id=test_users['student1_id'],  # student1
                content='Student reply'
            )
            db.session.add(reply)
            db.session.commit()
            reply_id = reply.id
        
        # Delete the reply as teacher
        response = auth_client['teacher'].delete(f'/api/forum/reply/{reply_id}')
        assert response.status_code == 200
        
        # Verify the reply content is replaced
        response = auth_client['teacher'].get(f'/api/forum/post/{post_id}/replies')
        assert response.status_code == 200
        replies = response.get_json()['replies']
        deleted_reply = self._find_reply_in_threaded_structure(replies, reply_id)
        assert deleted_reply['content'] == 'The reply is deleted by the teacher'

    def test_soft_delete_forum_post_no_permission(self, auth_client, test_course):
        """Test that users cannot soft delete posts they don't own"""
        # Create a post as student1
        data = {'title': 'Student Post', 'content': 'Student content'}
        response = auth_client['student1'].post(f'/api/forum/{test_course}', json=data)
        assert response.status_code == 201
        post_data = response.get_json()['post']
        post_id = post_data['id']
        
        # Try to delete as student2
        response = auth_client['student2'].delete(f'/api/forum/post/{post_id}')
        assert response.status_code == 403
        assert 'No permission to delete this post' in response.get_json()['error']
        
        # Verify content is unchanged
        response = auth_client['student1'].get(f'/api/forum/{test_course}')
        assert response.status_code == 200
        posts = response.get_json()['posts']
        post = next(p for p in posts if p['id'] == post_id)
        assert post['content'] == 'Student content'

    def test_soft_delete_forum_reply_no_permission(self, auth_client, test_course, test_users):
        """Test that users cannot soft delete replies they don't own"""
        # Create a post and reply as student1
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Post for Permission Test',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id
            
            reply = ForumReply(
                post_id=post_id,
                user_id=test_users['student1_id'],  # student1
                content='Student reply'
            )
            db.session.add(reply)
            db.session.commit()
            reply_id = reply.id
        
        # Try to delete as student2
        response = auth_client['student2'].delete(f'/api/forum/reply/{reply_id}')
        assert response.status_code == 403
        assert 'No permission to delete this reply' in response.get_json()['error']
        
        # Verify content is unchanged
        response = auth_client['student1'].get(f'/api/forum/post/{post_id}/replies')
        assert response.status_code == 200
        replies = response.get_json()['replies']
        reply = self._find_reply_in_threaded_structure(replies, reply_id)
        assert reply['content'] == 'Student reply'

    def test_soft_delete_preserves_reply_count(self, auth_client, test_course, test_users):
        """Test that soft deleting a reply preserves the post's reply count"""
        # Create a post first
        with auth_client['teacher'].application.app_context():
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],  # teacher
                title='Post for Count Test',
                content='Content'
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id
        
        # Create a reply through the API (this updates reply_count)
        reply_data = {'content': 'Reply content'}
        response = auth_client['student1'].post(f'/api/forum/post/{post_id}/reply', json=reply_data)
        assert response.status_code == 201
        reply_data_response = response.get_json()['reply']
        reply_id = reply_data_response['id']
        
        # Verify initial reply count
        response = auth_client['student1'].get(f'/api/forum/{test_course}')
        assert response.status_code == 200
        posts = response.get_json()['posts']
        post = next(p for p in posts if p['id'] == post_id)
        assert post['reply_count'] == 1
        
        # Soft delete the reply
        response = auth_client['student1'].delete(f'/api/forum/reply/{reply_id}')
        assert response.status_code == 200
        
        # Verify reply count is preserved
        response = auth_client['student1'].get(f'/api/forum/{test_course}')
        assert response.status_code == 200
        posts = response.get_json()['posts']
        post = next(p for p in posts if p['id'] == post_id)
        assert post['reply_count'] == 1  # Count should remain the same

    def _find_reply_in_threaded_structure(self, replies, reply_id):
        """Helper method to find a reply in the threaded structure"""
        for reply in replies:
            if reply['id'] == reply_id:
                return reply
            if 'child_replies' in reply:
                found = self._find_reply_in_threaded_structure(reply['child_replies'], reply_id)
                if found:
                    return found
        return None
