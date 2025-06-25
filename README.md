# Resume Intelligence - AI-Powered Career Assistant

Resume Intelligence is a sophisticated web application designed to help job seekers optimize their resumes, practice for interviews, and discover relevant job opportunities. By leveraging the power of AI and natural language processing (NLP), this tool provides personalized feedback and data-driven insights to enhance your career prospects.

## ✨ Features

-   **📄 Resume Analysis:** Upload your resume (PDF) to receive an in-depth analysis, including an ATS (Applicant Tracking System) score, keyword optimization suggestions, and formatting feedback.
-   **💡 Dynamic Job Recommendations:** Get personalized job title recommendations based on the skills and experience identified in your resume.
-   **🧠 Skill-Based Interview Questions:** Generate practice interview questions tailored to the specific skills listed on your resume to help you prepare for technical interviews.
-   **👔 Professional UI:** A clean, modern, and intuitive user interface built with Bootstrap for a seamless user experience.
-   **🔒 Secure & Private:** Your data is processed securely, and your API keys are managed through environment variables, never exposed in the codebase.

## 🛠️ Tech Stack

-   **Backend:** Python, Flask
-   **Frontend:** HTML, CSS, JavaScript, Bootstrap
-   **AI & NLP:** OpenAI (GPT-4o), spaCy, NLTK
-   **Database:** SQLAlchemy (with SQLite for development)
-   **Deployment:** Git, GitHub

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   Python 3.8+
-   `pip` for package management
-   An [OpenAI API Key](https://platform.openai.com/api-keys)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nikunjraykundlia/resumeai.git
    cd ResumeIntelligence
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    A `requirements.txt` file is not yet present in the repository. You can create one using:
    ```bash
    pip freeze > requirements.txt
    ```
    Then install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    -   Create a file named `.env` in the root directory of the project.
    -   Add your OpenAI API key to this file:
        ```
        OPENAI_API_KEY='your_openai_api_key_here'
        ```

### Usage

1.  **Run the Flask application:**
    ```bash
    flask run
    ```

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000` to access the application.

3.  **Analyze your resume:**
    -   On the homepage, use the upload form to select your resume PDF.
    -   Click "Analyze" to see your detailed resume analysis, job recommendations, and more.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or want to add new features, please feel free to:

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request