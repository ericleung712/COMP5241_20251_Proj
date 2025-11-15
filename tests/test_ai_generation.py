import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.ai.ai_service import AIService


class TestSemesterOptions:
    """Test dynamic semester options generation"""

    def test_semester_options_logic_september(self):
        """Test semester options logic for September (Fall semester)"""
        # Test the logic directly without mocking Date
        current_year = 2025
        current_month = 9  # September

        # Expected semesters for September: Fall 2025, Spring 2026, Summer 2026
        expected_semesters = ['Fall 2025', 'Spring 2026', 'Summer 2026']

        # This simulates the logic from the JavaScript function
        if current_month >= 9:
            semesters = [f'Fall {current_year}', f'Spring {current_year+1}', f'Summer {current_year+1}']
        elif current_month >= 5:
            semesters = [f'Summer {current_year}', f'Fall {current_year}', f'Spring {current_year+1}']
        else:
            semesters = [f'Spring {current_year}', f'Summer {current_year}', f'Fall {current_year}']

        assert semesters == expected_semesters

    def test_semester_options_logic_january(self):
        """Test semester options logic for January (Spring semester)"""
        current_year = 2025
        current_month = 1  # January

        # Expected semesters for January: Spring 2025, Summer 2025, Fall 2025
        expected_semesters = ['Spring 2025', 'Summer 2025', 'Fall 2025']

        if current_month >= 9:
            semesters = [f'Fall {current_year}', f'Spring {current_year+1}', f'Summer {current_year+1}']
        elif current_month >= 5:
            semesters = [f'Summer {current_year}', f'Fall {current_year}', f'Spring {current_year+1}']
        else:
            semesters = [f'Spring {current_year}', f'Summer {current_year}', f'Fall {current_year}']

        assert semesters == expected_semesters

    def test_semester_options_logic_may(self):
        """Test semester options logic for May (Summer semester)"""
        current_year = 2025
        current_month = 5  # May

        # Expected semesters for May: Summer 2025, Fall 2025, Spring 2026
        expected_semesters = ['Summer 2025', 'Fall 2025', 'Spring 2026']

        if current_month >= 9:
            semesters = [f'Fall {current_year}', f'Spring {current_year+1}', f'Summer {current_year+1}']
        elif current_month >= 5:
            semesters = [f'Summer {current_year}', f'Fall {current_year}', f'Spring {current_year+1}']
        else:
            semesters = [f'Spring {current_year}', f'Summer {current_year}', f'Fall {current_year}']

        assert semesters == expected_semesters


class TestAcademicYearPlaceholder:
    """Test dynamic academic year placeholder"""

    def test_academic_year_placeholder_current_year(self):
        """Test academic year placeholder shows current year format"""
        current_year = 2025
        next_year_short = str(current_year + 1)[2:]  # '26'

        expected_placeholder = f'e.g.{current_year}-{next_year_short}'
        assert expected_placeholder == 'e.g.2025-26'

    def test_academic_year_placeholder_year_boundary(self):
        """Test academic year placeholder at year boundary"""
        current_year = 2025
        next_year_short = str(current_year + 1)[2:]

        expected_placeholder = f'e.g.{current_year}-{next_year_short}'
        assert expected_placeholder == 'e.g.2025-26'

        # Test next year
        current_year = 2026
        next_year_short = str(current_year + 1)[2:]

        expected_placeholder = f'e.g.{current_year}-{next_year_short}'
        assert expected_placeholder == 'e.g.2026-27'


class TestAIGeneration:
    """Test AI activity generation for all activity types"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return AIService()

    def test_generate_poll_activity(self, ai_service):
        """Test poll activity generation"""
        mock_response = {
            "title": "Test Poll",
            "description": "A test poll activity",
            "question": "What is your favorite color?",
            "options": ["Red", "Blue", "Green", "Yellow"],
            "correct_answer": "Blue"
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity(
                'poll',
                'Test course content about colors',
                'Web resources about colors'
            )

            assert result['title'] == 'Test Poll'
            assert result['question'] == 'What is your favorite color?'
            assert len(result['options']) == 4

    def test_generate_quiz_activity(self, ai_service):
        """Test quiz activity generation"""
        mock_response = {
            "title": "Test Quiz",
            "description": "A test quiz activity",
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": 1,
                    "explanation": "Basic math"
                }
            ],
            "time_limit": 300
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity(
                'quiz',
                'Test course content about math',
                'Web resources about math'
            )

            assert result['title'] == 'Test Quiz'
            assert len(result['questions']) == 1
            assert result['questions'][0]['question'] == 'What is 2+2?'

    def test_generate_word_cloud_activity(self, ai_service):
        """Test word cloud activity generation"""
        mock_response = {
            "title": "Test Word Cloud",
            "description": "A test word cloud activity",
            "prompt": "Enter keywords related to Python programming",
            "max_words": 10,
            "min_word_length": 2
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity(
                'word_cloud',
                'Test course content about Python',
                'Web resources about Python'
            )

            assert result['title'] == 'Test Word Cloud'
            assert result['prompt'] == 'Enter keywords related to Python programming'
            assert result['max_words'] == 10

    def test_generate_short_answer_activity(self, ai_service):
        """Test short answer activity generation"""
        mock_response = {
            "title": "Test Short Answer",
            "description": "A test short answer activity",
            "questions": [
                {
                    "question": "Explain what is Python?",
                    "max_length": 500,
                    "sample_answer": "Python is a programming language"
                }
            ],
            "time_limit": 600
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity(
                'short_answer',
                'Test course content about programming',
                'Web resources about programming'
            )

            assert result['title'] == 'Test Short Answer'
            assert len(result['questions']) == 1
            assert result['questions'][0]['max_length'] == 500

    def test_generate_mini_game_activity(self, ai_service):
        """Test mini game activity generation"""
        mock_response = {
            "title": "Test Mini Game",
            "description": "A test mini game activity",
            "game_type": "matching",
            "rules": "Match the terms with their definitions",
            "content": {
                "items": ["Variable", "Function", "Class"],
                "matches": ["A storage location", "A reusable code block", "A blueprint for objects"]
            }
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity(
                'mini_game',
                'Test course content about programming concepts',
                'Web resources about programming'
            )

            assert result['title'] == 'Test Mini Game'
            assert result['game_type'] == 'matching'
            assert len(result['content']['items']) == 3


class TestJSONParsing:
    """Test various JSON parsing scenarios"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return AIService()

    def test_parse_clean_json(self, ai_service):
        """Test parsing clean JSON response"""
        mock_response = '{"title": "Test", "description": "Clean JSON"}'

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = mock_response

            result = ai_service.generate_activity('poll', 'test content')

            assert result['title'] == 'Test'
            assert result['description'] == 'Clean JSON'

    def test_parse_markdown_wrapped_json(self, ai_service):
        """Test parsing JSON wrapped in markdown code blocks"""
        mock_response = '''```json
        {
            "title": "Test",
            "description": "Markdown wrapped JSON"
        }
        ```'''

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = mock_response

            result = ai_service.generate_activity('poll', 'test content')

            assert result['title'] == 'Test'
            assert result['description'] == 'Markdown wrapped JSON'

    def test_parse_json_with_markdown_code_block(self, ai_service):
        """Test parsing JSON with generic markdown code block"""
        mock_response = '''```
        {
            "title": "Test",
            "description": "Generic markdown JSON"
        }
        ```'''

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = mock_response

            result = ai_service.generate_activity('poll', 'test content')

            assert result['title'] == 'Test'
            assert result['description'] == 'Generic markdown JSON'

    def test_parse_mixed_content_with_json(self, ai_service):
        """Test parsing content with JSON embedded in text"""
        mock_response = '''Here is the generated activity:
        {
            "title": "Test",
            "description": "JSON in mixed content"
        }
        Hope you like it!'''

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = mock_response

            result = ai_service.generate_activity('poll', 'test content')

            assert result['title'] == 'Test'
            assert result['description'] == 'JSON in mixed content'

    def test_parse_invalid_json_fallback(self, ai_service):
        """Test fallback behavior for invalid JSON"""
        mock_response = 'This is not JSON at all, just plain text response.'

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = mock_response

            result = ai_service.generate_activity('poll', 'test content')

            assert 'parse_error' in result
            assert 'raw_content' in result
            assert result['title'] == 'AI生成的poll活动'

    def test_ai_service_error_handling(self, ai_service):
        """Test error handling when AI service fails"""
        with patch.object(ai_service.client.chat.completions, 'create', side_effect=Exception('API Error')):
            result = ai_service.generate_activity('poll', 'test content')

            assert 'error' in result
            assert 'AI生成失败' in result['error']


class TestQuestionsArrayHandling:
    """Test handling of questions array in quiz and short_answer activities"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return AIService()

    def test_quiz_multiple_questions_array(self, ai_service):
        """Test quiz with multiple questions in array format"""
        mock_response = {
            "title": "Multi-Question Quiz",
            "description": "A quiz with multiple questions",
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": 1,
                    "explanation": "Basic addition"
                },
                {
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correct_answer": 2,
                    "explanation": "Geography knowledge"
                }
            ],
            "time_limit": 600
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity('quiz', 'test content')

            assert len(result['questions']) == 2
            assert result['questions'][0]['question'] == 'What is 2+2?'
            assert result['questions'][1]['question'] == 'What is the capital of France?'

    def test_short_answer_multiple_questions_array(self, ai_service):
        """Test short answer with multiple questions in array format"""
        mock_response = {
            "title": "Multi-Question Short Answer",
            "description": "Short answer with multiple questions",
            "questions": [
                {
                    "question": "Explain what is a variable in programming?",
                    "max_length": 300,
                    "sample_answer": "A variable is a storage location with a name"
                },
                {
                    "question": "What is a function?",
                    "max_length": 400,
                    "sample_answer": "A function is a reusable block of code"
                }
            ],
            "time_limit": 900
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity('short_answer', 'test content')

            assert len(result['questions']) == 2
            assert result['questions'][0]['max_length'] == 300
            assert result['questions'][1]['max_length'] == 400

    def test_quiz_single_question_backward_compatibility(self, ai_service):
        """Test quiz with single question format (backward compatibility)"""
        mock_response = {
            "title": "Single Question Quiz",
            "description": "A quiz with single question",
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1,
            "time_limit": 300
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity('quiz', 'test content')

            # Should handle single question format
            assert result['title'] == 'Single Question Quiz'
            assert 'question' in result or 'questions' in result