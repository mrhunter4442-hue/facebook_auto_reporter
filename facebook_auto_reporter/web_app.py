from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import json
import threading
import uuid
from main import FacebookAutoReporter
from config import Config

app = Flask(__name__)
app.secret_key = 'your_very_secure_secret_key_here_12345'

# Store jobs in memory (in production, use database)
jobs = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # In a real app, you'd verify credentials here
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Save settings
        settings_data = {
            'facebook_username': request.form['fb_username'],
            'facebook_password': request.form['fb_password'],
            'openai_api_key': request.form['openai_key'],
            'max_reports': int(request.form['max_reports']),
            'delay': int(request.form['delay'])
        }
        
        # Save to .env file
        with open('.env', 'w') as f:
            f.write(f"FACEBOOK_USERNAME={settings_data['facebook_username']}\n")
            f.write(f"FACEBOOK_PASSWORD={settings_data['facebook_password']}\n")
            f.write(f"OPENAI_API_KEY={settings_data['openai_api_key']}\n")
        
        return jsonify({'status': 'success', 'message': 'Settings saved successfully'})
    
    return render_template('settings.html')

@app.route('/targets', methods=['GET', 'POST'])
def targets():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        targets_list = request.form['targets'].split('\n')
        targets_list = [t.strip() for t in targets_list if t.strip()]
        
        with open('data/targets.json', 'w') as f:
            json.dump(targets_list, f, indent=2)
        
        return jsonify({'status': 'success', 'message': f'Saved {len(targets_list)} targets'})
    
    # Load existing targets
    try:
        with open('data/targets.json', 'r') as f:
            targets_list = json.load(f)
    except:
        targets_list = []
    
    return render_template('targets.html', targets=targets_list)

@app.route('/start_job', methods=['POST'])
def start_job():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'Not logged in'})
    
    job_id = str(uuid.uuid4())
    
    # Start reporting in background thread
    jobs[job_id] = {
        'status': 'running',
        'progress': 0,
        'results': []
    }
    
    thread = threading.Thread(target=run_reporting_job, args=(job_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'success', 'job_id': job_id, 'message': 'Job started'})

def run_reporting_job(job_id):
    try:
        # Initialize reporter
        reporter = FacebookAutoReporter(job_id, jobs)
        success = reporter.run_batch_reporting()
        
        if success:
            jobs[job_id]['status'] = 'completed'
        else:
            jobs[job_id]['status'] = 'failed'
            
    except Exception as e:
        print(f"Job error: {e}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

@app.route('/job_status/<job_id>')
def job_status(job_id):
    if job_id in jobs:
        return jsonify(jobs[job_id])
    return jsonify({'status': 'not_found'})

@app.route('/reports')
def reports():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # Load generated reports
    report_files = []
    reports_dir = 'data/reports/'
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith(('.json', '.csv', '.xlsx', '.pdf')):
                report_files.append({
                    'name': file,
                    'path': f"data/reports/{file}",
                    'size': os.path.getsize(f"{reports_dir}/{file}")
                })
    
    return render_template('reports.html', reports=report_files)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)