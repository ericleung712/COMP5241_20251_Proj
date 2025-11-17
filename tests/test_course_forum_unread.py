import pytest
from src.models.forum import ForumPost, ForumReply, UserForumRead
from src.models.course import Course
from src.models.user import User
from src.database import db
from datetime import datetime, timedelta


class TestCourseForumUnread:
    """测试课程论坛未读状态"""

    def test_forum_unread_excludes_own_content(self, app, test_users, test_course):
        """测试论坛未读状态不包括用户自己的内容"""
        with app.app_context():
            # 标记学生1为已读
            read_record = UserForumRead.query.filter_by(
                user_id=test_users['student1_id'],
                course_id=test_course
            ).first()
            if read_record:
                read_record.last_read_at = datetime.utcnow()
            else:
                read_record = UserForumRead(
                    user_id=test_users['student1_id'],
                    course_id=test_course,
                    last_read_at=datetime.utcnow()
                )
                db.session.add(read_record)
            db.session.commit()

            # 学生1创建自己的帖子
            post = ForumPost(
                course_id=test_course,
                user_id=test_users['student1_id'],
                title='My Own Post',
                content='Content from student1'
            )
            db.session.add(post)
            db.session.commit()

            # 导入check_forum_unread函数进行测试
            from src.routes.course import check_forum_unread

            # 应该没有未读通知（因为是自己的帖子）
            assert check_forum_unread(test_users['student1_id'], test_course) == False

            # 教师创建新内容
            teacher_post = ForumPost(
                course_id=test_course,
                user_id=test_users['teacher_id'],
                title='Teacher Post',
                content='Content from teacher'
            )
            db.session.add(teacher_post)
            db.session.commit()

            # 现在应该有未读通知（来自其他用户的内容）
            assert check_forum_unread(test_users['student1_id'], test_course) == True