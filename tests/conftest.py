import pytest
import os
import tempfile
from main import create_app
from src.database import db
from src.models.user import User
from src.models.course import Course, course_enrollments
from src.models.activity import Activity
from src.models.response import ActivityResponse
from flask import session


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Monkey patch os.path.join to return our temporary path when creating database path
    import os.path
    original_join = os.path.join

    def patched_join(*args):
        if len(args) >= 3 and args[-2:] == ('database', 'app.db'):
            # Return temporary database path instead of production database
            return db_path
        return original_join(*args)

    os.path.join = patched_join

    try:
        app = create_app()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'

        # Create the database and tables
        with app.app_context():
            db.create_all()

        yield app
    finally:
        # Restore original os.path.join
        os.path.join = original_join

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_users(app):
    """Create test users."""
    with app.app_context():
        # Clear existing data
        db.session.query(ActivityResponse).delete()
        db.session.query(Activity).delete()
        db.session.query(course_enrollments).delete()
        db.session.query(Course).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create teacher
        teacher = User(
            username='teacher1',
            email='teacher@example.com',
            full_name='Test Teacher',
            role='teacher'
        )
        teacher.set_password('password123')

        # Create students
        student1 = User(
            username='student1',
            email='student1@example.com',
            full_name='Test Student 1',
            role='student'
        )
        student1.set_password('password123')

        student2 = User(
            username='student2',
            email='student2@example.com',
            full_name='Test Student 2',
            role='student'
        )
        student2.set_password('password123')

        db.session.add_all([teacher, student1, student2])
        db.session.commit()

        # Return user IDs instead of objects to avoid session issues
        return {
            'teacher_id': teacher.id,
            'student1_id': student1.id,
            'student2_id': student2.id
        }


@pytest.fixture
def test_course(app, test_users):
    """Create a test course."""
    with app.app_context():
        course = Course(
            course_name='Test Course',
            course_code='TEST101',
            description='A test course for quiz testing',
            teacher_id=test_users['teacher_id'],
            semester='Fall 2025',
            academic_year='2025-26'
        )
        db.session.add(course)
        db.session.commit()

        # Enroll students
        student1 = User.query.get(test_users['student1_id'])
        student2 = User.query.get(test_users['student2_id'])
        course.students.append(student1)
        course.students.append(student2)
        db.session.commit()

        return course.id


@pytest.fixture
def auth_client(app, client, test_users):
    """Create authenticated test clients."""
    clients = {}
    
    # Teacher client
    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = test_users['teacher_id']
        clients['teacher'] = client
    
    # Need separate clients for each user since sessions are per-client
    from flask import Flask
    client1 = app.test_client()
    with client1:
        with client1.session_transaction() as sess:
            sess['user_id'] = test_users['student1_id']
        clients['student1'] = client1
    
    client2 = app.test_client()
    with client2:
        with client2.session_transaction() as sess:
            sess['user_id'] = test_users['student2_id']
        clients['student2'] = client2
    
    return clients