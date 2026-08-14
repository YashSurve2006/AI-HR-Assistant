# 🤖 Lumina: Premium AI HR Assistant

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" />
</div>
<br />

**Lumina AI HR Assistant** is a sophisticated, single-page AI-driven web application designed to revolutionize HR operations. Built for academic excellence and industry-grade demonstrations, it features a premium glassmorphic UI, a robust Flask NLP backend, and dynamic data visualizations.

---

## 📸 Visual Showcase

<div align="center">
  <img src="images/dashboard-light.png" alt="AI HR Assistant Dashboard" width="100%" />
  <p><em>AI HR Assistant — Interactive Data Science & NLP Platform</em></p>
</div>

### 🎨 Premium Luminous Enterprise UI
The responsive SaaS interface supports persistent theme preferences. Powered by a newly integrated "Luminous Enterprise" glassmorphism design system, the interface leverages fluid optical depth, elegant SVG iconography, and dynamic Chart.js visualizations that adapt perfectly to the active theme.

<div align="center">
  <img src="images/dashboard-light.png" alt="Light Mode" width="48%" />
  <img src="images/dashboard-dark.png" alt="Dark Mode" width="48%" />
</div>

### 🤖 AI HR Chatbot & Intelligence Command Center
The chatbot acts as the central hub, utilizing an implemented NLP retrieval pipeline with text normalization and intent routing. It features a glowing "Super-Input" interface and interactive quick-start cards.

<img src="images/ai-chat.png" alt="AI Chatbot Interface" width="100%" />

### 📄 Embedded Resume Intelligence Card
Candidates can upload their resumes via drag-and-drop. The system performs NLP preprocessing to achieve skill extraction, generating a premium embedded chat widget with an animated circular ATS gauge, skill tags, and categorized breakdown metrics.

<img src="images/resume-analyzer.png" alt="Resume Analyzer Upload" width="100%" />
<br/><br/>
<img src="images/resume-results.png" alt="Resume Analyzer Results" width="100%" />

### 💼 AI Job Recommendations
By applying TF-IDF and Cosine Similarity, the recommendation engine matches extracted resume skills to our job database. It generates dynamic live job-platform search buttons with native SVG branding for LinkedIn, Indeed, Naukri, and Wellfound.

<img src="images/job-recommendations.png" alt="Job Recommendations" width="100%" />

### 🔎 Job Directory
Browse over 80 fictional corporate job roles. The directory includes robust search capabilities, beautifully styled dark-mode dropdowns for department, location, and experience, and native application links.

<img src="images/job-directory.png" alt="Job Directory" width="100%" />

### 📊 Employee Feedback Intelligence
Real-time sentiment analysis of employee satisfaction surveys. Our VADER Sentiment engine calculates polarity to provide department-level insights through a beautifully aligned CSS Grid layout, alongside an interactive, animated feedback stream featuring sentiment-coded badges.

<img src="images/employee-insights.png" alt="Employee Feedback Dashboard" width="100%" />

### 📱 Responsive Experience
Built on a fluid responsive grid, the chatbot scales perfectly (`calc(100vh - 160px)`) to provide an immersive experience across desktop, tablet, and mobile layouts.

<div align="center">
  <img src="images/mobile-view.png" alt="Mobile Responsive View" width="350px" />
</div>

---

## 🌟 Flagship Features

### 1. 🧠 Natural Language HR Chatbot
A 4-layer hybrid NLP pipeline that understands human conversational intent.
- **Zero Hardcoded Data**: Knowledge is derived entirely from `dataset/hr_faq.csv`.
- **Robust Normalization**: Handles casing, punctuation variations, typos, and conversational phrasing effortlessly.
- **Floating Command Center**: Designed with a sleek, floating Super-Input with a glowing halo border.

### 2. 📄 Intelligent Resume Analyzer
Automated candidate screening utilizing advanced Natural Language Processing.
- **PDF Data Extraction**: Seamlessly extracts raw text from candidate resumes.
- **Animated ATS Ring**: Presents the candidate's score on a visually stunning, premium SVG circular progress ring.
- **Technical Skill Recognition**: Automatically detects and displays skills as interactive frosted-glass tags.

### 3. 🎯 Smart Job Recommender & Directory
A TF-IDF ranking engine that connects talent to opportunities.
- **Live Search Integrations**: Beautiful, brand-colored SVG icon buttons for direct searches on **LinkedIn, Indeed, Naukri, Wellfound, and Internshala**.
- **Interactive Directory**: Search and filter using native `<select>` dropdowns fully customized for the dark glassmorphism aesthetic.

### 4. 📊 Real-Time Feedback Analytics
Deep sentiment analysis of employee satisfaction surveys.
- **Dynamic Dashboards**: Visualizes organizational health using properly scaled CSS grids (`.charts-grid`, `.insights-stats`).
- **Interactive Stream**: A scrolling feed of employee feedback styled as frosted glass cards with interactive hover-slides and precise VADER polarity badges.

### 5. 🎨 Premium "Luminous Enterprise" User Interface
A stunning frontend engineered entirely with Vanilla JS and pure CSS.
- **Glassmorphism Design**: Features translucent, blurred card surfaces (`backdrop-filter: blur(20px)`) and a deep indigo-charcoal gradient background.
- **Advanced Sizing**: A fully immersive `1600px` max-width and properly calculated viewport heights (`vh`) for the chat environment.
- **Top-Tier Typography**: Utilizes the geometric **Outfit** font for headings and **Inter** for data readability.

---

## 🛠️ Technology Stack

| Architecture Layer | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3, Flask |
| **Machine Learning / NLP** | Scikit-Learn (TF-IDF, Cosine Similarity), NLTK, VADER Sentiment |
| **Data Processing** | Pandas, PyPDF2 |
| **Frontend Structure** | HTML5, CSS3 (CSS Variables, Flexbox, CSS Grid) |
| **Frontend Logic** | Vanilla JavaScript (ES6+), Fetch API |
| **Data Visualization** | Chart.js |

---

## 📂 Project Structure

```text
📁 AI-HR-Assistant
├── 📁 backend
│   ├── app.py                  # Main Flask Server & API Routes
│   ├── job_recommender.py      # TF-IDF Cosine Similarity Engine
│   └── resume_analyzer.py      # NLP PDF parsing and Skill Extraction
├── 📁 frontend
│   ├── index.html              # Main Single-Page Application
│   ├── 📁 css
│   │   └── style.css           # Premium Glassmorphic Design System
│   └── 📁 js
│       └── script.js           # API Fetching, Chart Rendering, Theme Logic
├── 📁 dataset
│   ├── hr_faq.csv              # Chatbot Knowledge Base (120+ entries)
│   ├── jobs.csv                # Job Directory (80+ realistic roles)
│   └── employee_feedback.csv   # Mock Employee Satisfaction Data
├── test_full.py                # Comprehensive Backend Integration Tests
├── requirements.txt            # Python Dependencies
└── README.md                   # You are here
```

---

## 🚀 Setup & Installation

Follow these steps to run the project locally.

### 1. Clone & Setup Environment
Ensure you have Python 3.8+ installed on your system.

```bash
# Clone the repository (if applicable)
git clone <repository_url>
cd AI-HR-Assistant

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Backend API
The Flask backend serves all the AI and data endpoints.
```bash
python backend/app.py
```
*The backend will initialize the NLP models and start on `http://127.0.0.1:5000`.*

### 4. Run Frontend Application
Open a new terminal window, navigate to the `frontend` folder, and start a static server.
```bash
cd frontend
python -m http.server 8080 --bind 127.0.0.1
```
*Access the application by navigating to `http://127.0.0.1:8080` in your browser.*

---

## ✅ Comprehensive Testing

This project includes a robust integration test suite to verify backend endpoints, NLP responses, and data consistency.

```bash
python test_full.py
```
*Validates 81/81 assertions ensuring the stability of the `/api/health`, `/api/chat`, `/api/resume/analyze`, `/api/resume/recommend`, and `/api/dashboard` endpoints.*

---

> **Note for Evaluators:** This project adheres strictly to zero hard-coding principles. All machine learning recommendations, HR policies, and job listings are driven entirely by the `dataset/` CSV files, ensuring realistic behavior in production environments.
