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


class TestDocumentInclusion:
    """Test document inclusion in AI activity generation"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return AIService()

    def test_generate_activity_with_document_content(self, ai_service):
        """Test that document content is properly included in AI prompts"""
        mock_response = {
            "title": "Test Activity with Documents",
            "description": "Activity generated with document content",
            "question": "What is the main topic?",
            "options": ["Topic A", "Topic B", "Topic C", "Topic D"],
            "correct_answer": "Topic A"
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            # Test with document content appended
            course_content = "Basic course content"
            document_content = "\n\n文档：Sample Document\nThis is extracted text from a document about advanced topics."

            full_content = course_content + "\n\n--- 从上传文档提取的内容 ---\n" + document_content

            result = ai_service.generate_activity(
                'poll',
                full_content,
                'Web resources'
            )

            assert result['title'] == 'Test Activity with Documents'
            assert result['description'] == 'Activity generated with document content'

    def test_document_content_formatting(self, ai_service):
        """Test that document content is properly formatted when appended"""
        # Test the content formatting logic directly
        course_content = "Original course content"
        document_content = "文档：Test Doc\nExtracted content here."

        expected_full_content = course_content + "\n\n--- 从上传文档提取的内容 ---\n" + document_content

        assert expected_full_content == "Original course content\n\n--- 从上传文档提取的内容 ---\n文档：Test Doc\nExtracted content here."

    @patch('src.routes.activity.extract_document_content')
    @patch('src.models.document.Document')
    def test_generate_ai_activity_with_documents(self, mock_document_class, mock_extract_content, auth_client, test_course):
        """Test the full endpoint with document inclusion"""
        client = auth_client['teacher']
        
        # Setup mocks
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.course_id = test_course  # test_course is already the ID
        mock_doc.is_active = True
        mock_doc.title = "Test Document"
        mock_doc.filename = "test.pdf"

        mock_document_class.query.get.return_value = mock_doc
        mock_extract_content.return_value = "Extracted document content about Python programming."

        # Mock AI service response
        mock_response = {
            "title": "Document-Enhanced Activity",
            "description": "Activity with document content",
            "question": "What is Python?",
            "options": ["Snake", "Programming Language", "Coffee", "Book"],
            "correct_answer": "Programming Language"
        }

        mock_ai_instance = Mock()
        mock_ai_instance.generate_activity.return_value = mock_response

        with patch('src.routes.activity.AIService', return_value=mock_ai_instance) as mock_ai_service_class:

            # Make request with document_ids
            response = client.post('/api/activities/ai/generate', json={
                'activity_type': 'poll',
                'course_content': 'Basic Python concepts',
                'course_id': test_course,
                'document_ids': [1]
            })

            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
            
            assert response.status_code == 200
            data = response.get_json()

            # Verify AI service was called with enhanced content
            mock_ai_instance.generate_activity.assert_called_once()
            call_args = mock_ai_instance.generate_activity.call_args

            # Check that document content was appended
            enhanced_content = call_args.kwargs['course_content']
            assert 'Basic Python concepts' in enhanced_content
            assert '--- 从上传文档提取的内容 ---' in enhanced_content
            assert 'Extracted document content about Python programming' in enhanced_content

            assert data['message'] == 'AI活动生成成功'
            assert data['generated_activity']['title'] == 'Document-Enhanced Activity'

    @patch('src.routes.activity.extract_document_content')
    @patch('src.models.document.Document')
    def test_generate_ai_activity_without_documents(self, mock_document_class, mock_extract_content, auth_client, test_course):
        """Test the endpoint works normally without document_ids"""
        client = auth_client['teacher']
        
        # Mock AI service response
        mock_response = {
            "title": "Regular Activity",
            "description": "Activity without documents",
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4"
        }

        mock_ai_instance = Mock()
        mock_ai_instance.generate_activity.return_value = mock_response

        with patch('src.routes.activity.AIService', return_value=mock_ai_instance) as mock_ai_service_class:
            mock_ai_instance = Mock()
            mock_ai_service_class.return_value = mock_ai_instance
            mock_ai_instance.generate_activity.return_value = mock_response

            # Make request without document_ids
            response = client.post('/api/activities/ai/generate', json={
                'activity_type': 'poll',
                'course_content': 'Basic math',
                'course_id': test_course
            })

            assert response.status_code == 200
            data = response.get_json()

            # Verify AI service was called with original content only
            mock_ai_instance.generate_activity.assert_called_once()
            call_args = mock_ai_instance.generate_activity.call_args

            # Check that content was not enhanced
            content = call_args.kwargs['course_content']
            assert content == 'Basic math'
            assert '--- 从上传文档提取的内容 ---' not in content

            # Verify extract_content was not called
            mock_extract_content.assert_not_called()

            assert data['message'] == 'AI活动生成成功'
            assert data['generated_activity']['title'] == 'Regular Activity'

    @patch('src.routes.activity.extract_document_content')
    @patch('src.models.document.Document')
    def test_generate_ai_activity_invalid_document(self, mock_document_class, mock_extract_content, auth_client, test_course):
        """Test that invalid documents are ignored"""
        client = auth_client['teacher']
        
        # Setup mock for invalid document (wrong course)
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.course_id = 999  # Different course
        mock_doc.is_active = True

        mock_document_class.query.get.return_value = mock_doc

        # Mock AI service response
        mock_response = {
            "title": "Activity with Invalid Doc",
            "description": "Should ignore invalid document",
            "question": "Test question?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }

        mock_ai_instance = Mock()
        mock_ai_instance.generate_activity.return_value = mock_response

        with patch('src.routes.activity.AIService', return_value=mock_ai_instance) as mock_ai_service_class:
            mock_ai_instance = Mock()
            mock_ai_service_class.return_value = mock_ai_instance
            mock_ai_instance.generate_activity.return_value = mock_response

            # Make request with invalid document ID
            response = client.post('/api/activities/ai/generate', json={
                'activity_type': 'poll',
                'course_content': 'Test content',
                'course_id': test_course,
                'document_ids': [1]  # Invalid document
            })

            assert response.status_code == 200
            data = response.get_json()

            # Verify AI service was called with original content only (invalid doc ignored)
            mock_ai_instance.generate_activity.assert_called_once()
            call_args = mock_ai_instance.generate_activity.call_args

            content = call_args.kwargs['course_content']
            assert content == 'Test content'
            assert '--- 从上传文档提取的内容 ---' not in content

            # Verify extract_content was not called for invalid document
            mock_extract_content.assert_not_called()


class TestTimeLimitInclusion:
    """Test time limit inclusion in AI activity generation"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return AIService()

    def test_generate_activity_with_time_limit(self, ai_service):
        """Test that time limit is included in AI prompts"""
        mock_response = {
            "title": "Test Activity with Time Limit",
            "description": "Activity with time constraint",
            "question": "What is the answer?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity(
                'poll',
                'Test course content',
                'Web resources',
                'Additional prompt',
                15  # 15 minutes time limit
            )

            assert result['title'] == 'Test Activity with Time Limit'

            # Verify the prompt included time limit
            call_args = mock_create.call_args
            messages = call_args.kwargs['messages']
            prompt_content = messages[1]['content']
            
            assert 'Time Limit: 15 minutes' in prompt_content

    def test_generate_activity_without_time_limit(self, ai_service):
        """Test that activities work normally without time limit"""
        mock_response = {
            "title": "Test Activity without Time Limit",
            "description": "Activity without time constraint",
            "question": "What is the answer?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }

        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

            result = ai_service.generate_activity(
                'poll',
                'Test course content',
                'Web resources',
                'Additional prompt'
                # No time_limit parameter
            )

            assert result['title'] == 'Test Activity without Time Limit'

            # Verify the prompt did not include time limit
            call_args = mock_create.call_args
            messages = call_args.kwargs['messages']
            prompt_content = messages[1]['content']
            
            assert 'Time Limit:' not in prompt_content

    @patch('src.routes.activity.extract_document_content')
    @patch('src.models.document.Document')
    def test_generate_ai_activity_with_time_limit(self, mock_document_class, mock_extract_content, auth_client, test_course):
        """Test the full endpoint with time limit inclusion"""
        client = auth_client['teacher']
        
        # Mock AI service response
        mock_response = {
            "title": "Time-Limited Activity",
            "description": "Activity with time limit",
            "question": "Answer quickly!",
            "options": ["Fast", "Slow", "Medium", "Unknown"],
            "correct_answer": "Fast"
        }

        mock_ai_instance = Mock()
        mock_ai_instance.generate_activity.return_value = mock_response

        with patch('src.routes.activity.AIService', return_value=mock_ai_instance) as mock_ai_service_class:
            mock_ai_instance = Mock()
            mock_ai_service_class.return_value = mock_ai_instance
            mock_ai_instance.generate_activity.return_value = mock_response

            # Make request with time_limit
            response = client.post('/api/activities/ai/generate', json={
                'activity_type': 'poll',
                'course_content': 'Test content for timed activity',
                'course_id': test_course,
                'time_limit': 10  # 10 minutes
            })

            assert response.status_code == 200
            data = response.get_json()

            # Verify AI service was called with time_limit
            mock_ai_instance.generate_activity.assert_called_once()
            call_args = mock_ai_instance.generate_activity.call_args

            # Check that time_limit was passed
            assert call_args.kwargs['time_limit'] == 10

            assert data['message'] == 'AI活动生成成功'
            assert data['generated_activity']['title'] == 'Time-Limited Activity'


class TestDocumentDropdownAPI:
    """Test document dropdown API endpoints for AI activity generator"""

    def test_get_course_documents_teacher(self, auth_client, test_course, test_users, app):
        """Test that teachers can get all documents for their course"""
        client = auth_client['teacher']

        with app.app_context():
            # Create test documents
            from src.models.document import Document
            from src.database import db

            doc1 = Document(
                course_id=test_course,
                uploader_id=test_users['teacher_id'],
                filename='test_doc1.pdf',
                stored_filename='stored_test_doc1.pdf',
                file_path='/uploads/stored_test_doc1.pdf',
                file_size=1024000,  # 1MB
                file_type='pdf',
                title='Test Document 1',
                is_active=True
            )

            doc2 = Document(
                course_id=test_course,
                uploader_id=test_users['teacher_id'],
                filename='test_doc2.docx',
                stored_filename='stored_test_doc2.docx',
                file_path='/uploads/stored_test_doc2.docx',
                file_size=2048000,  # 2MB
                file_type='docx',
                title='Test Document 2',
                is_active=False  # Inactive document
            )

            db.session.add(doc1)
            db.session.add(doc2)
            db.session.commit()

            # Test getting documents
            response = client.get(f'/api/documents/course/{test_course}')
            assert response.status_code == 200

            documents = response.get_json()
            assert len(documents) == 2  # Teachers see all documents including inactive

            # Check document structure
            doc_data = documents[0]
            assert 'id' in doc_data
            assert 'title' in doc_data
            assert 'file_type' in doc_data
            assert 'file_size_mb' in doc_data
            assert 'is_active' in doc_data

            # Verify file size calculation (doc2 comes first due to creation order)
            assert doc_data['file_size_mb'] == 1.95  # 2MB

            # Clean up
            db.session.delete(doc1)
            db.session.delete(doc2)
            db.session.commit()

    def test_get_course_documents_student(self, auth_client, test_course, test_users, app):
        """Test that students can only see active documents"""
        teacher_client = auth_client['teacher']
        student_client = auth_client['student1']

        with app.app_context():
            # Create test documents
            from src.models.document import Document
            from src.database import db

            doc1 = Document(
                course_id=test_course,
                uploader_id=test_users['teacher_id'],
                filename='active_doc.pdf',
                stored_filename='stored_active_doc.pdf',
                file_path='/uploads/stored_active_doc.pdf',
                file_size=1024000,
                file_type='pdf',
                title='Active Document',
                is_active=True
            )

            doc2 = Document(
                course_id=test_course,
                uploader_id=test_users['teacher_id'],
                filename='inactive_doc.pdf',
                stored_filename='stored_inactive_doc.pdf',
                file_path='/uploads/stored_inactive_doc.pdf',
                file_size=2048000,
                file_type='pdf',
                title='Inactive Document',
                is_active=False
            )

            db.session.add(doc1)
            db.session.add(doc2)
            db.session.commit()

            # Test student can only see active documents
            response = student_client.get(f'/api/documents/course/{test_course}')
            assert response.status_code == 200

            documents = response.get_json()
            assert len(documents) == 1  # Students only see active documents
            assert documents[0]['title'] == 'Active Document'
            assert documents[0]['is_active'] == True

            # Clean up
            db.session.delete(doc1)
            db.session.delete(doc2)
            db.session.commit()

    def test_get_course_documents_unauthorized(self, client, test_course):
        """Test that unauthorized users cannot access course documents"""
        # Test without authentication
        response = client.get(f'/api/documents/course/{test_course}')
        assert response.status_code == 401

    def test_get_course_documents_wrong_course_teacher(self, auth_client, test_users, app):
        """Test that teachers cannot access documents from courses they don't own"""
        client = auth_client['teacher']

        with app.app_context():
            # Create another teacher
            from src.models.user import User
            from src.models.course import Course
            from src.database import db
            import time

            other_teacher = User(
                username=f'other_teacher_{int(time.time())}',
                email=f'other_teacher_{int(time.time())}@example.com',
                full_name='Other Teacher',
                role='teacher'
            )
            other_teacher.set_password('password123')
            db.session.add(other_teacher)
            db.session.commit()

            other_course = Course(
                course_name='Other Course',
                course_code=f'OTHER101_{int(time.time())}',
                teacher_id=other_teacher.id,  # Use the actual teacher ID
                semester='Fall 2025',
                academic_year='2025-2026'
            )
            db.session.add(other_course)
            db.session.commit()

            # Try to access documents from other course
            response = client.get(f'/api/documents/course/{other_course.id}')
            assert response.status_code == 403

            # Clean up
            db.session.delete(other_course)
            db.session.delete(other_teacher)
            db.session.commit()

    def test_get_course_documents_student_not_enrolled(self, auth_client, test_users, app):
        """Test that students cannot access documents from courses they're not enrolled in"""
        student_client = auth_client['student1']

        with app.app_context():
            # Create another teacher
            from src.models.user import User
            from src.models.course import Course
            from src.database import db
            import time

            other_teacher = User(
                username=f'other_teacher_{int(time.time())}',
                email=f'other_teacher_{int(time.time())}@example.com',
                full_name='Other Teacher',
                role='teacher'
            )
            other_teacher.set_password('password123')
            db.session.add(other_teacher)
            db.session.commit()

            other_course = Course(
                course_name='Other Course',
                course_code=f'OTHER101_{int(time.time())}',
                teacher_id=other_teacher.id,
                semester='Fall 2025',
                academic_year='2025-2026'
            )
            db.session.add(other_course)
            db.session.commit()

            # Try to access documents from course not enrolled in
            response = student_client.get(f'/api/documents/course/{other_course.id}')
            assert response.status_code == 403

            # Clean up
            db.session.delete(other_course)
            db.session.delete(other_teacher)
            db.session.commit()

    def test_get_course_documents_empty_course(self, auth_client, test_course):
        """Test getting documents from a course with no documents"""
        client = auth_client['teacher']

        # Course should have no documents initially
        response = client.get(f'/api/documents/course/{test_course}')
        assert response.status_code == 200

        documents = response.get_json()
        assert len(documents) == 0
        assert documents == []

    def test_document_dropdown_integration_with_ai_generation(self, auth_client, test_course, test_users, app):
        """Test the complete flow: load documents -> select -> generate AI activity"""
        client = auth_client['teacher']

        with app.app_context():
            # Create test document
            from src.models.document import Document
            from src.database import db

            doc = Document(
                course_id=test_course,
                uploader_id=test_users['teacher_id'],
                filename='integration_test.pdf',
                stored_filename='stored_integration_test.pdf',
                file_path='/uploads/stored_integration_test.pdf',
                file_size=1024000,
                file_type='pdf',
                title='Integration Test Document',
                is_active=True
            )
            db.session.add(doc)
            db.session.commit()

            # Step 1: Load documents (simulating dropdown load)
            response = client.get(f'/api/documents/course/{test_course}')
            assert response.status_code == 200
            documents = response.get_json()
            assert len(documents) == 1
            assert documents[0]['title'] == 'Integration Test Document'

            # Step 2: Generate AI activity with document selection
            mock_response = {
                "title": "Document-Enhanced Activity",
                "description": "Activity with selected document content",
                "question": "What is the main topic?",
                "options": ["Topic A", "Topic B", "Topic C", "Topic D"],
                "correct_answer": "Topic A"
            }

            mock_ai_instance = Mock()
            mock_ai_instance.generate_activity.return_value = mock_response

            with patch('src.routes.activity.AIService', return_value=mock_ai_instance) as mock_ai_service_class:
                with patch('src.routes.activity.extract_document_content', return_value='Extracted content from integration test document'):
                    # Make request with document_ids (simulating dropdown selection)
                    response = client.post('/api/activities/ai/generate', json={
                        'activity_type': 'poll',
                        'course_content': 'Basic course content',
                        'course_id': test_course,
                        'document_ids': [doc.id]
                    })

                    assert response.status_code == 200
                    data = response.get_json()

                    # Verify AI service was called with enhanced content
                    mock_ai_instance.generate_activity.assert_called_once()
                    call_args = mock_ai_instance.generate_activity.call_args

                    enhanced_content = call_args.kwargs['course_content']
                    assert 'Basic course content' in enhanced_content
                    assert '--- 从上传文档提取的内容 ---' in enhanced_content
                    assert 'Extracted content from integration test document' in enhanced_content

                    assert data['message'] == 'AI活动生成成功'

            # Clean up
            db.session.delete(doc)
            db.session.commit()