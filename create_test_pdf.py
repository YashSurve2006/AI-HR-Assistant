from reportlab.pdfgen import canvas
import os

def create_resume_pdf(filename, text_lines):
    c = canvas.Canvas(filename)
    y = 800
    for line in text_lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    fs_resume = [
        "Jane Doe - Full Stack Developer",
        "Experience: 5 years of professional software development experience.",
        "Role: Full Stack Engineer at TechCorp.",
        "Education: Bachelor of Technology (BTech) in Computer Engineering.",
        "Skills: JavaScript, React, Node.js, Python, SQL, MongoDB, HTML, CSS, Git.",
        "Projects:",
        "- Developed a scalable web application using React and Node.js.",
        "- Designed and optimized SQL and MongoDB database schemas.",
        "- Created REST APIs with Express and Node.js.",
        "Certifications: Certified Web Developer."
    ]
    
    ds_resume = [
        "John Smith - Data Scientist",
        "Experience: 4 years of data science and machine learning experience.",
        "Role: Machine Learning Engineer at DataCo.",
        "Education: Master of Science in Data Science.",
        "Skills: Python, Machine Learning, Scikit-learn, Pandas, NumPy, SQL, TensorFlow, AWS.",
        "Projects:",
        "- Built predictive models using Machine Learning and Scikit-learn.",
        "- Analyzed large datasets with Pandas and SQL.",
        "- Deployed ML models to AWS.",
        "Certifications: AWS Certified Machine Learning Specialty."
    ]
    
    create_resume_pdf("test_resume_fs.pdf", fs_resume)
    create_resume_pdf("test_resume_ds.pdf", ds_resume)
