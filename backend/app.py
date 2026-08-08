"""Flask application entry point for AI HR Assistant."""

from flask import Flask, jsonify
from flask_cors import CORS

import os
from werkzeug.utils import secure_filename

import config
import chatbot
import resume_analyzer
import job_recommender
import sentiment
import data_processor as dp
import data_visualization as dv

FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path='')
# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# CORS: allow all origins in debug/dev mode so the frontend works when
# opened via file://, Live Server, or any localhost port.
# In production, restrict this to your actual domain.
CORS(app, origins="*", supports_credentials=False)


@app.route("/")
def index():
    """Serve the frontend single-page application."""
    return app.send_static_file("index.html")

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for frontend connectivity."""
    return jsonify({
        "status": "ok",
        "message": "AI HR Assistant backend is running",
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint for HR chatbot interactions."""
    from flask import request
    data = request.get_json() or {}
    message = data.get("message", "")
    session_id = data.get("session_id", "default")
    
    response_data = chatbot.get_chatbot_response(message, session_id=session_id)
    
    return jsonify({
        "success": response_data.get("success", True),
        "answer": response_data["answer"],
        "category": response_data["category"],
        "confidence": response_data["confidence"],
        "confidence_level": response_data.get("confidence_level", "low"),
        "matched_question": response_data.get("matched_question"),
        "source": response_data.get("source", "system"),
    })


@app.route("/api/resume/analyze", methods=["POST"])
def analyze_resume_endpoint():
    """Endpoint for resume analysis and skill extraction."""
    from flask import request
    
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "File must be a PDF"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            analysis_result = resume_analyzer.analyze_resume(file_path)
            if not analysis_result.get("success"):
                return jsonify(analysis_result), 400
            return jsonify(analysis_result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
            
    return jsonify({"success": False, "error": "Invalid request"}), 400


@app.route("/api/resume/recommend", methods=["POST"])
def recommend_resume_endpoint():
    """Endpoint for resume analysis and job recommendation."""
    from flask import request
    
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "File must be a PDF"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract text and skills from PDF
            text = resume_analyzer.extract_text_from_pdf(file_path)
            if not text.strip():
                return jsonify({"success": False, "error": "Could not extract text from the PDF."}), 400
                
            cleaned_text = resume_analyzer.preprocess_resume_text(text)
            skills = resume_analyzer.extract_skills(cleaned_text)
            
            # Recommend jobs
            recommendations = job_recommender.recommend_jobs(cleaned_text, skills)
            
            return jsonify({
                "success": True,
                "filename": filename,
                "recommendations": recommendations
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
            
    return jsonify({"success": False, "error": "Invalid request"}), 400


@app.route("/api/feedback/sentiment", methods=["GET"])
def feedback_sentiment():
    """Endpoint for feedback sentiment analysis."""
    try:
        # Load feedback data
        df = dp.load_feedback()
        
        # Analyze sentiment
        analyzed_df = sentiment.analyze_feedback_dataframe(df)
        
        # Get summaries
        summary = sentiment.get_sentiment_summary(analyzed_df)
        dept_summary = sentiment.get_department_summary(analyzed_df)
        
        # Ensure json serializable
        analyzed_df = analyzed_df.fillna("")
        feedback_list = analyzed_df.to_dict(orient='records')
        
        return jsonify({
            "success": True,
            "summary": summary,
            "department_summary": dept_summary,
            "feedback": feedback_list
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    """Endpoint that returns all jobs for the Job Directory."""
    try:
        df = dp.load_jobs()
        # ensure it's serializable, fill na with ""
        df = df.fillna("")
        jobs_list = df.to_dict(orient='records')
        
        return jsonify({
            "success": True,
            "jobs": jobs_list
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    """Endpoint that returns all data needed to render the analytics dashboard."""
    try:
        summary = dv.get_dashboard_summary()
        sentiment_chart = dv.get_feedback_chart_data()
        dept_sentiment = dv.get_department_sentiment_data()
        rating_dist = dv.get_rating_distribution()
        job_dist = dv.get_job_distribution()
        loc_dist = dv.get_job_location_distribution()

        return jsonify({
            "success": True,
            "summary": summary,
            "sentiment": sentiment_chart,
            "department_sentiment": dept_sentiment,
            "rating_distribution": rating_dist,
            "job_distribution": job_dist,
            "location_distribution": loc_dist,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
