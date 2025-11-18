#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL on Supabase

This script exports data from the local SQLite database and imports it into PostgreSQL.
Run this after setting up Supabase and updating DATABASE_URL in .env.
"""

import os
import sys
from flask import Flask
from src.database import db
from src.models.user import User
from src.models.course import Course, course_enrollments
from src.models.activity import Activity
from src.models.response import ActivityResponse
from src.models.analytics import Leaderboard, ActivityAnalytics
from src.models.document import Document
from src.models.forum import ForumPost, ForumReply, UserForumRead
from sqlalchemy import select, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(sqlite_uri=None):
    """Create app with specified database URI"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri or os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'temp-key'
    db.init_app(app)
    return app

def export_sqlite_data():
    """Export all data from SQLite database"""
    print("Exporting data from SQLite...")

    # Create app with SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'app.db')
    sqlite_uri = f'sqlite:///{db_path}'
    app = create_app(sqlite_uri)

    with app.app_context():
        data = {
            'users': [user.to_dict() for user in User.query.all()],
            'courses': [course.to_dict() for course in Course.query.all()],
            'course_enrollments': [
                {'course_id': row.course_id, 'user_id': row.user_id, 'enrolled_at': row.enrolled_at}
                for row in db.session.execute(select(course_enrollments)).fetchall()
            ],
            'activities': [activity.to_dict() for activity in Activity.query.all()],
            'responses': [response.to_dict() for response in ActivityResponse.query.all()],
            'leaderboards': [lb.to_dict() for lb in Leaderboard.query.all()],
            'analytics': [analytics.to_dict() for analytics in ActivityAnalytics.query.all()],
            'documents': [doc.to_dict() for doc in Document.query.all()],
            'forum_posts': [post.to_dict() for post in ForumPost.query.all()],
            'forum_replies': [reply.to_dict() for reply in ForumReply.query.all()],
            'forum_reads': [read.to_dict() for read in UserForumRead.query.all()],
        }

    print(f"Exported {sum(len(v) for v in data.values())} records")
    return data

def import_to_postgresql(data):
    """Import data into PostgreSQL"""
    print("Importing data to PostgreSQL...")

    app = create_app()  # Uses DATABASE_URL from env

    with app.app_context():
        # Create tables
        db.create_all()
        print("Tables created")

        # Import in order to handle foreign keys
        # 1. Users
        for user_data in data['users']:
            user = User(
                id=user_data['id'],  # Set id for merge
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                department=user_data.get('department'),
                password_hash=user_data['password_hash'],
                created_at=user_data['created_at'],
                last_login=user_data.get('last_login')
            )
            db.session.merge(user)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['users'])} users")

        # 2. Courses
        for course_data in data['courses']:
            course = Course(
                id=course_data['id'],  # Set id for merge
                course_code=course_data['course_code'],
                course_name=course_data['course_name'],
                description=course_data.get('description'),
                teacher_id=course_data['teacher_id'],
                semester=course_data['semester'],
                academic_year=course_data['academic_year'],
                created_at=course_data['created_at']
            )
            db.session.merge(course)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['courses'])} courses")

        # 3. Course enrollments
        for ce_data in data['course_enrollments']:
            # Use raw SQL with ON CONFLICT DO NOTHING for PostgreSQL
            db.session.execute(
                text("""
                INSERT INTO course_enrollments (course_id, user_id, enrolled_at)
                VALUES (:course_id, :user_id, :enrolled_at)
                ON CONFLICT (course_id, user_id) DO NOTHING
                """),
                {
                    'course_id': ce_data['course_id'],
                    'user_id': ce_data['user_id'],
                    'enrolled_at': ce_data['enrolled_at']
                }
            )
        db.session.commit()
        print(f"Imported {len(data['course_enrollments'])} enrollments")

        # 4. Activities
        for activity_data in data['activities']:
            activity = Activity(
                id=activity_data['id'],  # Set id for merge
                title=activity_data['title'],
                description=activity_data.get('description'),
                activity_type=activity_data['activity_type'],
                course_id=activity_data['course_id'],
                creator_id=activity_data['creator_id'],
                config=activity_data['config'],  # Now dict
                is_ai_generated=activity_data.get('is_ai_generated', False),
                ai_prompt=activity_data.get('ai_prompt'),
                ai_refined=activity_data.get('ai_refined', False),
                status=activity_data['status'],
                start_time=activity_data.get('start_time'),
                end_time=activity_data.get('end_time'),
                duration_minutes=activity_data['duration_minutes'],
                created_at=activity_data['created_at'],
                updated_at=activity_data.get('updated_at')
            )
            db.session.merge(activity)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['activities'])} activities")

        # 5. Responses
        for response_data in data['responses']:
            response = ActivityResponse(
                id=response_data['id'],  # Set id for merge
                activity_id=response_data['activity_id'],
                student_id=response_data['student_id'],
                response_data=response_data['response_data'],  # Now dict
                ai_analysis=response_data.get('ai_analysis'),  # Now dict
                similarity_score=response_data.get('similarity_score'),
                score=response_data.get('score'),
                feedback=response_data.get('feedback'),
                submitted_at=response_data['submitted_at'],
                time_spent_seconds=response_data.get('time_spent_seconds')
            )
            db.session.merge(response)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['responses'])} responses")

        # 6. Leaderboards
        for lb_data in data['leaderboards']:
            lb = Leaderboard(
                id=lb_data['id'],  # Set id for merge
                course_id=lb_data['course_id'],
                name=lb_data['name'],
                description=lb_data.get('description'),
                config=lb_data['config'],  # Now dict
                start_date=lb_data.get('start_date'),
                end_date=lb_data.get('end_date'),
                is_active=lb_data['is_active'],
                created_at=lb_data['created_at'],
                updated_at=lb_data.get('updated_at')
            )
            db.session.merge(lb)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['leaderboards'])} leaderboards")

        # 7. Analytics
        for analytics_data in data['analytics']:
            analytics = ActivityAnalytics(
                id=analytics_data['id'],  # Set id for merge
                activity_id=analytics_data['activity_id'],
                analytics_data=analytics_data['analytics_data'],  # Now dict
                ai_report=analytics_data.get('ai_report'),  # Now dict
                analyzed_at=analytics_data['analyzed_at']
            )
            db.session.merge(analytics)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['analytics'])} analytics")

        # 8. Documents
        for doc_data in data['documents']:
            doc = Document(
                id=doc_data['id'],  # Set id for merge
                course_id=doc_data['course_id'],
                uploader_id=doc_data['uploader_id'],
                filename=doc_data['filename'],
                stored_filename=doc_data['stored_filename'],
                file_path=doc_data['file_path'],
                file_size=doc_data['file_size'],
                file_type=doc_data['file_type'],
                title=doc_data.get('title'),
                description=doc_data.get('description'),
                is_active=doc_data.get('is_active', True),
                download_count=doc_data.get('download_count', 0),
                created_at=doc_data['created_at'],
                updated_at=doc_data.get('updated_at')
            )
            db.session.merge(doc)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['documents'])} documents")

        # 9. Forum posts
        for post_data in data['forum_posts']:
            post = ForumPost(
                id=post_data['id'],  # Set id for merge
                course_id=post_data['course_id'],
                user_id=post_data['user_id'],
                title=post_data['title'],
                content=post_data['content'],
                is_pinned=post_data.get('is_pinned', False),
                created_at=post_data['created_at'],
                updated_at=post_data.get('updated_at')
            )
            db.session.merge(post)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['forum_posts'])} forum posts")

        # 10. Forum replies
        for reply_data in data['forum_replies']:
            reply = ForumReply(
                id=reply_data['id'],  # Set id for merge
                post_id=reply_data['post_id'],
                user_id=reply_data['user_id'],
                content=reply_data['content'],
                parent_reply_id=reply_data.get('parent_reply_id'),
                created_at=reply_data['created_at'],
                updated_at=reply_data.get('updated_at')
            )
            db.session.merge(reply)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['forum_replies'])} forum replies")

        # 11. Forum reads
        for read_data in data['forum_reads']:
            read = UserForumRead(
                id=read_data['id'],  # Set id for merge
                user_id=read_data['user_id'],
                course_id=read_data['course_id'],
                last_read_at=read_data['last_read_at']
            )
            db.session.merge(read)  # Use merge to handle existing records
        db.session.commit()
        print(f"Imported {len(data['forum_reads'])} forum reads")

        # Admin user is already imported from data

    print("Migration completed successfully!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--export-only':
        data = export_sqlite_data()
        import json
        with open('migration_data.json', 'w') as f:
            json.dump(data, f, default=str)
        print("Data exported to migration_data.json")
    else:
        data = export_sqlite_data()
        import_to_postgresql(data)