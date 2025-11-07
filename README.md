# Smart Classroom Platform

A Flask-based smart classroom interaction platform with AI integration. Supports teachers in creating various learning activities, student participation, and real-time data analysis.

## Features

### Teacher Features
- Course management: Create and manage courses, import student lists
- Activity creation: Support for multiple activity types (polls, quizzes, word clouds, short answers, mini games)
- AI integration: Automatically generate learning activities based on course content
- Real-time monitoring: View student participation and activity progress
- Data analysis: Get detailed learning analytics reports

### Student Features
- Course enrollment: Register for courses of interest
- Activity participation: Participate in various interactive learning activities
- Real-time feedback: Receive immediate learning feedback
- Progress tracking: View personal learning progress and grades

### AI Features
- Smart activity generation: Automatically generate learning activities based on course content
- Answer analysis: Automatically analyze student responses and identify similar answers
- Personalized feedback: Generate personalized learning feedback for each student
- Learning insights: Provide learning data insights and suggestions

### Admin Features
- User management: Manage teacher, student, and administrator accounts
- System monitoring: Monitor system usage and performance
- Data backup: System data backup and recovery
- Leaderboard: Course leaderboards and learning incentives

## Technology Stack

### Backend
- Flask: Python web framework
- SQLAlchemy: ORM for database operations
- SQLite: Lightweight database
- OpenAI API: AI functionality integration
- Werkzeug: Password security handling

### Frontend
- HTML5: Semantic markup
- CSS3: Modern responsive design
- JavaScript: Native JS for interactions
- Chart.js: Data visualization

### Project Structure
```
smart-classroom-platform/
├── src/
│   ├── models/              # Data models
│   │   ├── user.py         # User model
│   │   ├── course.py       # Course model
│   │   ├── activity.py     # Activity model
│   │   ├── response.py     # Response model
│   │   └── analytics.py    # Analytics model
│   ├── routes/              # API routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── course.py       # Course routes
│   │   ├── activity.py     # Activity routes
│   │   ├── response.py     # Response routes
│   │   ├── analytics.py   # Analytics routes
│   │   └── admin.py        # Admin routes
│   ├── ai/                  # AI functionality
│   │   └── ai_service.py   # AI service
│   ├── static/              # Static files
│   │   ├── index.html      # Home page
│   │   ├── teacher.html    # Teacher interface
│   │   ├── student.html    # Student interface
│   │   └── admin.html      # Admin interface
│   └── database.py         # Database configuration
├── database/                # Database files
├── main.py                 # Application entry point
├── wsgi.py                 # WSGI configuration
├── requirements.txt        # Dependencies
├── Procfile               # Heroku deployment
└── README.md              # Project documentation
```

## Getting Started

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd smart-classroom-platform
```

2. Create a virtual environment
```bash
python -m venv venv
```

3. Activate the virtual environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file in the project root
2. Add your OpenAI API key:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### Running the Application

```bash
python main.py
```

The application will start at `http://localhost:5000`.

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user information
- `PUT /api/auth/profile` - Update user information

### Course Endpoints
- `GET /api/courses/` - Get course list
- `POST /api/courses/` - Create course
- `GET /api/courses/<id>` - Get course details
- `PUT /api/courses/<id>` - Update course
- `POST /api/courses/<id>/enroll` - Enroll in course
- `POST /api/courses/<id>/import-students` - Import students

### Activity Endpoints
- `GET /api/activities/` - Get activity list
- `POST /api/activities/` - Create activity
- `GET /api/activities/<id>` - Get activity details
- `PUT /api/activities/<id>` - Update activity
- `POST /api/activities/<id>/start` - Start activity
- `POST /api/activities/<id>/stop` - Stop activity
- `POST /api/activities/ai/generate` - AI generate activity

### Response Endpoints
- `POST /api/responses/` - Submit response
- `GET /api/responses/activity/<id>` - Get activity responses
- `POST /api/responses/<id>/feedback` - Add feedback
- `POST /api/responses/ai/analyze/<id>` - AI analyze response

### Analytics Endpoints
- `GET /api/analytics/dashboard` - Get dashboard data
- `GET /api/analytics/leaderboard/<id>` - Get leaderboard
- `GET /api/analytics/activity/<id>/analytics` - Get activity analytics

### Admin Endpoints
- `GET /api/admin/users` - Get all users
- `GET /api/admin/stats` - Get system statistics
- `POST /api/admin/backup` - Create backup

## User Interfaces

### Teacher Interface
- Course management: Create, edit, and delete courses
- Student management: Import student lists and view student information
- Activity creation: Manually create or AI-generate learning activities
- Real-time monitoring: View activity progress and student participation
- Data analysis: View detailed learning analytics reports

### Student Interface
- Course browsing: View available courses for enrollment
- Activity participation: Participate in various learning activities
- Grade viewing: View personal grades and feedback
- Progress tracking: View learning progress and participation statistics

### Admin Interface
- User management: Manage all user accounts
- System monitoring: Monitor system usage
- Data management: System data backup and recovery
- Statistical analysis: View overall system statistics

## AI Functionality

### Activity Generation
The system can automatically generate learning activities based on course content. Supported activity types include polls, quizzes, word clouds, short answer questions, and mini games. Teachers can review and optimize AI-generated content before publishing.

### Answer Analysis
Automatically analyze student responses to identify similarities and common themes. The system provides learning insights and improvement suggestions based on response patterns.

### Personalized Feedback
Generate personalized learning feedback for each student based on their response quality. The system provides constructive suggestions and learning guidance.

## Responsive Design

The platform is designed with mobile-first principles, featuring adaptive layouts that work across different screen sizes. Touch-friendly interactions and optimized page loading ensure a smooth user experience.

## Deployment

### Heroku Deployment
1. Create a Heroku application
2. Set environment variables
3. Push code to Heroku
4. Start the application

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "wsgi:app"]
```

## Security

- Password encryption using Werkzeug
- Secure session management
- Role-based access control
- Data validation on both frontend and backend

## Performance

- Database indexing for optimized query performance
- Caching mechanisms to reduce database load
- Asynchronous task processing for time-consuming operations
- CDN acceleration for static resources

## License

MIT License

## Contact

- Project maintainer: [Your Name]
- Email: [your-email@example.com]
- Repository: [GitHub Repository URL]

## Acknowledgments

Thanks to all developers and educators who have contributed to this project.

