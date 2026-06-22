
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from database import db, DeveloperProfile, Job, Application
from config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database initialized!")

# ============ PAGES ============

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/developer')
def developer_dashboard():
    return render_template('developer.html')

@app.route('/hr')
def hr_dashboard():
    return render_template('hr_dashboard.html')

# ============ API - ANALYZE ============

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze GitHub profile and save to database"""
    try:
        print("✅ Analyze request received!")
        
        data = request.json
        username = data.get('username', '').strip()
        
        print(f"📝 Username: {username}")
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Check if already analyzed
        existing = DeveloperProfile.query.filter_by(username=username).first()
        if existing:
            print(f"✅ Using cached profile for {username}")
            skills = json.loads(existing.detected_skills) if existing.detected_skills else []
            return jsonify({
                'username': existing.username,
                'overall_score': existing.overall_score,
                'seniority_level': existing.seniority_level,
                'public_repos': existing.public_repos,
                'followers': existing.followers,
                'detected_skills': skills,
                'github_url': existing.github_url,
                'avatar_url': existing.avatar_url,
                'bio': existing.bio,
                'company': existing.company,
                'location': existing.location,
                'total_stars': existing.total_stars
            })
        
        # Fetch from GitHub
        print(f"🔄 Fetching GitHub data for {username}...")
        
        try:
            profile_resp = requests.get(
                f'https://api.github.com/users/{username}',
                timeout=5
            )
        except requests.exceptions.Timeout:
            return jsonify({'error': 'GitHub request timeout. Try again!'}), 500
        except Exception as e:
            print(f"❌ GitHub request error: {e}")
            return jsonify({'error': 'Network error. Check internet connection'}), 500
        
        print(f"📊 GitHub response status: {profile_resp.status_code}")
        
        if profile_resp.status_code != 200:
            return jsonify({'error': f'User "{username}" not found on GitHub'}), 404
        
        github_data = profile_resp.json()
        print(f"✅ GitHub data received!")
        
        # Get repos
        try:
            repos_resp = requests.get(
                f'https://api.github.com/users/{username}/repos?per_page=100',
                timeout=5
            )
            repos = repos_resp.json() if repos_resp.status_code == 200 else []
        except:
            repos = []
        
        # ANALYZE PROFILE
        print("🤖 Analyzing profile...")
        
        public_repos = github_data.get('public_repos', 0)
        followers = github_data.get('followers', 0)
        bio = github_data.get('bio', '') or 'No bio'
        
        # Calculate score
        repo_score = min(public_repos / 5, 20)
        followers_score = min(followers / 2, 20)
        total_stars = sum(r.get('stargazers_count', 0) for r in repos) if repos else 0
        stars_score = min(total_stars / 10, 20)
        
        total_score = repo_score + followers_score + stars_score + 10
        total_score = min(total_score, 100)
        
        # Seniority
        if total_score >= 60:
            seniority = 'Senior'
        elif total_score >= 40:
            seniority = 'Mid-Level'
        else:
            seniority = 'Junior'
        
        # Skill detection
        bio_text = (bio + ' ' + ' '.join([r.get('name', '') for r in repos[:5]])).lower()
        
        skills = []
        skill_keywords = {
            'Python': ['python', 'django', 'flask'],
            'JavaScript': ['javascript', 'js', 'react', 'node'],
            'Java': ['java', 'spring'],
            'Docker': ['docker', 'container'],
            'AWS': ['aws', 'amazon', 's3'],
            'GCP': ['gcp', 'google cloud'],
            'Azure': ['azure', 'microsoft cloud'],
            'MongoDB': ['mongodb', 'mongo'],
            'PostgreSQL': ['postgresql', 'postgres', 'sql'],
            'Git': ['git', 'github', 'gitlab'],
            'Kubernetes': ['kubernetes', 'k8s'],
            'DevOps': ['devops', 'ci/cd', 'jenkins'],
            'Machine Learning': ['machine learning', 'ml', 'tensorflow', 'pytorch'],
            'React': ['react', 'reactjs'],
            'Vue': ['vue', 'vuejs']
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in bio_text for keyword in keywords):
                skills.append({'name': skill, 'confidence': 0.85})
        
        if not skills:
            skills = [{'name': 'GitHub User', 'confidence': 0.85}]
        
        # Save to database
        profile = DeveloperProfile(
            username=username,
            overall_score=round(total_score, 2),
            seniority_level=seniority,
            public_repos=public_repos,
            followers=followers,
            detected_skills=json.dumps(skills),
            avatar_url=github_data.get('avatar_url'),
            bio=bio,
            github_url=github_data.get('html_url'),
            company=github_data.get('company', 'N/A'),
            location=github_data.get('location', 'N/A'),
            total_stars=total_stars
        )
        
        db.session.add(profile)
        db.session.commit()
        
        print(f"✅ Analysis complete! Score: {total_score}")
        
        return jsonify({
            'username': username,
            'overall_score': round(total_score, 2),
            'seniority_level': seniority,
            'public_repos': public_repos,
            'followers': followers,
            'detected_skills': skills,
            'github_url': github_data.get('html_url'),
            'avatar_url': github_data.get('avatar_url'),
            'bio': bio,
            'company': github_data.get('company', 'N/A'),
            'location': github_data.get('location', 'N/A'),
            'total_stars': total_stars
        })
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error: {str(e)}'}), 500

# ============ API - POST JOB ============

@app.route('/api/post-job', methods=['POST'])
def post_job():
    """Post a new job"""
    try:
        data = request.json
        
        job = Job(
            title=data.get('title'),
            company=data.get('company'),
            description=data.get('description'),
            required_skills=','.join(data.get('skills', [])),
            salary_min=data.get('salary_min', 0),
            salary_max=data.get('salary_max', 0),
            experience_level=data.get('experience_level'),
            location=data.get('location', ''),
            posted_by=data.get('posted_by', 'HR'),
            status='active'
        )
        
        db.session.add(job)
        db.session.commit()
        
        print(f"✅ Job posted: {job.title} (ID: {job.id})")
        
        return jsonify({
            'message': 'Job posted successfully',
            'job_id': job.id
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============ API - REAL JOB MATCHING ============

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    """Get REAL job recommendations based on skills and experience"""
    try:
        data = request.json
        username = data.get('username')
        
        print(f"🔍 Finding jobs for: {username}")
        
        # Get developer profile
        dev = DeveloperProfile.query.filter_by(username=username).first()
        if not dev:
            return jsonify({'error': 'Profile not found. Analyze first!'}), 404
        
        # Get all active jobs
        jobs = Job.query.filter_by(status='active').all()
        
        if not jobs:
            print("⚠️ No jobs in database")
            return jsonify({'recommendations': []})
        
        # Parse developer skills
        dev_skills = json.loads(dev.detected_skills) if dev.detected_skills else []
        dev_skill_names = [s['name'] for s in dev_skills]
        
        print(f"👤 Developer: {dev.username}, Skills: {dev_skill_names}, Level: {dev.seniority_level}")
        
        recommendations = []
        
        for job in jobs:
            job_skills = [s.strip() for s in job.required_skills.split(',') if s.strip()]
            
            # ============ SKILL MATCHING ============
            matching_skills = sum(1 for skill in job_skills if skill in dev_skill_names)
            skill_match = matching_skills / len(job_skills) if job_skills else 0
            
            # ============ SENIORITY MATCHING ============
            seniority_match = 0
            if dev.seniority_level == job.experience_level:
                seniority_match = 1.0
            elif dev.seniority_level == 'Senior' and job.experience_level in ['Mid-Level', 'Junior']:
                seniority_match = 0.9
            elif dev.seniority_level == 'Mid-Level' and job.experience_level == 'Junior':
                seniority_match = 0.9
            elif dev.seniority_level == 'Mid-Level' and job.experience_level == 'Senior':
                seniority_match = 0.7
            elif dev.seniority_level == 'Junior' and job.experience_level == 'Mid-Level':
                seniority_match = 0.6
            else:
                seniority_match = 0.5
            
            # ============ FINAL MATCH SCORE ============
            # 60% skills, 40% seniority
            final_score = (skill_match * 0.6) + (seniority_match * 0.4)
            
            # Only show jobs with >30% match
            if final_score > 0.3:
                recommendations.append({
                    'job_id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'description': job.description,
                    'required_skills': job_skills,
                    'match_score': round(final_score, 2),
                    'skill_match': round(skill_match, 2),
                    'seniority_match': round(seniority_match, 2),
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'experience_level': job.experience_level,
                    'location': job.location
                })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"✅ Found {len(recommendations)} matching jobs")
        
        return jsonify({'recommendations': recommendations[:10]})
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============ API - SALARY ============

@app.route('/api/salary-prediction', methods=['POST'])
def predict_salary():
    """Predict salary"""
    try:
        data = request.json
        skills = data.get('skills', [])
        seniority = data.get('seniority', 'mid').lower()
        
        base = {
            'junior': 40000, 
            'mid-level': 80000, 
            'mid': 80000, 
            'senior': 120000
        }.get(seniority, 80000)
        
        premium = ['Docker', 'AWS', 'Machine Learning', 'Kubernetes', 'GCP', 'Azure']
        bonus = sum(1 for s in skills if s in premium) * 0.1
        
        adjusted = base * (1 + bonus)
        
        return jsonify({
            'min': int(adjusted * 0.85),
            'avg': int(adjusted),
            'max': int(adjusted * 1.15)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API - HEALTH ============

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server running!'})

# ============ API - GET ALL JOBS ============

@app.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    """Get all active jobs"""
    try:
        jobs = Job.query.filter_by(status='active').all()
        return jsonify({'jobs': [j.to_dict() for j in jobs]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 GitHub Analyzer Starting...")
    print("=" * 60)
    print("📍 Open: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000, use_reloader=False)          
              


                
