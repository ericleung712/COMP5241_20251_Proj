import pytest
from src.models.user import User
from src.models.course import Course
from src.models.activity import Activity
from src.models.response import ActivityResponse
from src.database import db


@pytest.fixture
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        # Clear existing data first to ensure clean state
        from src.models.user import User
        from src.models.course import Course, course_enrollments
        from src.models.activity import Activity
        from src.models.response import ActivityResponse
        from src.models.analytics import Leaderboard, ActivityAnalytics
        from src.models.document import Document
        from src.models.forum import ForumPost, ForumReply, UserForumRead
        from src.database import db
        
        # Clear in correct order to respect foreign keys
        db.session.query(UserForumRead).delete()
        db.session.query(ForumReply).delete()
        db.session.query(ForumPost).delete()
        db.session.query(ActivityResponse).delete()
        db.session.query(ActivityAnalytics).delete()
        db.session.query(Activity).delete()
        db.session.query(Document).delete()
        db.session.query(Leaderboard).delete()
        db.session.query(course_enrollments).delete()
        db.session.query(Course).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        import uuid
        unique_username = f'test_admin_{uuid.uuid4().hex[:8]}'
        
        admin = User(
            username=unique_username,
            email=f'{unique_username}@example.com',
            full_name='Test Admin',
            role='admin'
        )
        admin.set_password('password123')
        db.session.add(admin)
        db.session.commit()
        return admin.id


@pytest.fixture
def admin_client(app, client, admin_user):
    """Create authenticated admin client."""
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user
        return client


@pytest.fixture
def test_data_for_overview(app, admin_user):
    """Create test data for system overview."""
    with app.app_context():
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        
        # Create teacher
        teacher = User(
            username=f'teacher_overview_{unique_id}',
            email=f'teacher_overview_{unique_id}@example.com',
            full_name='Teacher Overview',
            role='teacher'
        )
        teacher.set_password('password123')
        db.session.add(teacher)
        db.session.commit()

        # Create courses
        course1 = Course(
            course_name='Course 1',
            course_code=f'COURSE1_{unique_id}',
            description='Test course 1',
            teacher_id=teacher.id,
            semester='Fall 2025',
            academic_year='2025-26'
        )
        course2 = Course(
            course_name='Course 2',
            course_code=f'COURSE2_{unique_id}',
            description='Test course 2',
            teacher_id=teacher.id,
            semester='Fall 2025',
            academic_year='2025-26'
        )
        db.session.add_all([course1, course2])
        db.session.commit()

        # Create students
        student1 = User(
            username=f'student_overview1_{unique_id}',
            email=f'student_overview1_{unique_id}@example.com',
            full_name='Student Overview 1',
            role='student'
        )
        student1.set_password('password123')

        student2 = User(
            username=f'student_overview2_{unique_id}',
            email=f'student_overview2_{unique_id}@example.com',
            full_name='Student Overview 2',
            role='student'
        )
        student2.set_password('password123')

        db.session.add_all([student1, student2])
        db.session.commit()

        # Enroll students in courses
        course1.students.append(student1)
        course1.students.append(student2)
        course2.students.append(student1)
        db.session.commit()

        # Create activities
        activity1 = Activity(
            title='Activity 1',
            description='Test activity 1',
            activity_type='quiz',
            course_id=course1.id,
            creator_id=teacher.id,
            status='active'
        )
        activity2 = Activity(
            title='Activity 2',
            description='Test activity 2',
            activity_type='poll',
            course_id=course1.id,
            creator_id=teacher.id,
            status='active'
        )
        activity3 = Activity(
            title='Activity 3',
            description='Test activity 3',
            activity_type='quiz',
            course_id=course2.id,
            creator_id=teacher.id,
            status='active'
        )
        db.session.add_all([activity1, activity2, activity3])
        db.session.commit()

        # Create responses
        response1 = ActivityResponse(
            activity_id=activity1.id,
            student_id=student1.id,
            score=85.0,
            time_spent_seconds=300,
            response_data='{"answers": ["A"]}'
        )
        response2 = ActivityResponse(
            activity_id=activity1.id,
            student_id=student2.id,
            score=90.0,
            time_spent_seconds=250,
            response_data='{"answers": ["A"]}'
        )
        response3 = ActivityResponse(
            activity_id=activity2.id,
            student_id=student1.id,
            score=100.0,
            time_spent_seconds=120,
            response_data='{"answers": ["B"]}'
        )
        response4 = ActivityResponse(
            activity_id=activity3.id,
            student_id=student1.id,
            score=80.0,
            time_spent_seconds=400,
            response_data='{"answers": ["C"]}'
        )
        db.session.add_all([response1, response2, response3, response4])
        db.session.commit()

        return {
            'course1_id': course1.id,
            'course2_id': course2.id,
            'activity1_id': activity1.id,
            'activity2_id': activity2.id,
            'activity3_id': activity3.id,
            'student1_id': student1.id,
            'student2_id': student2.id
        }


def test_system_overview_requires_admin(client):
    """Test that system overview requires admin access."""
    response = client.get('/api/admin/system-overview')
    assert response.status_code == 403


def test_system_overview_with_data(admin_client, test_data_for_overview):
    """Test system overview endpoint with test data."""
    response = admin_client.get('/api/admin/system-overview')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'system_aggregates' in data
    assert 'course_breakdown' in data
    assert 'user_activity' in data
    assert 'date_range' in data
    
    # Check date range
    date_range = data['date_range']
    assert 'start_date' in date_range
    assert 'end_date' in date_range
    
    # Check user activity data
    user_activity = data['user_activity']
    assert isinstance(user_activity, list)
    if len(user_activity) > 0:
        for item in user_activity:
            assert 'month' in item
            assert 'total_users' in item
            assert 'active_users' in item
            assert isinstance(item['total_users'], int)
            assert isinstance(item['active_users'], int)
            assert item['total_users'] >= 0
            assert item['active_users'] >= 0
    
    # Check system aggregates
    aggregates = data['system_aggregates']
    assert 'avg_completion_rate' in aggregates
    assert 'total_time_spent_seconds' in aggregates
    assert 'avg_quiz_score' in aggregates
    assert 'total_courses_analyzed' in aggregates
    
    # Check course breakdown
    breakdown = data['course_breakdown']
    assert len(breakdown) == 2  # Two courses
    
    for course in breakdown:
        assert 'course_id' in course
        assert 'course_code' in course
        assert 'completion_rate' in course
        assert 'total_activities' in course
        assert 'completed_activities' in course
        assert 'total_time_spent_seconds' in course
        assert 'avg_time_per_user_seconds' in course
        assert 'users_with_responses' in course
        assert 'avg_quiz_score' in course
        assert 'quiz_responses' in course
        
        # Validate data types and ranges
        assert isinstance(course['completion_rate'], (int, float))
        assert 0 <= course['completion_rate'] <= 100
        assert course['total_activities'] >= 0
        assert course['completed_activities'] >= 0
        assert course['total_time_spent_seconds'] >= 0
        assert course['avg_time_per_user_seconds'] >= 0
        assert course['users_with_responses'] >= 0
        assert 0 <= course['avg_quiz_score'] <= 100
        assert course['quiz_responses'] >= 0


def test_system_overview_empty_database(admin_client):
    """Test system overview with no courses."""
    response = admin_client.get('/api/admin/system-overview')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['system_aggregates']['total_courses_analyzed'] == 0
    assert len(data['course_breakdown']) == 0


def test_system_overview_with_date_range(admin_client, test_data_for_overview):
    """Test system overview endpoint with date range parameters."""
    from datetime import datetime
    
    # Test with specific date range
    start_date = datetime(2024, 1, 1).isoformat()
    end_date = datetime(2025, 12, 31).isoformat()
    
    response = admin_client.get(f'/api/admin/system-overview?start_date={start_date}&end_date={end_date}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'system_aggregates' in data
    assert 'course_breakdown' in data
    assert 'user_activity' in data
    assert 'date_range' in data
    
    # Check that date range is returned correctly
    date_range = data['date_range']
    assert date_range['start_date'] == start_date
    assert date_range['end_date'] == end_date


def test_system_overview_invalid_date_range(admin_client):
    """Test system overview with invalid date range."""
    response = admin_client.get('/api/admin/system-overview?start_date=2025-12-31&end_date=2024-01-01')
    assert response.status_code == 400
    
    data = response.get_json()
    assert 'error' in data
    assert '开始日期不能晚于结束日期' in data['error']