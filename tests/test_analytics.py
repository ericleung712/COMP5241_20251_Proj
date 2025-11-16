import pytest
from src.models.user import User
from src.models.course import Course
from src.models.activity import Activity
from src.models.response import ActivityResponse
from src.database import db


@pytest.fixture
def teacher_user(app):
    """Create a teacher user."""
    with app.app_context():
        teacher = User(
            username='test_teacher',
            email='test_teacher@example.com',
            full_name='Test Teacher',
            role='teacher'
        )
        teacher.set_password('password123')
        db.session.add(teacher)
        db.session.commit()
        return teacher.id


@pytest.fixture
def teacher_client(app, client, teacher_user):
    """Create authenticated teacher client."""
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = teacher_user
        return client


@pytest.fixture
def student_user(app):
    """Create a student user."""
    with app.app_context():
        student = User(
            username='test_student',
            email='test_student@example.com',
            full_name='Test Student',
            role='student'
        )
        student.set_password('password123')
        db.session.add(student)
        db.session.commit()
        return student.id


@pytest.fixture
def student_client(app, client, student_user):
    """Create authenticated student client."""
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = student_user
        return client


@pytest.fixture
def teacher_test_data(app, teacher_user, student_user):
    """Create test data for teacher analytics."""
    with app.app_context():
        teacher_id = teacher_user
        student_id = student_user

        # Create courses for the teacher
        course1 = Course(
            course_name='Teacher Course 1',
            course_code='TCOURSE1',
            description='Test course 1 for teacher',
            teacher_id=teacher_id,
            semester='Fall 2025',
            academic_year='2025-26'
        )
        course2 = Course(
            course_name='Teacher Course 2',
            course_code='TCOURSE2',
            description='Test course 2 for teacher',
            teacher_id=teacher_id,
            semester='Fall 2025',
            academic_year='2025-26'
        )

        # Create a course for another teacher (should not be visible)
        other_teacher = User(
            username='other_teacher',
            email='other_teacher@example.com',
            full_name='Other Teacher',
            role='teacher'
        )
        other_teacher.set_password('password123')
        db.session.add(other_teacher)
        db.session.commit()

        other_course = Course(
            course_name='Other Teacher Course',
            course_code='OTCOURSE',
            description='Course from other teacher',
            teacher_id=other_teacher.id,
            semester='Fall 2025',
            academic_year='2025-26'
        )

        db.session.add_all([course1, course2, other_course])
        db.session.commit()

        # Enroll student in teacher's courses
        course1.students.append(User.query.get(student_id))
        course2.students.append(User.query.get(student_id))
        db.session.commit()

        # Create activities
        activity1 = Activity(
            title='Quiz Activity 1',
            description='Test quiz activity 1',
            activity_type='quiz',
            course_id=course1.id,
            creator_id=teacher_id,
            status='active'
        )
        activity2 = Activity(
            title='Poll Activity 1',
            description='Test poll activity 1',
            activity_type='poll',
            course_id=course1.id,
            creator_id=teacher_id,
            status='active'
        )
        activity3 = Activity(
            title='Quiz Activity 2',
            description='Test quiz activity 2',
            activity_type='quiz',
            course_id=course2.id,
            creator_id=teacher_id,
            status='active'
        )
        db.session.add_all([activity1, activity2, activity3])
        db.session.commit()

        # Create responses with scores
        response1 = ActivityResponse(
            activity_id=activity1.id,
            student_id=student_id,
            score=85.0,
            time_spent_seconds=300,
            response_data='{"answers": [{"option_index": 0, "is_correct": true}]}'
        )
        response2 = ActivityResponse(
            activity_id=activity3.id,
            student_id=student_id,
            score=92.0,
            time_spent_seconds=250,
            response_data='{"answers": [{"option_index": 1, "is_correct": true}]}'
        )
        db.session.add_all([response1, response2])
        db.session.commit()

        return {
            'teacher_id': teacher_id,
            'student_id': student_id,
            'course1_id': course1.id,
            'course2_id': course2.id,
            'other_course_id': other_course.id,
            'activity1_id': activity1.id,
            'activity2_id': activity2.id,
            'activity3_id': activity3.id
        }


def test_teacher_system_overview_requires_auth(client):
    """Test that teacher system overview requires authentication."""
    response = client.get('/api/analytics/teacher/system-overview')
    assert response.status_code == 401


def test_teacher_system_overview_requires_teacher_role(student_client):
    """Test that teacher system overview requires teacher role."""
    response = student_client.get('/api/analytics/teacher/system-overview')
    assert response.status_code == 403


def test_teacher_system_overview_with_data(teacher_client, teacher_test_data):
    """Test teacher system overview endpoint with test data."""
    response = teacher_client.get('/api/analytics/teacher/system-overview')
    assert response.status_code == 200

    data = response.get_json()
    assert 'system_aggregates' in data
    assert 'course_breakdown' in data
    assert 'date_range' in data

    # Check date range
    date_range = data['date_range']
    assert 'start_date' in date_range
    assert 'end_date' in date_range

    # Check system aggregates
    aggregates = data['system_aggregates']
    assert 'avg_completion_rate' in aggregates
    assert 'total_time_spent_seconds' in aggregates
    assert 'avg_quiz_score' in aggregates
    assert 'total_courses_analyzed' in aggregates

    # Should only show teacher's courses (2 courses, not 3 including other teacher's course)
    breakdown = data['course_breakdown']
    assert len(breakdown) == 2  # Only teacher's courses

    for course in breakdown:
        assert 'course_id' in course
        assert 'course_code' in course
        assert 'course_name' in course
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

        # Ensure only teacher's courses are included
        assert course['course_code'] in ['TCOURSE1', 'TCOURSE2']


def test_teacher_system_overview_empty_courses(teacher_client):
    """Test teacher system overview when teacher has no courses."""
    response = teacher_client.get('/api/analytics/teacher/system-overview')
    assert response.status_code == 200

    data = response.get_json()
    assert data['system_aggregates']['total_courses_analyzed'] == 0
    assert len(data['course_breakdown']) == 0


def test_teacher_system_overview_with_date_range(teacher_client, teacher_test_data):
    """Test teacher system overview endpoint with date range parameters."""
    from datetime import datetime

    # Test with specific date range
    start_date = datetime(2024, 1, 1).isoformat()
    end_date = datetime(2025, 12, 31).isoformat()

    response = teacher_client.get(f'/api/analytics/teacher/system-overview?start_date={start_date}&end_date={end_date}')
    assert response.status_code == 200

    data = response.get_json()
    assert 'system_aggregates' in data
    assert 'course_breakdown' in data
    assert 'date_range' in data

    # Check that date range is returned correctly
    date_range = data['date_range']
    assert date_range['start_date'] == start_date
    assert date_range['end_date'] == end_date


def test_teacher_system_overview_invalid_date_range(teacher_client):
    """Test teacher system overview with invalid date range."""
    response = teacher_client.get('/api/analytics/teacher/system-overview?start_date=2025-12-31&end_date=2024-01-01')
    assert response.status_code == 400

    data = response.get_json()
    assert 'error' in data
    assert '开始日期不能晚于结束日期' in data['error']


def test_teacher_dashboard_data(teacher_client, teacher_test_data):
    """Test teacher dashboard data endpoint."""
    response = teacher_client.get('/api/analytics/dashboard')
    assert response.status_code == 200

    data = response.get_json()
    assert 'role' in data
    assert data['role'] == 'teacher'
    assert 'stats' in data
    assert 'recent_activities' in data

    stats = data['stats']
    assert 'total_courses' in stats
    assert 'total_activities' in stats
    assert 'active_activities' in stats
    assert 'completed_activities' in stats

    # Should show teacher's data
    assert stats['total_courses'] == 2  # Two courses created by teacher
    assert stats['total_activities'] == 3  # Three activities created by teacher


def test_student_dashboard_data(student_client):
    """Test student dashboard data endpoint."""
    response = student_client.get('/api/analytics/dashboard')
    assert response.status_code == 200

    data = response.get_json()
    assert 'role' in data
    assert data['role'] == 'student'
    assert 'stats' in data
    assert 'recent_responses' in data

    stats = data['stats']
    assert 'total_courses' in stats
    assert 'total_participations' in stats
    assert 'avg_score' in stats


def test_student_dashboard_data_with_responses(student_client, teacher_test_data):
    """Test student dashboard data with responses to verify avg_score calculation."""
    # Use the student from teacher_test_data who has responses with scores 85.0 and 92.0
    # Average should be (85.0 + 92.0) / 2 = 88.5
    with student_client:
        with student_client.session_transaction() as sess:
            sess['user_id'] = teacher_test_data['student_id']
        
        response = student_client.get('/api/analytics/dashboard')
        assert response.status_code == 200

        data = response.get_json()
        stats = data['stats']
        assert 'avg_score' in stats
        assert stats['avg_score'] == 88.5  # (85.0 + 92.0) / 2


@pytest.fixture
def admin_client(app, client, admin_user):
    """Create authenticated admin client."""
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user
        return client


@pytest.fixture
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        admin = User(
            username='test_admin',
            email='test_admin@example.com',
            full_name='Test Admin',
            role='admin'
        )
        admin.set_password('password123')
        db.session.add(admin)
        db.session.commit()
        return admin.id


def test_admin_dashboard_data(admin_client):
    """Test admin dashboard data endpoint."""
    response = admin_client.get('/api/analytics/dashboard')
    assert response.status_code == 200

    data = response.get_json()
    assert 'role' in data
    assert data['role'] == 'admin'
    assert 'stats' in data
    assert 'role_stats' in data
    assert 'recent_users' in data

    stats = data['stats']
    assert 'total_users' in stats
    assert 'total_courses' in stats
    assert 'total_activities' in stats
    assert 'total_responses' in stats
    assert 'active_users' in stats
    assert 'ai_activities' in stats


def test_admin_dashboard_ai_activities_count(admin_client, teacher_test_data):
    """Test that admin dashboard correctly counts AI-generated activities."""
    with admin_client:
        # Create some AI-generated activities
        teacher_id = teacher_test_data['teacher_id']
        course_id = teacher_test_data['course1_id']
        
        # Create AI activity
        ai_activity = Activity(
            title='AI Generated Quiz',
            description='Test AI-generated quiz',
            activity_type='quiz',
            course_id=course_id,
            creator_id=teacher_id,
            status='active',
            is_ai_generated=True
        )
        
        # Create regular activity
        regular_activity = Activity(
            title='Regular Quiz',
            description='Test regular quiz',
            activity_type='quiz',
            course_id=course_id,
            creator_id=teacher_id,
            status='active',
            is_ai_generated=False
        )
        
        db.session.add_all([ai_activity, regular_activity])
        db.session.commit()
        
        # Get admin dashboard data
        response = admin_client.get('/api/analytics/dashboard')
        assert response.status_code == 200
        
        data = response.get_json()
        stats = data['stats']
        
        # Should count only AI activities
        assert stats['ai_activities'] == 1