# Multi-Question Quiz Implementation

```
Brief summary:

Major Features Implemented with detailed code examples:

1. Teacher - Create Multiple Question Quizzes
2. Teacher - View Multi-Question Quiz Details
3. Teacher - View Student Responses
4. Student - Display Multi-Question Quiz Form
5. Student - Submit Multi-Question Quiz Answers
6. Student - View Multi-Question Quiz Results
7. AI Generator - Multi-Question Quiz Support

✅ 4 Bugs Fixed with solutions:
Single Question Format Compatibility
Radio Button Name Conflicts
Option Index Management
AI Generator Answer Format

✅ Additional sections:
Database schema examples
Testing checklist
Future enhancement ideas
```

## Overview
This document summarizes the implementation of the multi-question quiz feature, which allows teachers to create quizzes with multiple questions and enables students to answer all questions in a single quiz session.

---

## Features Implemented

### 1. Teacher - Create Multiple Question Quizzes

#### Feature Description
Teachers can now add multiple questions to a single quiz activity, with each question having its own set of options and correct answer.

#### UI Changes
- Replaced single question form with dynamic multi-question system
- Added "Add Question" button to create unlimited questions
- Each question card includes:
  - Question text field
  - Multiple options with correct answer selection
  - Explanation field
  - Remove button

#### Code Example - Quiz Question Structure

```javascript
// New multi-question format in quiz configuration
function addQuizQuestion() {
    const questionsContainer = document.getElementById('quizQuestions');
    const questionIndex = questionsContainer.children.length;
    
    const questionDiv = document.createElement('div');
    questionDiv.className = 'quiz-question-item';
    questionDiv.dataset.questionIndex = questionIndex;
    questionDiv.style.cssText = 'padding: 20px; border: 2px solid #e1e5e9; border-radius: 12px; margin-bottom: 20px; background: #f8f9fa;';
    
    questionDiv.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #082f49;">Question ${questionIndex + 1}</h4>
            <button type="button" class="btn btn-danger" onclick="removeQuizQuestion(this)">Remove Question</button>
        </div>
        <div class="form-group">
            <label>Question Text:</label>
            <input type="text" class="quiz-question-text" placeholder="e.g., Which of the following is correct?">
        </div>
        <div class="form-group">
            <label>Options:</label>
            <div class="quiz-options-container">
                <!-- Options for this specific question -->
            </div>
            <button type="button" class="btn btn-secondary" onclick="addQuizOption(this)">Add Option</button>
        </div>
        <div class="form-group">
            <label>Explanation:</label>
            <textarea class="quiz-explanation" placeholder="Explain why this answer is correct" rows="3"></textarea>
        </div>
    `;
    
    questionsContainer.appendChild(questionDiv);
}
```

#### Data Collection on Submission

```javascript
// Collecting multiple questions data
} else if (selectedActivityType === 'quiz') {
    const questionItems = document.querySelectorAll('.quiz-question-item');
    
    if (questionItems.length === 0) {
        showMessage('Please add at least one question', 'error');
        return;
    }
    
    const questions = [];
    let hasError = false;
    
    questionItems.forEach((questionItem, qIndex) => {
        const questionText = questionItem.querySelector('.quiz-question-text').value.trim();
        const options = Array.from(questionItem.querySelectorAll('.option-input'))
            .map(input => input.value.trim()).filter(v => v);
        const correctAnswerRadio = questionItem.querySelector('input[type="radio"]:checked');
        const explanation = questionItem.querySelector('.quiz-explanation').value.trim();
        
        if (!questionText) {
            showMessage(`Please enter text for question ${qIndex + 1}`, 'error');
            hasError = true;
            return;
        }
        if (options.length < 2) {
            showMessage(`Question ${qIndex + 1} requires at least 2 options`, 'error');
            hasError = true;
            return;
        }
        if (!correctAnswerRadio) {
            showMessage(`Please select correct answer for question ${qIndex + 1}`, 'error');
            hasError = true;
            return;
        }
        
        questions.push({
            question: questionText,
            options: options,
            correct_answer: parseInt(correctAnswerRadio.value),
            explanation: explanation
        });
    });
    
    if (hasError) return;
    
    data.config = { questions: questions };
}
```

---

### 2. Teacher - View Multi-Question Quiz Details

#### Feature Description
When viewing quiz activity details, teachers can see all questions with their options, correct answers highlighted, and explanations.

#### Code Example - Display Logic

```javascript
// Display quiz configuration
} else if (activity.activity_type === 'quiz') {
    if (config.questions && Array.isArray(config.questions)) {
        // Multiple questions format
        config.questions.forEach((q, index) => {
            configHtml += `<div style="padding: 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 15px;">`;
            configHtml += `<h4 style="color: #082f49; margin-bottom: 10px;">Question ${index + 1}</h4>`;
            configHtml += `<div class="form-group"><label>Question Text:</label><p style="padding: 10px; background: white; border-radius: 5px;">${q.question}</p></div>`;
            
            if (q.options && Array.isArray(q.options)) {
                configHtml += `<div class="form-group"><label>Options:</label><ul style="padding: 10px; background: white; border-radius: 5px;">`;
                configHtml += q.options.map((opt, optIndex) => {
                    const isCorrect = q.correct_answer === optIndex;
                    return `<li style="color: ${isCorrect ? '#28a745' : 'inherit'}; font-weight: ${isCorrect ? 'bold' : 'normal'};">${opt} ${isCorrect ? '✓' : ''}</li>`;
                }).join('');
                configHtml += `</ul></div>`;
            }
            
            if (q.explanation) {
                configHtml += `<div class="form-group"><label>Explanation:</label><p style="padding: 10px; background: white; border-radius: 5px;">${q.explanation}</p></div>`;
            }
            configHtml += `</div>`;
        });
    } else {
        // Old single question format (backward compatibility)
        // ... handle old format
    }
}
```

---

### 3. Teacher - View Student Responses for Multiple Questions

#### Feature Description
Teachers can view detailed student responses showing answers to all questions, with visual indicators for correct/incorrect answers and overall score.

#### Code Example - Response Display

```javascript
function displayResponseData(responseData, activityType, config) {
    let html = '';
    
    if (activityType === 'quiz') {
        if (responseData.answers && Array.isArray(responseData.answers)) {
            // Multiple questions format
            const questions = config.questions || [];
            html += '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">';
            
            responseData.answers.forEach((answer, index) => {
                const question = questions[index];
                const isCorrect = answer.is_correct;
                const selectedOption = question && question.options && answer.option_index !== undefined 
                    ? question.options[answer.option_index] 
                    : answer.selected_option || 'Not selected';
                
                html += `<div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #dee2e6;">`;
                html += `<strong>Question ${index + 1}:</strong> ${question ? question.question : 'Unknown'}<br>`;
                html += `<strong>Selected Answer:</strong> ${selectedOption}`;
                
                if (isCorrect !== undefined) {
                    html += `<br><strong>Result:</strong> <span style="color: ${isCorrect ? '#28a745' : '#dc3545'}; font-weight: bold;">
                        ${isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </span>`;
                    
                    if (!isCorrect && question && question.correct_answer !== undefined && question.options) {
                        html += `<br><strong>Correct Answer:</strong> <span style="color: #28a745;">${question.options[question.correct_answer]}</span>`;
                    }
                }
                html += `</div>`;
            });
            
            // Calculate and display overall score
            const correctCount = responseData.answers.filter(a => a.is_correct).length;
            const totalQuestions = responseData.answers.length;
            const percentage = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;
            
            html += `<div style="margin-top: 15px; padding-top: 15px; border-top: 2px solid #082f49; font-weight: bold; color: #082f49;">
                Overall Score: ${correctCount}/${totalQuestions} (${percentage}%)
            </div>`;
            html += '</div>';
        }
    }
    
    return html;
}
```

---

### 4. Student - Display Multi-Question Quiz Form

#### Feature Description
Students see all quiz questions in a clean, numbered format where they can select answers for each question before submitting.

#### Code Example - Quiz Form Generation

```javascript
function generateQuizForm(config) {
    // Check if it's multiple questions format
    if (config.questions && Array.isArray(config.questions)) {
        let html = '<div class="response-form">';
        html += '<h3 style="margin-bottom: 20px;">Quiz - Answer all questions</h3>';
        
        config.questions.forEach((q, qIndex) => {
            const question = q.question || 'Question';
            const options = q.options || [];
            
            html += `
                <div style="padding: 20px; background: white; border-radius: 12px; margin-bottom: 20px; border: 2px solid #e1e5e9;">
                    <h4 style="color: #082f49; margin-bottom: 15px;">Question ${qIndex + 1}</h4>
                    <p style="margin-bottom: 15px; font-size: 16px; color: #333;">${question}</p>
                    <div class="poll-options">
                        ${options.map((option, oIndex) => `
                            <div class="poll-option" onclick="selectQuizOption(${qIndex}, ${oIndex})" data-q="${qIndex}" data-o="${oIndex}">
                                ${option}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        
        html += '<button class="btn btn-success" onclick="submitQuizResponse()" style="margin-top: 15px; width: 100%; padding: 15px; font-size: 16px;">Submit Quiz</button>';
        html += '</div>';
        
        return html;
    }
}
```

---

### 5. Student - Submit Multi-Question Quiz Answers

#### Feature Description
Students can submit answers for all questions in one submission, with validation ensuring all questions are answered.

#### Code Example - Submission Logic

```javascript
async function submitQuizResponse() {
    const config = currentActivity.config || {};
    
    // Check if it's multiple questions format
    if (config.questions && Array.isArray(config.questions)) {
        const answers = [];
        let hasError = false;
        
        // Collect answers for all questions
        for (let qIndex = 0; qIndex < config.questions.length; qIndex++) {
            const selectedOption = document.querySelector(`.poll-option.selected[data-q="${qIndex}"]`);
            
            if (!selectedOption) {
                showMessage(`Please answer question ${qIndex + 1}`, 'error');
                hasError = true;
                break;
            }
            
            const question = config.questions[qIndex];
            const selectedIndex = parseInt(selectedOption.dataset.o);
            const correctAnswer = question.correct_answer;
            const isCorrect = selectedIndex === correctAnswer;
            
            answers.push({
                question_index: qIndex,
                selected_option: selectedOption.textContent.trim(),
                option_index: selectedIndex,
                is_correct: isCorrect
            });
        }
        
        if (hasError) return;
        
        // Calculate overall score
        const correctCount = answers.filter(a => a.is_correct).length;
        const totalQuestions = answers.length;
        const score = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;
        
        const responseData = {
            answers: answers,
            total_questions: totalQuestions,
            correct_count: correctCount,
            score: score
        };
        
        await submitResponse(responseData);
    }
}
```

---

### 6. Student - View Multi-Question Quiz Results

#### Feature Description
Students can view their quiz results with detailed feedback for each question, showing their answer, correctness, correct answer (if wrong), and explanations.

#### Code Example - Results Display

```javascript
function displayResponseData(responseData, activityType, config) {
    if (activityType === 'quiz') {
        if (responseData.answers && Array.isArray(responseData.answers)) {
            // Multiple questions format
            const questions = config.questions || [];
            html += '<div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">';
            html += '<h4 style="margin-bottom: 15px; color: #082f49;">Your Answers</h4>';
            
            responseData.answers.forEach((answer, index) => {
                const question = questions[index];
                const isCorrect = answer.is_correct;
                const selectedOption = question && question.options && answer.option_index !== undefined 
                    ? question.options[answer.option_index] 
                    : answer.selected_option || 'Not selected';
                
                html += `<div style="margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid ${isCorrect ? '#28a745' : '#dc3545'};">`;
                html += `<div style="font-weight: bold; color: #082f49; margin-bottom: 10px;">Question ${index + 1}</div>`;
                html += `<div style="margin-bottom: 10px; color: #666;">${question ? question.question : 'Unknown'}</div>`;
                html += `<div style="padding: 10px; background: #f8f9fa; border-radius: 5px; margin-bottom: 10px;">
                    <strong>Your Answer:</strong> ${selectedOption}
                </div>`;
                
                if (isCorrect !== undefined) {
                    html += `<div style="padding: 10px; background: ${isCorrect ? '#d4edda' : '#f8d7da'}; border-radius: 5px; margin-bottom: 10px;">
                        <strong>Result:</strong> 
                        <span style="color: ${isCorrect ? '#155724' : '#721c24'}; font-weight: bold;">
                            ${isCorrect ? '✓ Correct' : '✗ Incorrect'}
                        </span>
                    </div>`;
                    
                    // Show correct answer if wrong
                    if (!isCorrect && question && question.correct_answer !== undefined && question.options) {
                        html += `<div style="padding: 10px; background: #d4edda; border-radius: 5px; margin-bottom: 10px;">
                            <strong>Correct Answer:</strong> <span style="color: #155724;">${question.options[question.correct_answer]}</span>
                        </div>`;
                    }
                    
                    // Show explanation if available
                    if (question && question.explanation) {
                        html += `<div style="padding: 10px; background: #e3f2fd; border-radius: 5px;">
                            <strong>Explanation:</strong> ${question.explanation}
                        </div>`;
                    }
                }
                html += `</div>`;
            });
            
            // Show overall score
            if (responseData.total_questions && responseData.correct_count !== undefined) {
                const percentage = responseData.score || 0;
                const colorClass = percentage >= 70 ? '#28a745' : percentage >= 50 ? '#ffc107' : '#dc3545';
                
                html += `<div style="margin-top: 20px; padding: 20px; background: white; border-radius: 8px; text-align: center; border: 2px solid ${colorClass};">
                    <h3 style="color: ${colorClass}; margin-bottom: 10px;">Overall Score</h3>
                    <div style="font-size: 32px; font-weight: bold; color: ${colorClass};">
                        ${responseData.correct_count}/${responseData.total_questions}
                    </div>
                    <div style="font-size: 24px; color: #666; margin-top: 5px;">
                        ${percentage}%
                    </div>
                </div>`;
            }
            html += '</div>';
        }
    }
    
    return html;
}
```

---

### 7. AI Generator - Multi-Question Quiz Support

#### Feature Description
The AI Activity Generator can now create quizzes with multiple questions and automatically convert them to the proper format.

#### Code Example - AI Integration

```javascript
async function useAIGeneratedActivity() {
    if (!aiGeneratedActivityData || !aiGeneratedCourseId) {
        showMessage('No AI generated activity data found', 'error');
        return;
    }
    
    const { activity, activityType } = aiGeneratedActivityData;
    let config = {};
    
    if (activityType === 'quiz') {
        // Handle quiz with questions array (multiple questions format)
        if (activity.questions && Array.isArray(activity.questions) && activity.questions.length > 0) {
            const questions = activity.questions.map(q => {
                // Ensure correct_answer is a number index
                let correctAnswerIndex = q.correct_answer;
                if (typeof correctAnswerIndex === 'string') {
                    // Try to find the index if it's a string matching an option
                    const foundIndex = q.options ? q.options.findIndex(opt => opt === correctAnswerIndex) : -1;
                    correctAnswerIndex = foundIndex >= 0 ? foundIndex : 0;
                } else if (typeof correctAnswerIndex !== 'number') {
                    correctAnswerIndex = 0;
                }
                
                return {
                    question: q.question || '',
                    options: q.options || [],
                    correct_answer: correctAnswerIndex,
                    explanation: q.explanation || ''
                };
            });
            
            config = { questions: questions };
        } else {
            // Fallback to single question format (backward compatibility)
            let correctAnswerIndex = activity.correct_answer;
            if (typeof correctAnswerIndex === 'string') {
                const foundIndex = activity.options ? activity.options.findIndex(opt => opt === correctAnswerIndex) : -1;
                correctAnswerIndex = foundIndex >= 0 ? foundIndex : 0;
            } else if (typeof correctAnswerIndex !== 'number') {
                correctAnswerIndex = 0;
            }
            
            config = {
                questions: [{
                    question: activity.question || '',
                    options: activity.options || [],
                    correct_answer: correctAnswerIndex,
                    explanation: activity.explanation || ''
                }]
            };
        }
    }
    
    // Create activity with proper config
    const data = {
        title: activity.title || 'AI Generated Activity',
        description: activity.description || '',
        activity_type: activityType,
        course_id: aiGeneratedCourseId,
        duration_minutes: activity.time_limit ? Math.floor(activity.time_limit / 60) : 10,
        config: config
    };
    
    // Submit to API...
}
```

---

## Bugs Fixed

### Bug 1: Single Question Format Compatibility
**Issue:** Old quizzes with single question format were not displaying correctly after implementing multi-question feature.

**Fix:** Added backward compatibility checks in all display and processing functions:

```javascript
// Example backward compatibility check
if (config.questions && Array.isArray(config.questions)) {
    // Handle new multi-question format
    config.questions.forEach((q, index) => {
        // Process each question
    });
} else {
    // Handle old single question format
    if (config.question) {
        // Process single question
    }
}
```

### Bug 2: Radio Button Name Conflicts
**Issue:** When multiple questions were added, radio buttons for correct answers had the same `name` attribute, causing conflicts.

**Fix:** Unique radio button names for each question:

```javascript
// Each question gets its own radio button group
<input type="radio" name="correctAnswer_${questionIndex}" value="${optionCount}">
```

### Bug 3: Option Index Management
**Issue:** When removing options or questions, indices were not updated, causing submission errors.

**Fix:** Added update functions to maintain correct indices:

```javascript
function updateQuizQuestionNumbers() {
    const questions = document.querySelectorAll('.quiz-question-item');
    questions.forEach((item, index) => {
        item.dataset.questionIndex = index;
        const header = item.querySelector('h4');
        if (header) {
            header.textContent = `Question ${index + 1}`;
        }
        // Update radio button names
        const radios = item.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.name = `correctAnswer_${index}`;
        });
    });
}
```

### Bug 4: AI Generator Answer Format
**Issue:** AI sometimes returned correct answers as strings instead of numeric indices, causing validation errors.

**Fix:** Added answer format conversion:

```javascript
// Convert string answers to numeric indices
let correctAnswerIndex = q.correct_answer;
if (typeof correctAnswerIndex === 'string') {
    const foundIndex = q.options ? q.options.findIndex(opt => opt === correctAnswerIndex) : -1;
    correctAnswerIndex = foundIndex >= 0 ? foundIndex : 0;
} else if (typeof correctAnswerIndex !== 'number') {
    correctAnswerIndex = 0;
}
```

---

## Database Schema

### Quiz Configuration Format

```javascript
// New multi-question format stored in activity.config
{
    "questions": [
        {
            "question": "What is the capital of France?",
            "options": ["London", "Paris", "Berlin", "Madrid"],
            "correct_answer": 1,  // Index of correct option (0-based)
            "explanation": "Paris is the capital and largest city of France."
        },
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1,
            "explanation": "2 + 2 equals 4."
        }
    ]
}
```

### Student Response Format

```javascript
// Student response stored in response.response_data
{
    "answers": [
        {
            "question_index": 0,
            "selected_option": "Paris",
            "option_index": 1,
            "is_correct": true
        },
        {
            "question_index": 1,
            "selected_option": "5",
            "option_index": 2,
            "is_correct": false
        }
    ],
    "total_questions": 2,
    "correct_count": 1,
    "score": 50
}
```

---

## Testing Checklist

- [x] Create quiz with single question
- [x] Create quiz with multiple questions (2-10 questions)
- [x] Add/remove questions dynamically
- [x] Add/remove options for each question
- [x] Select correct answer for each question
- [x] View quiz details showing all questions
- [x] Student participates in multi-question quiz
- [x] Student cannot submit without answering all questions
- [x] Student receives immediate feedback with scores
- [x] Teacher views student responses for all questions
- [x] Teacher sees overall score statistics
- [x] AI generates multi-question quiz
- [x] AI-generated quiz displays correctly
- [x] AI-generated quiz can be used successfully
- [x] Backward compatibility with old single-question quizzes
- [x] Proper error handling and validation

---

## Future Enhancements

1. **Question Bank**: Allow teachers to save and reuse questions
2. **Question Shuffling**: Randomize question order for each student
3. **Option Shuffling**: Randomize option order to prevent cheating
4. **Time Limits per Question**: Set individual time limits for each question
5. **Question Categories**: Organize questions by topic/difficulty
6. **Partial Credit**: Award points for partially correct answers
7. **Question Import/Export**: Import questions from CSV/JSON files
8. **Rich Text Support**: Add formatting, images, and code snippets to questions
9. **Question Analytics**: Track which questions students find most difficult
10. **Adaptive Quizzes**: Adjust difficulty based on student performance

---

## Conclusion

The multi-question quiz feature has been successfully implemented with full backward compatibility. Teachers can now create comprehensive quizzes with multiple questions, and students can complete them in a single session with detailed feedback. The AI generator integration provides an automated way to create multi-question quizzes, significantly reducing teacher workload while maintaining quality.
