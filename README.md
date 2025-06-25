<div align="center">
  <img src="https://github.com/user-attachments/assets/54027d97-7ce6-4ca2-832c-5643b7adc0ef" alt="Resume AI Logo" width="200"/>
</div>

# Resume AI - AI-Powered Career Assistant

  *Accelerate your job search with AI-powered resume analysis, optimization, and job matching.*
</div>

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

Resume AI is a sophisticated web application that helps job seekers optimize their resumes, prepare for interviews, and discover relevant job opportunities. By leveraging AI and NLP technologies, the application provides:

- **Comprehensive Resume Analysis**: Detailed ATS score, keyword optimization, and formatting feedback
- **Personalized Job Recommendations**: Based on your skills and experience
- **Skill-Based Interview Prep**: Tailored practice questions for technical interviews
- **Data-Driven Insights**: Visual analytics of your resume's strengths and weaknesses

---

## Key Features

### Automated Resume Analysis
- ATS Compatibility Scoring (0-100%)
- Keyword density and optimization suggestions
- Skills gap analysis
- Formatting and structure recommendations

### Career Enhancement Tools
- Job title matching based on your profile
- MAANG (Meta, Amazon, Apple, Netflix, Google) specific scoring
- Personalized interview question generator
- Job market trend insights

### User Experience
- Secure PDF upload and processing
- Clean, responsive Bootstrap interface
- Interactive results dashboard
- PDF report generation

---

## Technology Stack

### Backend
- **Python 3.12**
- **Flask** web framework
- **SQLAlchemy** ORM
- **PostgreSQL** database (Production)
- **SQLite** database (Development)

### AI/NLP Processing
- **spaCy** for NLP processing
- **scikit-learn** for machine learning
- **OpenAI GPT-4** for advanced analysis
- **PyTorch** for deep learning models

### Frontend
- **HTML5** / **CSS3**
- **JavaScript**
- **Bootstrap 5**
- **Chart.js** for visualizations

### Deployment
- **Render.com** cloud platform
- **GitHub Actions** CI/CD
- **Gunicorn** WSGI server

---

## Installation Guide

### Prerequisites
- Python 3.12
- PostgreSQL (for production)
- OpenAI API Key

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/nikunjraykundlia/resumeai.git
   cd resumeai
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

---

## Configuration

Create a `.env` file in the root directory with the following content:

```env
# .env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:password@localhost/resumeai
FLASK_SECRET_KEY=your_secret_key
DEBUG=True
```

### Environment Variables Explained
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI features)
- `DATABASE_URL`: Database connection URL
- `FLASK_SECRET_KEY`: Secret key for session security
- `DEBUG`: Set to False in production

---

## Project Structure

```
ResumeAI/
├── attached_assets/           # Dataset files
│   ├── expanded_skills_with_web_app_and_database.csv
│   └── job_title_des.csv
├── static/                    # Static assets
│   ├── css/                   # CSS files
│   ├── js/                    # JavaScript files
│   ├── img/                   # Image assets
│   └── images/                # Image assets
├── templates/                 # Flask templates
│   ├── advanced_analysis.html
│   ├── api_test.html
│   ├── chatbot.html
│   ├── cover_letter.html
│   ├── index.html
│   ├── job_match.html
│   ├── job_match_form.html
│   ├── job_recommendations.html
│   ├── layout.html
│   ├── login.html
│   ├── register.html
│   ├── resume_analysis.html
│   └── skills_test.html
├── utils/                     # Core functionality
│   ├── advanced_analyzer.py
│   ├── adzuna_api.py
│   ├── adzuna_enhanced.py
│   ├── api.py
│   ├── ats_scorer.py
│   ├── google_ai_helper.py
│   ├── job_matcher.py
│   ├── job_search_tips.py
│   ├── maang_ats_scorer.py
│   ├── ocr_processor.py
│   ├── openai_analyzer.py
│   ├── openai_helper.py
│   ├── resume_analyzer.py
│   ├── resume_suggestions.py
│   └── skills_extractor.py
├── tests/                     # Test cases
├── .env.example               # Environment template
├── app.py                     # Flask application
├── forms.py                   # WTForms definitions
├── models.py                  # Database models
├── requirements.txt           # Dependencies
├── runtime.txt                # Python version
└── README.md                  # This file
```

---

## Deployment

### Steps to deploy on Render.com
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Set start command:
   ```bash
   gunicorn app:app
   ```
5. Add environment variables from your `.env` file
6. Deploy!

### Post-Deployment
- Your application will be available at `https://your-app-name.onrender.com`
- Monitor logs in the Render dashboard
- Set up automatic deployments from GitHub

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request

Please ensure:
- All tests pass
- Code follows PEP8 style guide
- New features include appropriate tests

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

- **Project Lead**: Nikunj Raikundliya
- **Email**: nikunjraikundliya@gmail.com
- **GitHub**: [nikunjraykundlia](https://github.com/nikunjraykundlia)

---

## Acknowledgements

- OpenAI for their powerful language models
- spaCy for natural language processing capabilities
- Render.com for deployment hosting
- Bootstrap for UI components

---

*Empowering job seekers with AI-driven career assistance*
