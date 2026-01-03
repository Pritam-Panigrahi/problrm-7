from flask import Flask, render_template, request, session, jsonify, redirect, url_for, send_file
import os
import json
from datetime import datetime
from config import Config
from models.database import init_db, SessionLocal
from models.user import User
from models.organization import Organization
from models.job import Job
from models.application import Application
from utils.ai_assistant import ResumeAssistant
from utils.skill_extractor import extract_and_categorize_skills
from utils.job_matcher import match_jobs_for_user
from utils.resume_generator import generate_ats_resume_content
from utils.pdf_generator import generate_pdf_resume_from_html
from utils.validators import validate_indian_phone, sanitize_input, validate_required_fields
from utils.translator import translate_text


app = Flask(__name__)
app.config.from_object(Config)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/worker/start', methods=['POST'])
def worker_start():
    data = request.get_json()
    phone = sanitize_input(data.get('phone', ''))
    language = sanitize_input(data.get('language', 'en'))
    
    if not validate_indian_phone(phone):
        return jsonify({'error': 'Invalid phone number'}), 400
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(phone=phone).first()
        
        if not user:
            user = User(phone=phone, language=language)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.language = language
            db.commit()
        
        session['user_id'] = user.id
        session['user_type'] = 'worker'
        session['language'] = language
        
        return jsonify({'success': True, 'user_id': user.id})
    
    finally:
        db.close()

@app.route('/worker/dashboard')
def worker_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user:
            return redirect(url_for('index'))
        
        applications = db.query(Application).filter_by(user_id=user.id).all()
        
        applications_data = []
        for app in applications:
            job = db.query(Job).filter_by(id=app.job_id).first()
            org = db.query(Organization).filter_by(id=job.organization_id).first() if job else None
            
            applications_data.append({
                'application': app,
                'job': job,
                'organization': org
            })
        
        return render_template('worker/dashboard.html', user=user, applications=applications_data)
    finally:
        db.close()

@app.route('/worker/chat', methods=['GET'])
def worker_chat():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user:
            return redirect(url_for('index'))
        
        return render_template('worker/chat.html', user=user, language=user.language)
    finally:
        db.close()

@app.route('/worker/chat/message', methods=['POST'])
def worker_chat_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_message = sanitize_input(data.get('message', ''))
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        chat_history = user.chat_history or []
        
        assistant = ResumeAssistant(language=user.language)
        ai_response = assistant.chat(user_message, chat_history)
        
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": ai_response})
        
        user.chat_history = chat_history
        
        is_complete = "COMPLETE" in ai_response
        
        if is_complete:
            resume_data = assistant.extract_resume_data(chat_history)
            
            user.name = resume_data.get('name', user.name)
            user.trade = resume_data.get('trade', user.trade)
            user.experience_years = resume_data.get('experience_years', user.experience_years)
            user.location = resume_data.get('location', user.location)
            user.education = resume_data.get('education', user.education)
            user.certifications = resume_data.get('certifications', user.certifications)
            user.skills = resume_data.get('skills', [])
            user.work_history = resume_data.get('work_history', [])
            user.resume_complete = 1
        
        db.commit()
        
        return jsonify({
            'response': ai_response,
            'is_complete': is_complete
        })
    
    finally:
        db.close()

@app.route('/worker/resume/preview')
def worker_resume_preview():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user or not user.resume_complete:
            return redirect(url_for('worker_chat'))
        
        categorized_skills = extract_and_categorize_skills(user.skills, user.trade)
        
        user_data = {
            'name': user.name,
            'phone': user.phone,
            'trade': user.trade,
            'experience_years': user.experience_years,
            'location': user.location,
            'skills': user.skills,
            'categorized_skills': categorized_skills,
            'education': user.education,
            'certifications': user.certifications,
            'work_history': user.work_history
        }
        
        resume_content = generate_ats_resume_content(user_data)
        
        return render_template('worker/resume_preview.html', 
                               user=user, 
                               resume_content=resume_content,
                               categorized_skills=categorized_skills)
    finally:
        db.close()

@app.route('/worker/resume/download')
def worker_resume_download():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user or not user.resume_complete:
            return jsonify({'error': 'Resume not ready'}), 400
        
        categorized_skills = extract_and_categorize_skills(user.skills, user.trade)
        
        user_data = {
            'name': user.name,
            'phone': user.phone,
            'trade': user.trade,
            'experience_years': user.experience_years,
            'location': user.location,
            'skills': user.skills,
            'categorized_skills': categorized_skills,
            'education': user.education,
            'certifications': user.certifications,
            'work_history': user.work_history
        }
        
        os.makedirs('static/resumes', exist_ok=True)
        filename = f"resume_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('static/resumes', filename)
        
        # Generate PDF using WeasyPrint for pixel-perfect HTML-to-PDF conversion
        success = generate_pdf_resume_from_html(user_data, categorized_skills, filepath)
        
        if success:
            return send_file(filepath, as_attachment=True, download_name=f"{user.name}_Resume.pdf")
        else:
            return jsonify({'error': 'PDF generation failed'}), 500
    
    finally:
        db.close()

@app.route('/worker/jobs/recommended')
def worker_jobs_recommended():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user or not user.resume_complete:
            return redirect(url_for('worker_chat'))
        
        jobs = db.query(Job).filter_by(status='active').all()
        
        jobs_data = []
        for job in jobs:
            org = db.query(Organization).filter_by(id=job.organization_id).first()
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'trade': job.trade,
                'required_skills': job.required_skills,
                'experience_required': job.experience_required,
                'location': job.location,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'organization_name': org.name if org else 'Unknown'
            })
        
        user_data = {
            'trade': user.trade,
            'experience_years': user.experience_years,
            'skills': user.skills,
            'location': user.location
        }
        
        matched_jobs = match_jobs_for_user(user_data, jobs_data)
        
        job_matches = []
        for match in matched_jobs:
            job = next((j for j in jobs_data if j['id'] == match['job_id']), None)
            if job:
                job['match_score'] = match['score']
                job['match_reasoning'] = match['reasoning']
                job_matches.append(job)
        
        return render_template('worker/jobs.html', jobs=job_matches, user=user)
    
    finally:
        db.close()

@app.route('/worker/apply/<int:job_id>', methods=['POST'])
def worker_apply(job_id):
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = SessionLocal()
    try:
        existing = db.query(Application).filter_by(
            user_id=session['user_id'],
            job_id=job_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Already applied to this job'}), 400
        
        application = Application(
            user_id=session['user_id'],
            job_id=job_id,
            status='pending'
        )
        
        db.add(application)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Application submitted successfully'})
    
    finally:
        db.close()

@app.route('/worker/account')
def worker_account():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user:
            return redirect(url_for('index'))
        
        return render_template('worker/account.html', user=user)
    finally:
        db.close()

@app.route('/worker/account/update', methods=['POST'])
def worker_account_update():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'name' in data and data['name']:
            user.name = sanitize_input(data['name'])
        if 'location' in data and data['location']:
            user.location = sanitize_input(data['location'])
        if 'trade' in data and data['trade']:
            user.trade = sanitize_input(data['trade'])
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    finally:
        db.close()

@app.route('/employer/start', methods=['POST'])
def employer_start():
    data = request.get_json()
    phone = sanitize_input(data.get('phone', ''))
    name = sanitize_input(data.get('name', ''))
    
    if not validate_indian_phone(phone):
        return jsonify({'error': 'Invalid phone number'}), 400
    
    db = SessionLocal()
    try:
        org = db.query(Organization).filter_by(phone=phone).first()
        
        if not org:
            org = Organization(phone=phone, name=name)
            db.add(org)
            db.commit()
            db.refresh(org)
        
        session['org_id'] = org.id
        session['user_type'] = 'employer'
        
        return jsonify({'success': True, 'org_id': org.id})
    
    finally:
        db.close()

@app.route('/employer/dashboard')
def employer_dashboard():
    if 'org_id' not in session or session.get('user_type') != 'employer':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        org = db.query(Organization).filter_by(id=session['org_id']).first()
        if not org:
            return redirect(url_for('index'))
        
        jobs = db.query(Job).filter_by(organization_id=org.id).all()
        
        jobs_data = []
        for job in jobs:
            app_count = db.query(Application).filter_by(job_id=job.id).count()
            jobs_data.append({
                'job': job,
                'application_count': app_count
            })
        
        return render_template('employer/dashboard.html', org=org, jobs=jobs_data)
    
    finally:
        db.close()

@app.route('/employer/post_job', methods=['GET', 'POST'])
def employer_post_job():
    if 'org_id' not in session or session.get('user_type') != 'employer':
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        return render_template('employer/post_job.html')
    
    data = request.get_json()
    
    required = ['title', 'trade', 'description', 'location']
    missing = validate_required_fields(data, required)
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400
    
    db = SessionLocal()
    try:
        skills_list = data.get('required_skills', '').split(',')
        skills_list = [s.strip() for s in skills_list if s.strip()]
        
        job = Job(
            organization_id=session['org_id'],
            title=sanitize_input(data['title']),
            trade=sanitize_input(data['trade']),
            description=sanitize_input(data['description']),
            required_skills=skills_list,
            experience_required=int(data.get('experience_required', 0)),
            location=sanitize_input(data['location']),
            salary_min=float(data.get('salary_min', 0)),
            salary_max=float(data.get('salary_max', 0)),
            status='active'
        )
        
        db.add(job)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Job posted successfully'})
    
    finally:
        db.close()

@app.route('/employer/matches/<int:job_id>')
def employer_matches(job_id):
    if 'org_id' not in session or session.get('user_type') != 'employer':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        job = db.query(Job).filter_by(id=job_id, organization_id=session['org_id']).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        users = db.query(User).filter_by(resume_complete=1).all()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'name': user.name,
                'trade': user.trade,
                'experience_years': user.experience_years,
                'skills': user.skills,
                'location': user.location
            })
        
        job_data = [{
            'id': job.id,
            'title': job.title,
            'trade': job.trade,
            'required_skills': job.required_skills,
            'experience_required': job.experience_required,
            'location': job.location
        }]
        
        matches = []
        for user_data in users_data:
            match_result = match_jobs_for_user(user_data, job_data)
            if match_result:
                user_data['match_score'] = match_result[0]['score']
                user_data['match_reasoning'] = match_result[0]['reasoning']
                matches.append(user_data)
        
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return render_template('employer/matches.html', job=job, matches=matches)
    
    finally:
        db.close()

@app.route('/employer/applicants/<int:job_id>')
def employer_applicants(job_id):
    if 'org_id' not in session or session.get('user_type') != 'employer':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        job = db.query(Job).filter_by(id=job_id, organization_id=session['org_id']).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        applications = db.query(Application).filter_by(job_id=job_id).all()
        
        applicants_data = []
        for app in applications:
            user = db.query(User).filter_by(id=app.user_id).first()
            if user:
                applicants_data.append({
                    'application': app,
                    'user': user
                })
        
        return render_template('employer/applicants.html', job=job, applicants=applicants_data)
    
    finally:
        db.close()

@app.route('/employer/application/update/<int:application_id>', methods=['POST'])
def employer_update_application(application_id):
    if 'org_id' not in session or session.get('user_type') != 'employer':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    new_status = sanitize_input(data.get('status', ''))
    
    if new_status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    
    db = SessionLocal()
    try:
        application = db.query(Application).filter_by(id=application_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        job = db.query(Job).filter_by(id=application.job_id).first()
        if not job or job.organization_id != session['org_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        application.status = new_status
        db.commit()
        
        return jsonify({'success': True, 'message': 'Application status updated'})
    
    finally:
        db.close()

@app.route('/employer/account')
def employer_account():
    if 'org_id' not in session or session.get('user_type') != 'employer':
        return redirect(url_for('index'))
    
    db = SessionLocal()
    try:
        org = db.query(Organization).filter_by(id=session['org_id']).first()
        if not org:
            return redirect(url_for('index'))
        
        return render_template('employer/account.html', org=org)
    finally:
        db.close()

@app.route('/employer/account/update', methods=['POST'])
def employer_account_update():
    if 'org_id' not in session or session.get('user_type') != 'employer':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    db = SessionLocal()
    try:
        org = db.query(Organization).filter_by(id=session['org_id']).first()
        if not org:
            return jsonify({'error': 'Organization not found'}), 404
        
        if 'name' in data and data['name']:
            org.name = sanitize_input(data['name'])
        if 'email' in data and data['email']:
            org.email = sanitize_input(data['email'])
        if 'location' in data and data['location']:
            org.location = sanitize_input(data['location'])
        if 'industry' in data and data['industry']:
            org.industry = sanitize_input(data['industry'])
        if 'description' in data and data['description']:
            org.description = sanitize_input(data['description'])
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    finally:
        db.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
