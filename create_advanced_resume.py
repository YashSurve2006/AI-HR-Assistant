"""Generate a realistic, professionally formatted PDF resume for testing."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "uploads", "advanced_test_resume.pdf")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ── Colour palette ───────────────────────────────────────────────
PRIMARY   = HexColor("#1a1a2e")
ACCENT    = HexColor("#16213e")
LINK_CLR  = HexColor("#0e6ba8")
LIGHT_BG  = HexColor("#f0f0f0")
DIVIDER   = HexColor("#cccccc")

# ── Styles ───────────────────────────────────────────────────────
styles = getSampleStyleSheet()

sName = ParagraphStyle("Name", parent=styles["Title"],
    fontSize=22, leading=26, textColor=PRIMARY, alignment=TA_LEFT,
    spaceAfter=2)

sTagline = ParagraphStyle("Tagline", parent=styles["Normal"],
    fontSize=11, leading=14, textColor=HexColor("#555555"),
    spaceAfter=4, alignment=TA_LEFT)

sContact = ParagraphStyle("Contact", parent=styles["Normal"],
    fontSize=9, leading=12, textColor=HexColor("#444444"),
    spaceAfter=8, alignment=TA_LEFT)

sSectionHead = ParagraphStyle("SectionHead", parent=styles["Heading2"],
    fontSize=12, leading=15, textColor=PRIMARY,
    spaceBefore=10, spaceAfter=4,
    borderWidth=0, borderPadding=0)

sSubHead = ParagraphStyle("SubHead", parent=styles["Heading3"],
    fontSize=10.5, leading=13, textColor=ACCENT,
    spaceBefore=6, spaceAfter=2)

sBody = ParagraphStyle("Body", parent=styles["Normal"],
    fontSize=9.5, leading=13, textColor=black,
    alignment=TA_JUSTIFY, spaceAfter=2)

sBullet = ParagraphStyle("Bullet", parent=sBody,
    leftIndent=14, bulletIndent=4, spaceAfter=1.5,
    bulletFontName="Helvetica", bulletFontSize=7)

sMeta = ParagraphStyle("Meta", parent=styles["Normal"],
    fontSize=9, leading=11, textColor=HexColor("#666666"),
    spaceAfter=2)

sSkillLabel = ParagraphStyle("SkillLabel", parent=styles["Normal"],
    fontSize=9, leading=12, textColor=PRIMARY, fontName="Helvetica-Bold")

sSkillValue = ParagraphStyle("SkillValue", parent=styles["Normal"],
    fontSize=9, leading=12, textColor=HexColor("#333333"))

# ── Helper functions ─────────────────────────────────────────────
def section_heading(title):
    return [
        Spacer(1, 3*mm),
        HRFlowable(width="100%", thickness=0.6, color=DIVIDER, spaceAfter=2),
        Paragraph(title.upper(), sSectionHead),
    ]

def bullet(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", sBullet)

def divider():
    return HRFlowable(width="100%", thickness=0.3, color=DIVIDER, spaceBefore=3, spaceAfter=3)

# ── Build document ───────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=15*mm, bottomMargin=15*mm,
)

story = []

# ── Header ───────────────────────────────────────────────────────
story.append(Paragraph("ARJUN VIKRAM DESHMUKH", sName))
story.append(Paragraph(
    "Senior Full-Stack &amp; AI Engineer  |  5+ Years of Experience  |  "
    "Cloud-Native Solutions  |  Machine Learning &amp; NLP Specialist", sTagline))
story.append(Paragraph(
    "Pune, Maharashtra, India  &bull;  +91-98765-43210  &bull;  "
    "arjun.deshmukh@email.com  &bull;  linkedin.com/in/arjundeshmukh  &bull;  "
    "github.com/arjunvdeshmukh", sContact))

# ── Professional Summary ─────────────────────────────────────────
story.extend(section_heading("Professional Summary"))
story.append(Paragraph(
    "Results-driven Senior Full-Stack and AI Engineer with over 5 years of progressive "
    "experience in designing, developing, and deploying scalable web applications and "
    "data-driven machine learning solutions. Proficient in Python, Java, and JavaScript "
    "ecosystems with deep expertise in React, Node.js, Flask, and Django frameworks. "
    "Demonstrated ability to architect microservices on AWS and Azure cloud platforms, "
    "implement CI/CD pipelines using Docker and Kubernetes, and build end-to-end ML "
    "pipelines leveraging TensorFlow, PyTorch, Scikit-learn, Pandas, and NumPy. "
    "Passionate about NLP, deep learning, and using data science to solve complex "
    "business problems. Strong communicator and team leader with experience managing "
    "cross-functional Agile teams of 6-10 engineers.", sBody))

# ── Technical Skills ──────────────────────────────────────────────
story.extend(section_heading("Technical Skills"))

skills_data = [
    ("Languages",        "Python, Java, JavaScript, TypeScript, SQL, C++, Go, Rust"),
    ("Frontend",         "React, HTML, CSS, Redux, Next.js, Webpack, Responsive Design"),
    ("Backend",          "Node.js, Express.js, Flask, Django, REST API, GraphQL, Microservices"),
    ("Databases",        "MySQL, PostgreSQL, MongoDB, Oracle, Redis, Elasticsearch"),
    ("AI / ML / DS",     "TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, NLP, "
                         "Machine Learning, Deep Learning, Hugging Face Transformers"),
    ("Cloud & DevOps",   "AWS (EC2, S3, Lambda, SageMaker), Azure, Docker, Kubernetes, "
                         "Git, GitHub, GitLab CI/CD, Jenkins, Terraform"),
    ("Data & BI",        "Apache Kafka, Apache Spark, Power BI, Tableau, Airflow"),
    ("Other",            "Linux, Networking, Cisco, Agile/Scrum, JIRA, Excel"),
]

for label, value in skills_data:
    t = Table(
        [[Paragraph(f"<b>{label}:</b>", sSkillLabel),
          Paragraph(value, sSkillValue)]],
        colWidths=[85, None],
        hAlign="LEFT",
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
    ]))
    story.append(t)

# ── Work Experience ──────────────────────────────────────────────
story.extend(section_heading("Professional Experience"))

# -- Role 1 --
story.append(Paragraph("Senior Full-Stack Engineer", sSubHead))
story.append(Paragraph("TechNova Solutions Pvt. Ltd., Pune  |  Jan 2023 – Present", sMeta))
story.append(bullet(
    "Lead architect and developer of a microservices-based e-commerce platform serving "
    "2 million+ monthly active users, built with React, Node.js, Express.js, and PostgreSQL, "
    "deployed on AWS using Docker containers orchestrated by Kubernetes."))
story.append(bullet(
    "Designed and implemented a real-time product recommendation engine using Python, "
    "Scikit-learn, and TF-IDF cosine similarity, increasing average order value by 18%."))
story.append(bullet(
    "Built an NLP-powered customer support chatbot using Flask, Hugging Face Transformers, "
    "and PyTorch, reducing support ticket volume by 35% within the first quarter."))
story.append(bullet(
    "Established CI/CD pipelines using GitHub Actions, Docker, and Kubernetes across "
    "12 microservices, reducing deployment time from 45 minutes to under 8 minutes."))
story.append(bullet(
    "Mentored a team of 4 junior developers through pair-programming sessions and code "
    "reviews, improving sprint velocity by 22%."))
story.append(bullet(
    "Implemented Apache Kafka-based event streaming for order processing, handling "
    "50,000+ events per minute with sub-second latency."))

story.append(Spacer(1, 3*mm))

# -- Role 2 --
story.append(Paragraph("Full-Stack Developer", sSubHead))
story.append(Paragraph("Infosync Technologies, Bangalore  |  Jul 2021 – Dec 2022", sMeta))
story.append(bullet(
    "Developed and maintained a SaaS HR management dashboard using React, TypeScript, "
    "Redux, and Node.js with a MySQL backend, serving 150+ enterprise clients."))
story.append(bullet(
    "Integrated RESTful APIs and GraphQL endpoints with Oracle and MongoDB databases, "
    "optimizing query performance by 40% through indexing and caching with Redis."))
story.append(bullet(
    "Engineered a sentiment analysis module using Python, TextBlob, and Pandas to "
    "analyze employee feedback data, surfacing actionable insights for HR teams."))
story.append(bullet(
    "Deployed applications on Azure App Service with automated CI/CD through GitLab, "
    "achieving 99.95% uptime over 18 months."))
story.append(bullet(
    "Created interactive data visualization dashboards using Power BI and Tableau, "
    "enabling executives to monitor KPIs including employee retention and satisfaction."))

story.append(Spacer(1, 3*mm))

# -- Role 3 --
story.append(Paragraph("Software Engineer Intern → Junior Developer", sSubHead))
story.append(Paragraph("DataCraft Analytics, Hyderabad  |  Jun 2019 – Jun 2021", sMeta))
story.append(bullet(
    "Built data ingestion pipelines using Python, Pandas, NumPy, and Apache Spark, "
    "processing 10 GB+ of daily transactional data from multiple sources."))
story.append(bullet(
    "Developed machine learning models for customer churn prediction using "
    "Scikit-learn (Random Forest, XGBoost) achieving 91% accuracy on the test set."))
story.append(bullet(
    "Designed a responsive internal admin panel using HTML, CSS, JavaScript, and Flask, "
    "integrating REST API calls to a PostgreSQL backend."))
story.append(bullet(
    "Automated infrastructure provisioning on AWS (EC2, S3, Lambda) using Terraform "
    "and managed Linux-based server environments."))
story.append(bullet(
    "Collaborated with the networking team to configure Cisco switches and firewalls "
    "for secure data center connectivity."))

# ── Projects ─────────────────────────────────────────────────────
story.extend(section_heading("Key Projects"))

# Project 1
story.append(Paragraph("AI-Powered Resume Screening System", sSubHead))
story.append(Paragraph(
    "Built an end-to-end resume screening application using Python, Flask, and React. "
    "Implemented PDF text extraction with pdfplumber, NLP preprocessing with NLTK, "
    "and skill extraction using regex and named-entity recognition. "
    "Developed a TF-IDF and cosine similarity engine with Scikit-learn to rank candidates "
    "against job descriptions. The system scored resumes on skills, experience, education, "
    "and project depth, reducing manual screening time by 60%. "
    "Deployed on AWS EC2 with Docker containers and PostgreSQL storage.", sBody))

# Project 2
story.append(Spacer(1, 2*mm))
story.append(Paragraph("Real-Time Fraud Detection Pipeline", sSubHead))
story.append(Paragraph(
    "Architected a streaming fraud detection system using Apache Kafka, Python, and "
    "TensorFlow. Trained a deep learning LSTM model on 5 million+ transactions, "
    "achieving 96.3% precision. Integrated the model into a Flask REST API microservice "
    "with Redis caching for sub-200ms inference. Built monitoring dashboards in Tableau "
    "and Power BI. The pipeline processed 100K+ transactions per hour on Kubernetes-managed "
    "AWS infrastructure.", sBody))

# Project 3
story.append(Spacer(1, 2*mm))
story.append(Paragraph("Multi-Language NLP Chatbot Platform", sSubHead))
story.append(Paragraph(
    "Developed a multilingual customer-facing chatbot using PyTorch, Hugging Face "
    "Transformers, and Node.js. Supported English, Hindi, and Marathi with intent "
    "classification accuracy of 94%. Backend built with Express.js and MongoDB. "
    "Frontend built with React and TypeScript. Integrated with Slack and Microsoft "
    "Teams via REST APIs. Handled 10,000+ queries daily in production.", sBody))

# Project 4
story.append(Spacer(1, 2*mm))
story.append(Paragraph("Predictive Maintenance IoT Dashboard", sSubHead))
story.append(Paragraph(
    "Designed a predictive maintenance system for manufacturing equipment using "
    "Machine Learning (Random Forest, Gradient Boosting) with Scikit-learn and Pandas. "
    "Sensor data streamed via Kafka and stored in PostgreSQL. Developed an interactive "
    "dashboard with React, Node.js, and Chart.js. Reduced unplanned downtime by 28%. "
    "Infrastructure managed with Docker, Kubernetes, and AWS.", sBody))

# Project 5
story.append(Spacer(1, 2*mm))
story.append(Paragraph("Enterprise Data Lake &amp; BI Platform", sSubHead))
story.append(Paragraph(
    "Led the design of a centralized data lake on AWS S3 with ETL pipelines built using "
    "Python, Pandas, NumPy, and Apache Spark. Connected Tableau and Power BI for "
    "executive reporting across sales, HR, and operations. Implemented SQL-based "
    "analytics on a PostgreSQL data warehouse. Managed Linux servers and configured "
    "networking infrastructure including Cisco routers. Reduced report generation "
    "time from 4 hours to 12 minutes.", sBody))

# ── Education ────────────────────────────────────────────────────
story.extend(section_heading("Education"))

story.append(Paragraph("Master of Technology (M.Tech) in Computer Science", sSubHead))
story.append(Paragraph(
    "Indian Institute of Technology (IIT) Pune  |  2017 – 2019  |  CGPA: 8.7/10", sMeta))
story.append(Paragraph(
    "Thesis: \"Deep Learning Approaches for Automated Resume Parsing and Job Matching\" "
    "— Developed a novel NLP pipeline using TensorFlow and BERT for semantic matching "
    "of candidate profiles to job descriptions.", sBody))

story.append(Spacer(1, 2*mm))
story.append(Paragraph("Bachelor of Engineering (B.E.) in Information Technology", sSubHead))
story.append(Paragraph(
    "Pune Institute of Computer Technology (PICT)  |  2013 – 2017  |  CGPA: 8.2/10", sMeta))
story.append(Paragraph(
    "Final year project: \"Machine Learning Based Student Performance Prediction System\" "
    "using Python, Scikit-learn, and Flask.", sBody))

# ── Certifications ───────────────────────────────────────────────
story.extend(section_heading("Certifications"))

certs = [
    "AWS Certified Solutions Architect – Associate (Amazon Web Services, 2023)",
    "TensorFlow Developer Certificate (Google, 2022)",
    "Microsoft Azure Fundamentals AZ-900 (Microsoft, 2022)",
    "Machine Learning Specialization (Stanford / Coursera, 2021)",
    "Docker Certified Associate (Mirantis, 2021)",
    "Cisco Certified Network Associate (CCNA) (Cisco, 2020)",
]
for cert in certs:
    story.append(bullet(cert))

# ── Achievements ─────────────────────────────────────────────────
story.extend(section_heading("Achievements & Publications"))

achievements = [
    "Received the \"Innovation Excellence Award\" at TechNova Solutions (2024) for the "
    "AI-powered recommendation engine that drove an 18% revenue increase.",
    "Published research paper: \"TF-IDF and Deep Learning Hybrid Models for Job-Resume "
    "Matching\" in the International Journal of NLP and Machine Learning (2020).",
    "Won 1st place at HackIndia 2022 — built a real-time ML-powered healthcare triage "
    "application using Python, Flask, React, and TensorFlow in 36 hours.",
    "Open-source contributor to Scikit-learn and Hugging Face Transformers libraries "
    "with 15+ merged pull requests.",
    "Speaker at PyCon India 2023 — \"Scaling NLP Microservices with Flask, Docker, and Kubernetes.\"",
]
for ach in achievements:
    story.append(bullet(ach))

# ── Build PDF ────────────────────────────────────────────────────
doc.build(story)
print(f"Resume generated: {OUTPUT_PATH}")
print(f"File size: {os.path.getsize(OUTPUT_PATH)} bytes")
