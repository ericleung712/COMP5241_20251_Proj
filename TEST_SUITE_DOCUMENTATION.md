# Smart Classroom Platform - Test Suite Documentation

## Overview

This document provides a comprehensive overview of the automated test suite for the Smart Classroom Platform, covering both multi-question quiz functionality and AI generation features.

## Test Structure

The test suite is organized into two main test files:

### 1. `tests/test_quiz.py` - Multi-Question Quiz Tests
### 2. `tests/test_ai_generation.py` - AI Generation Feature Tests

## Test Statistics

- **Total Test Classes**: 6
- **Total Test Methods**: 32
- **Test Coverage Areas**:
  - Quiz creation and management
  - Student participation and responses
  - Teacher oversight and analytics
  - AI activity generation
  - JSON parsing and error handling
  - Frontend logic validation

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

---

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

### Functional Coverage
- ✅ Quiz creation (single and multiple questions)
- ✅ Student quiz participation and submission
- ✅ Immediate feedback and scoring
- ✅ Teacher response viewing and analytics
- ✅ AI activity generation for all types
- ✅ JSON parsing with multiple formats
- ✅ Error handling and validation
- ✅ Backward compatibility

### API Coverage
- ✅ Activity creation endpoints
- ✅ Response submission endpoints
- ✅ Activity status management
- ✅ AI generation endpoints
- ✅ Analytics and reporting

### Data Validation
- ✅ Quiz configuration validation
- ✅ Response data structure validation
- ✅ Score calculation validation
- ✅ User permission validation

---

## Test Results Summary

As of November 15, 2025:

- **Total Tests**: 32 test methods across 6 test classes
- **All Tests Passing**: ✅ 32/32 tests pass successfully
- **Test Execution Time**: ~12-15 seconds for full suite (quiz tests: ~12s, AI tests: ~1s)
- **Database Isolation**: ✅ Tests use temporary databases, production database remains unchanged
- **Mock Usage**: Extensive mocking of AI services and external dependencies

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

*Test Suite Version: 1.0*  
*Last Updated: November 15, 2025*  
*Coverage: Multi-Question Quiz & AI Generation Features*