# Study-Bud

![Study-Bud Logo](static/images/avatar.svg)

## A Discord-style platform for collaborative study groups

Study-Bud is a robust Django application that facilitates seamless study group collaboration, messaging, and resource sharing. It provides a Discord-style interface where users can create topic-based rooms, join existing ones, and communicate with participants through text messages, file sharing, and polls.

### ✨ Live Demo
[https://study-bud.example.com](https://study-bud.example.com)

## 🚀 Features

- **User Authentication & Management**
  - Email-based registration and login
  - Profile customization with avatars
  - Account recovery via email

- **Study Rooms**
  - Create public or private study rooms
  - Topic-based organization
  - Room hosting with participant management

- **Messaging System**
  - Real-time chat in rooms
  - File and image sharing
  - Emoji reactions
  - Message history

- **Interactive Features**
  - Create and participate in polls
  - Private room access control
  - Join request management

- **AI Integration with GROQ**
  - AI-assisted chat for study help
  - Automated quiz generation
  - Customizable difficulty levels
  - Multiple AI model options

- **Complete REST API**
  - Comprehensive API for all functionality
  - JWT authentication
  - Swagger documentation
  - Programmatic access

## 📋 Requirements

- Python 3.10+
- Django 5.1.6
- Django REST Framework 3.14.0
- GROQ API key for AI features
- See `requirements.txt` for complete list

## 🔧 Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/study-bud.git
   cd study-bud
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create an environment file:
   ```bash
   # Create a .env file in the project root with:
   GROQ_API_KEY=your_groq_api_key_here
   ```

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

9. Access the application at `http://127.0.0.1:8000/`

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build --build-arg GROQ_API_KEY=your_api_key -t study-bud:latest .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 study-bud:latest
   ```

3. Access the application at `http://localhost:8000/`

## 🧪 Testing

Run the test suite with:
```bash
python manage.py test
```

Run specific test modules:
```bash
python manage.py test base.tests.test_api
python manage.py test base.tests.test_models
```

## 📚 Documentation

Comprehensive documentation is available in the following formats:

- **Markdown**: [StudyBud_Documentation.md](StudyBud_Documentation.md)
- **LaTeX/PDF**: [StudyBud_Documentation.tex](StudyBud_Documentation.tex)

To generate the PDF documentation:
1. Install a LaTeX distribution like MiKTeX (Windows) or MacTeX (macOS)
2. Compile the LaTeX document:
   ```bash
   pdflatex StudyBud_Documentation.tex
   pdflatex StudyBud_Documentation.tex  # Run twice for TOC generation
   ```

### API Documentation

Interactive API documentation is available at `/api/docs/` when the application is running.

## 🌟 Key Features Breakdown

### Room System
Create topic-specific study rooms where users can collaborate. Room owners can manage participants, and rooms can be set as public or private.

### Messaging System
Send text messages, share files, and use emoji reactions. The system supports images with preview capabilities and distinguishes system messages.

### Polls
Create polls within rooms to gather opinions or make decisions. Users can vote on options and see real-time results.

### Private Room Access Control
Private rooms require approval to join. Users request access, and hosts can approve or reject requests, with automatic participant tracking.

### AI Integration
The GROQ API powers two key AI features:
1. **AI Chat**: Get study assistance by interacting with the AI
2. **Quiz Generation**: Create customized topic-based quizzes with multiple-choice questions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Your Name - [@yourusername](https://twitter.com/yourusername) - email@example.com

Project Link: [https://github.com/yourusername/study-bud](https://github.com/yourusername/study-bud)

---

Made with ❤️ for collaborative learning
