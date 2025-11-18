# Smart Classroom Platform - Test Suite Documentation

## Overview

This document provides a comprehensive overview of the automated test suite for the Smart Classroom Platform, covering multi-question quiz functionality, AI generation features, and analytics endpoints.

## Test Structure

The test suite is organized into four main test files:

### 1. `tests/test_quiz.py` - Multi-Question Quiz Tests
### 2. `tests/test_ai_generation.py` - AI Generation Feature Tests
### 3. `tests/test_analytics.py` - Analytics Endpoints Tests
### 4. `tests/test_forum.py` - Forum Functionality Tests

## Test Statistics

- **Total Test Classes**: 10
- **Total Test Methods**: 96
- **Test Coverage Areas**:
  - Quiz creation and management (single and multiple questions)
  - Student participation and responses
  - Teacher oversight and analytics
  - Teacher dashboard analytics and performance charts
  - AI activity generation and tracking
  - JSON parsing and error handling
  - Document dropdown API functionality
  - Time limit inclusion in AI prompts
  - Frontend logic validation
  - AI activity tracking and analytics
  - Student average score calculations
  - Admin dashboard metrics (active users, AI activities)
  - Forum post and reply creation
  - Threaded replies and depth limits
  - Forum search and notifications
  - Teacher forum access and permissions
  - Forum unread status calculation
  - Soft delete functionality for posts and replies
  - PostgreSQL database compatibility
  - Foreign key constraint handling
  - JSONB field optimization
  - Database migration validation

---

## 1. Multi-Question Quiz Tests (`test_quiz.py`)

### TestMultiQuestionQuiz Class

#### Quiz Creation Tests
- **`test_create_quiz_single_question`**: Validates creation of quizzes with single questions
- **`test_create_quiz_multiple_questions`**: Tests creation of quizzes with 2-10 questions
- **`test_quiz_config_validation`**: Ensures proper validation of quiz configuration

#### Quiz Viewing Tests
- **`test_view_quiz_details_showing_all_questions`**: Verifies all questions are displayed correctly in quiz details

#### Student Participation Tests
- **`test_student_participates_multi_question_quiz`**: Tests complete student quiz participation workflow
- **`test_student_cannot_submit_without_answering_all_questions`**: Validates submission constraints
- **`test_student_receives_immediate_feedback_with_scores`**: Tests immediate scoring and feedback

#### Teacher Oversight Tests
- **`test_teacher_views_student_responses_all_questions`**: Validates teacher can view all student responses
- **`test_teacher_sees_overall_score_statistics`**: Tests score statistics and analytics

#### Compatibility Tests
- **`test_backward_compatibility_single_question_quizzes`**: Ensures backward compatibility with existing single-question quizzes

#### AI Integration Tests
- **`test_ai_generated_quiz_creation`**: Tests AI-generated quiz creation process
- **`test_ai_generated_quiz_can_be_used_successfully`**: Validates AI-generated quizzes work end-to-end

#### Error Handling Tests
- **`test_error_handling_validation`**: Tests various error scenarios and validation

---

## 2. AI Generation Tests (`test_ai_generation.py`)

### TestSemesterOptions Class
Tests for dynamic semester dropdown generation based on current date:

- **`test_semester_options_logic_september`**: Validates semester options in September (Fall semester)
- **`test_semester_options_logic_january`**: Validates semester options in January (Spring semester)
- **`test_semester_options_logic_may`**: Validates semester options in May (Summer semester)

### TestAcademicYearPlaceholder Class
Tests for dynamic academic year placeholder updates:

- **`test_academic_year_placeholder_current_year`**: Tests placeholder shows current year format (e.g., 2025-26)
- **`test_academic_year_placeholder_year_boundary`**: Tests year boundary transitions

### TestAIGeneration Class
Tests for AI activity generation across all supported activity types:

- **`test_generate_poll_activity`**: Tests poll activity generation with questions and options
- **`test_generate_quiz_activity`**: Tests quiz activity generation with questions array
- **`test_generate_word_cloud_activity`**: Tests word cloud activity generation
- **`test_generate_short_answer_activity`**: Tests short answer activity generation
- **`test_generate_mini_game_activity`**: Tests mini game activity generation

### TestJSONParsing Class
Tests for robust JSON parsing with various AI response formats:

- **`test_parse_clean_json`**: Tests parsing of clean JSON responses
- **`test_parse_markdown_wrapped_json`**: Tests parsing JSON wrapped in markdown code blocks (```json)
- **`test_parse_json_with_markdown_code_block`**: Tests parsing JSON with generic markdown blocks (```)
- **`test_parse_mixed_content_with_json`**: Tests extracting JSON from mixed text content
- **`test_parse_invalid_json_fallback`**: Tests fallback behavior for invalid JSON
- **`test_ai_service_error_handling`**: Tests error handling when AI service fails

### TestQuestionsArrayHandling Class
Tests for handling questions array format in quiz and short answer activities:

- **`test_quiz_multiple_questions_array`**: Tests quiz with multiple questions in array format
- **`test_short_answer_multiple_questions_array`**: Tests short answer with multiple questions in array format
- **`test_quiz_single_question_backward_compatibility`**: Tests backward compatibility with single question format

### TestDocumentInclusion Class
Tests for document content inclusion in AI activity generation:

- **`test_generate_activity_with_document_content`**: Tests document content inclusion in AI prompts
- **`test_document_content_formatting`**: Tests proper formatting of document content
- **`test_generate_ai_activity_with_documents`**: Tests full API with document inclusion
- **`test_generate_ai_activity_without_documents`**: Tests API without document inclusion
- **`test_generate_ai_activity_invalid_document`**: Tests handling of invalid documents

### TestTimeLimitInclusion Class
Tests for time limit inclusion in AI activity generation:

- **`test_generate_activity_with_time_limit`**: Tests AI service includes time limit in prompts
- **`test_generate_activity_without_time_limit`**: Tests backward compatibility without time limits
- **`test_generate_ai_activity_with_time_limit`**: Tests full API endpoint with time limit parameter

### TestDocumentDropdownAPI Class
Tests for document dropdown API endpoints supporting AI activity generator:

- **`test_get_course_documents_teacher`**: Tests teacher access to all course documents
- **`test_get_course_documents_student`**: Tests student access to active documents only
- **`test_get_course_documents_unauthorized`**: Tests authentication requirements
- **`test_get_course_documents_wrong_course_teacher`**: Tests teacher permission boundaries
- **`test_get_course_documents_student_not_enrolled`**: Tests student enrollment requirements
- **`test_get_course_documents_empty_course`**: Tests empty course handling
- **`test_document_dropdown_integration_with_ai_generation`**: Tests end-to-end document selection flow

---

## 3. Analytics Endpoints Tests (`test_analytics.py`)

### TestAnalytics Class
Tests for analytics API endpoints including teacher dashboard analytics and system overview:

#### Authentication and Authorization Tests
- **`test_teacher_system_overview_requires_auth`**: Verifies unauthenticated requests return 401
- **`test_teacher_system_overview_requires_teacher_role`**: Ensures only teachers can access teacher analytics endpoints

#### Teacher System Overview Tests
- **`test_teacher_system_overview_with_data`**: Tests successful data retrieval with populated courses and activities
- **`test_teacher_system_overview_empty_courses`**: Tests behavior when teacher has no courses
- **`test_teacher_system_overview_with_date_range`**: Tests date range filtering functionality
- **`test_teacher_system_overview_invalid_date_range`**: Tests validation of invalid date parameters

#### Dashboard Data Tests
- **`test_teacher_dashboard_data`**: Tests teacher dashboard data endpoint with course and activity statistics
- **`test_student_dashboard_data`**: Tests student dashboard data endpoint with enrollment and participation data
- **`test_student_dashboard_data_with_responses`**: Tests student dashboard with average score calculation from quiz responses
- **`test_admin_dashboard_data`**: Tests admin dashboard data endpoint with system-wide statistics
- **`test_admin_dashboard_ai_activities_count`**: Tests that admin dashboard correctly counts AI-generated activities

#### Test Features
- **Authentication Testing**: Comprehensive checks for auth requirements and proper HTTP status codes
- **Authorization Testing**: Role-based access control validation for teacher-specific endpoints
- **Data Filtering**: Ensures teacher-specific data isolation and course ownership validation
- **Date Range Validation**: Tests optional date filtering with ISO format validation
- **Edge Cases**: Empty data scenarios, invalid inputs, and error conditions
- **API Response Validation**: Verifies correct JSON structure, data accuracy, and aggregations
- **AI Activity Tracking**: Tests proper counting and flagging of AI-generated activities
- **Student Analytics**: Tests average score calculations and dashboard metrics

## Test Fixtures

### Core Fixtures (`conftest.py`)
- **`app`**: Creates and configures test Flask application instance
- **`client`**: Provides test client for API testing
- **`runner`**: Provides test runner for Click commands
- **`test_users`**: Creates test users (teacher, students) and returns their IDs
- **`test_course`**: Creates test course with enrolled students
- **`auth_client`**: Creates authenticated test clients for different user roles

### AI Service Fixtures (`test_ai_generation.py`)
- **`ai_service`**: Creates AIService instance for testing

---

## Running the Tests

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install pytest pytest-flask requests
```

### Test Configuration

The test configuration is defined in `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Running All Tests

To run the complete test suite:

```bash
cd /workspaces/COMP5241_20251_Proj
python -m pytest tests/ -v
```

### Running Specific Test Files

#### Run Quiz Tests Only:
```bash
python -m pytest tests/test_quiz.py -v
```

#### Run AI Generation Tests Only:
```bash
python -m pytest tests/test_ai_generation.py -v
```

#### Run Analytics Tests:
```bash
python -m pytest tests/test_analytics.py::TestAnalytics -v
```

#### Run Forum Tests:
```bash
python -m pytest tests/test_forum.py::TestForumRoutes -v
```

---

## 4. Forum Functionality Tests (`test_forum.py`)

### TestForumModels Class
Tests for forum data models and relationships:

- **`test_forum_post_creation`**: Validates forum post creation with proper relationships
- **`test_forum_reply_creation`**: Tests reply creation and user attribution
- **`test_threaded_replies`**: Verifies threaded reply relationships and child reply access
- **`test_user_forum_read`**: Tests user forum read tracking with unique constraints

### TestForumRoutes Class
Comprehensive tests for forum API endpoints:

#### Authentication and Authorization Tests
- **`test_get_forum_posts_unauthorized`**: Verifies authentication requirements
- **`test_get_forum_posts_no_access`**: Tests permission checks for course access

#### Forum Post Management Tests
- **`test_create_forum_post`**: Tests teacher forum post creation
- **`test_create_forum_post_student`**: Tests student forum post creation
- **`test_create_forum_post_invalid_data`**: Validates input data requirements
- **`test_get_forum_posts`**: Tests forum post retrieval and listing
- **`test_update_forum_post`**: Tests post editing functionality
- **`test_update_forum_post_no_permission`**: Verifies permission controls
- **`test_delete_forum_post`**: Tests post deletion with proper authorization

#### Reply Functionality Tests
- **`test_create_forum_reply`**: Tests basic reply creation
- **`test_threaded_replies_api`**: Tests threaded reply API responses
- **`test_create_reply_to_reply`**: Tests nested reply creation
- **`test_create_reply_to_reply_invalid_parent`**: Validates parent reply existence
- **`test_create_reply_to_reply_wrong_post`**: Tests cross-post reply prevention
- **`test_reply_depth_limit`**: Enforces 3-level reply depth limit

#### Forum Features Tests
- **`test_forum_search`**: Tests search functionality across titles and content
- **`test_forum_notifications`**: Tests unread notification system
- **`test_forum_notifications_exclude_own_content`**: Verifies own content exclusion
- **`test_forum_pagination`**: Tests pagination for large forum datasets

#### Soft Delete Tests
- **`test_soft_delete_forum_post_by_owner`**: Tests post owner can soft delete their own posts
- **`test_soft_delete_forum_reply_by_owner`**: Tests reply owner can soft delete their own replies
- **`test_soft_delete_forum_post_by_teacher`**: Tests teachers can soft delete any post in their courses
- **`test_soft_delete_forum_reply_by_teacher`**: Tests teachers can soft delete any reply in their courses
- **`test_soft_delete_forum_post_no_permission`**: Tests users cannot delete posts they don't own or aren't teachers for
- **`test_soft_delete_forum_reply_no_permission`**: Tests users cannot delete replies they don't own or aren't teachers for
- **`test_soft_delete_preserves_reply_count`**: Tests that soft deleting posts/replies preserves reply counts and threading

### Test Features
- **Authentication Testing**: Comprehensive checks for auth requirements and proper HTTP status codes
- **Authorization Testing**: Role-based access control for forum operations
- **Data Validation**: Ensures proper forum data structure and relationships
- **Threading Logic**: Validates nested reply creation and depth limits
- **Search Functionality**: Tests content and title search capabilities
- **Notification System**: Verifies unread status calculation and mark-as-read functionality
- **Pagination**: Tests large dataset handling with proper pagination
- **Permission Controls**: Ensures teachers and students have appropriate forum access
- **User Attribution**: Tests proper user name display in forum content

#### Run Forum Tests Only:
```bash
python -m pytest tests/test_forum.py -v
```

### Running Specific Test Classes

#### Run Multi-Question Quiz Tests:
```bash
python -m pytest tests/test_quiz.py::TestMultiQuestionQuiz -v
```

#### Run AI Generation Tests:
```bash
python -m pytest tests/test_ai_generation.py::TestAIGeneration -v
```

#### Run JSON Parsing Tests:
```bash
python -m pytest tests/test_ai_generation.py::TestJSONParsing -v
```

#### Run Analytics Tests:
```bash
python -m pytest tests/test_analytics.py::TestAnalytics -v
```

### Running Individual Tests

#### Run a Single Test Method:
```bash
python -m pytest tests/test_quiz.py::TestMultiQuestionQuiz::test_create_quiz_single_question -v
```

#### Run Tests with Coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Output Options

#### Verbose Output (Default):
```bash
python -m pytest tests/ -v
```

#### Short Tracebacks:
```bash
python -m pytest tests/ --tb=short
```

#### No Output (Quiet):
```bash
python -m pytest tests/ -q
```

## Database Isolation

### Issue Fixed
Initially, tests were modifying the production database (`database/app.db`) because the `create_app()` function in `main.py` hardcoded the database path. This caused test data to persist in the production database.

### Solution Implemented
Modified `tests/conftest.py` to use monkey patching of `os.path.join` to intercept the database path creation in `create_app()`. Tests now use temporary SQLite databases that are automatically created and cleaned up.

### Key Changes
- **Monkey Patching**: `os.path.join` is patched to return temporary database paths when creating `database/app.db`
- **Automatic Cleanup**: Temporary databases are removed after each test session
- **Production Safety**: Production database remains completely untouched by tests

### Verification
- Production database user count: 3 (unchanged)
- Production database activity count: 1 (unchanged)
- Production database response count: 1 (unchanged)

---

## PostgreSQL Migration Testing

### Migration Validation
The test suite has been updated to validate the successful migration from SQLite to PostgreSQL:

#### Foreign Key Constraint Fixes
- **Issue**: PostgreSQL's stricter constraints caused test failures with hardcoded user IDs
- **Solution**: Updated all forum tests to use dynamic fixture references instead of hardcoded IDs (1, 2, 3)
- **Result**: All 32 forum tests now pass with PostgreSQL foreign key constraints

#### JSON Field Optimization
- **Issue**: JSON fields needed migration from TEXT to JSONB type for performance
- **Solution**: Updated all models to use `db.JSON` for cross-database compatibility
- **Result**: JSON operations work seamlessly in both SQLite and PostgreSQL

#### Test Database Isolation
- **Issue**: Tests were initially running against production database
- **Solution**: Enhanced `conftest.py` with proper database path isolation for PostgreSQL
- **Result**: Tests safely use temporary databases without affecting production data

#### Migration Script Validation
- **Export/Import**: Comprehensive migration script with conflict resolution
- **Data Integrity**: All relationships and data preserved during migration
- **Association Tables**: Special handling for many-to-many relationships
- **Progress Tracking**: Detailed logging and error reporting

### Migration Test Coverage
- ✅ Forum tests with dynamic user ID fixtures
- ✅ Foreign key constraint validation
- ✅ JSONB field compatibility
- ✅ Database connection management
- ✅ Environment variable configuration
- ✅ Migration script functionality
- ✅ Data integrity preservation

### Functional Coverage
- ✅ Quiz creation (single and multiple questions)
- ✅ Student quiz participation and submission
- ✅ Immediate feedback and scoring
- ✅ Teacher response viewing and analytics
- ✅ Teacher dashboard analytics and performance charts
- ✅ AI activity generation for all types
- ✅ JSON parsing with multiple formats
- ✅ Error handling and validation
- ✅ Backward compatibility
- ✅ AI activity tracking and database flagging
- ✅ Student average score calculations
- ✅ Admin dashboard metrics (active users, AI activities)
- ✅ Forum post and reply creation
- ✅ Threaded replies with depth limits
- ✅ Forum search and pagination
- ✅ Teacher forum access and permissions
- ✅ Forum unread status calculation and display
- ✅ Soft delete functionality for forum posts and replies
- ✅ PostgreSQL database compatibility and migration
- ✅ Foreign key constraint handling
- ✅ JSONB field optimization and performance
- ✅ Database isolation and test safety

### API Coverage
- ✅ Activity creation endpoints
- ✅ Response submission endpoints
- ✅ Activity status management
- ✅ AI generation endpoints
- ✅ Analytics and reporting endpoints
- ✅ Teacher dashboard analytics endpoints
- ✅ Student dashboard with average score metrics
- ✅ Admin dashboard with active users and AI activities tracking

### Data Validation
- ✅ Quiz configuration validation
- ✅ Response data structure validation
- ✅ Score calculation validation
- ✅ User permission validation
- ✅ AI activity flag validation
- ✅ Average score calculation accuracy
- ✅ Admin dashboard metrics accuracy

---

## Test Results Summary

As of November 18, 2025:

- **Total Tests**: 96 test methods across 10 test classes
- **All Tests Passing**: ✅ 96/96 tests pass successfully
- **Test Execution Time**: ~9 minutes for full suite (quiz tests: ~2m, AI tests: ~1m, analytics tests: ~2m, forum tests: ~4m)
- **Database Compatibility**: ✅ Tests pass with both SQLite (development) and PostgreSQL (production)
- **Database Isolation**: ✅ Tests use temporary databases, production database remains unchanged
- **Migration Validation**: ✅ All tests pass post-PostgreSQL migration
- **Mock Usage**: Extensive mocking of AI services and external dependencies

---

## Database Compatibility

### Multi-Database Support
The test suite now supports both SQLite (development) and PostgreSQL (production) databases:

- **SQLite**: Used for local development and fast testing
- **PostgreSQL**: Used for production deployment on Supabase
- **Automatic Detection**: Tests automatically use the appropriate database based on `DATABASE_URL` environment variable
- **Constraint Handling**: Tests properly handle PostgreSQL's stricter foreign key constraints
- **JSONB Optimization**: Tests validate JSONB field performance improvements

### Migration Testing
- **Data Integrity**: Migration preserves all data and relationships
- **Foreign Key Constraints**: All foreign key relationships maintained
- **JSON Field Compatibility**: Seamless JSON/TEXT to JSONB migration
- **Performance Validation**: JSONB queries show improved performance

---

## Continuous Integration

These tests are designed to run in CI/CD pipelines and provide:

- Fast feedback on code changes
- Regression testing for existing functionality
- Validation of new features
- Confidence in deployments

### Recommended CI Commands:
```bash
# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=xml

# Run tests in parallel (if pytest-xdist installed)
python -m pytest tests/ -n auto

# Fail fast on first error
python -m pytest tests/ --tb=short -x
```

---

## Maintenance Guidelines

### Adding New Tests
1. Follow existing naming conventions (`test_*`)
2. Use appropriate fixtures from `conftest.py`
3. Include docstrings explaining test purpose
4. Mock external dependencies (AI services, etc.)
5. Test both success and error scenarios

### Test Organization
- Keep related tests in the same class
- Use descriptive test method names
- Group fixtures logically
- Separate unit tests from integration tests

### Best Practices
- Tests should be independent and isolated
- Use meaningful assertions with clear error messages
- Mock external services to avoid flaky tests
- Keep tests fast and reliable
- Test edge cases and error conditions

---

*Test Suite Version: 2.0*  
*Last Updated: November 18, 2025*  
*Coverage: Multi-Question Quiz, AI Generation Features, Analytics Endpoints, Dashboard Metrics, Forum Functionality & PostgreSQL Migration*