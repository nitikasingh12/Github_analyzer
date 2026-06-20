from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
CORS(app)

# Mock database
profiles_db = {}
jobs_db = {}

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
    """Analyze GitHub profile"""
    try:
        print("✅ Analyze request received!")
        
        data = request.json
        username = data.get('username', '').strip()
        
        print(f"📝 Username: {username}")
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
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
        
        # Simple skill detection
        bio_text = (bio + ' ' + ' '.join([r.get('name', '') for r in repos[:5]])).lower()
        
        skills = []
        if 'python' in bio_text:
            skills.append({'name': 'Python', 'confidence': 0.85})
        if 'javascript' in bio_text or 'js' in bio_text:
            skills.append({'name': 'JavaScript', 'confidence': 0.85})
        if 'java' in bio_text:
            skills.append({'name': 'Java', 'confidence': 0.85})
        if 'docker' in bio_text:
            skills.append({'name': 'Docker', 'confidence': 0.85})
        if 'aws' in bio_text:
            skills.append({'name': 'AWS', 'confidence': 0.85})
        if 'react' in bio_text:
            skills.append({'name': 'React', 'confidence': 0.85})
        if 'node' in bio_text:
            skills.append({'name': 'Node.js', 'confidence': 0.85})
        if 'git' in bio_text:
            skills.append({'name': 'Git', 'confidence': 0.85})
        
        if not skills:
            skills = [{'name': 'GitHub User', 'confidence': 0.85}]
        
        analysis = {
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
        }
        
        # Save to database
        profiles_db[username] = {
            'username': username,
            'github_data': github_data,
            'analysis': analysis,
            'analyzed_at': datetime.now()
        }
        
        print(f"✅ Analysis complete! Score: {total_score}")
        
        return jsonify(analysis)
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error: {str(e)}'}), 500

# ============ API - RECOMMENDATIONS ============

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    """Get job recommendations"""
    try:
        data = request.json
        username = data.get('username')
        
        if username not in profiles_db:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Return mock recommendations
        recommendations = [
            {
                'job_id': '1',
                'title': 'Senior Python Developer',
                'company': 'Google',
                'match_score': 0.85,
                'salary_min': 100000,
                'salary_max': 150000
            },
            {
                'job_id': '2',
                'title': 'Full Stack Developer',
                'company': 'Microsoft',
                'match_score': 0.72,
                'salary_min': 90000,
                'salary_max': 130000
            },
            {
                'job_id': '3',
                'title': 'Backend Engineer',
                'company': 'Amazon',
                'match_score': 0.68,
                'salary_min': 95000,
                'salary_max': 135000
            }
        ]
        
        return jsonify({'recommendations': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API - SALARY ============

@app.route('/api/salary-prediction', methods=['POST'])
def predict_salary():
    """Predict salary"""
    try:
        data = request.json
        skills = data.get('skills', [])
        seniority = data.get('seniority', 'mid').lower()
        
        base = {'junior': 40000, 'mid-level': 80000, 'mid': 80000, 'senior': 120000}.get(seniority, 80000)
        
        premium = ['Docker', 'AWS', 'Machine Learning']
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
# ============ API - SUGGESTIONS ============

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    """Get improvement suggestions"""
    try:
        data = request.json
        username = data.get('username')
        
        if username not in profiles_db:
            return jsonify({'error': 'Profile not found. Analyze first!'}), 404
        
        profile = profiles_db[username]
        analysis = profile['analysis']
        
        score = analysis['overall_score']
        level = analysis['seniority_level']
        skills = [s['name'] for s in analysis['detected_skills']]
        repos = analysis['public_repos']
        followers = analysis['followers']
        
        # ============ STRENGTHS ============
        strengths = []
        
        if score >= 60:
            strengths.append({
                'title': '⭐ Strong Developer Profile',
                'description': f'Your score of {score}/100 shows solid experience'
            })
        
        if repos >= 20:
            strengths.append({
                'title': '📦 Productive Developer',
                'description': f'You have {repos} public repositories - showing consistency'
            })
        
        if followers >= 50:
            strengths.append({
                'title': '👥 Community Presence',
                'description': f'{followers} followers - your work is noticed'
            })
        
        if len(skills) >= 5:
            strengths.append({
                'title': '🛠️ Multi-skilled Developer',
                'description': f'Knowledge in {len(skills)} different technologies'
            })
        
        # ============ WEAKNESSES ============
        weaknesses = []
        
        if score < 40:
            weaknesses.append({
                'title': '📉 Low Developer Score',
                'description': f'Your score is {score}/100. Build more projects!',
                'severity': 'HIGH'
            })
        
        if repos < 5:
            weaknesses.append({
                'title': '📦 Lack of Portfolio',
                'description': f'Only {repos} repos. Need more projects to showcase skills',
                'severity': 'HIGH'
            })
        
        if followers < 10:
            weaknesses.append({
                'title': '👥 Low Community Engagement',
                'description': 'Few followers. Contribute to open source projects!',
                'severity': 'MEDIUM'
            })
        
        if len(skills) < 3:
            weaknesses.append({
                'title': '🛠️ Limited Tech Stack',
                'description': f'Only {len(skills)} skills detected. Learn more technologies!',
                'severity': 'MEDIUM'
            })
        
        # ============ IMPROVEMENT PLAN ============
        if level == 'Junior':
            plan = [
                {
                    'step': 1,
                    'title': '🎯 Build More Projects',
                    'description': 'Create 5-10 small projects',
                    'time': '2-3 months',
                    'impact': '+15 score points'
                },
                {
                    'step': 2,
                    'title': '📚 Learn New Technologies',
                    'description': 'Pick 3 new skills and master them',
                    'time': '1-2 months per skill',
                    'impact': '+10 score points'
                },
                {
                    'step': 3,
                    'title': '🔗 Contribute to Open Source',
                    'description': 'Make 5-10 PRs to real open source projects',
                    'time': '1-2 months',
                    'impact': '+20 score points'
                }
            ]
        elif level == 'Mid-Level':
            plan = [
                {
                    'step': 1,
                    'title': '🏗️ Build Complex Projects',
                    'description': 'Create 2-3 production-grade applications',
                    'time': '2-3 months',
                    'impact': '+20 score points'
                },
                {
                    'step': 2,
                    'title': '☁️ Learn Cloud & DevOps',
                    'description': 'Master deployment and infrastructure',
                    'time': '6-8 weeks',
                    'impact': '+15 score points'
                },
                {
                    'step': 3,
                    'title': '👨‍🏫 Help Others & Code Review',
                    'description': 'Review pull requests, answer questions',
                    'time': 'Ongoing',
                    'impact': '+reputation'
                }
            ]
        else:  # Senior
            plan = [
                {
                    'step': 1,
                    'title': '🚀 Lead Major Projects',
                    'description': 'Own projects from concept to production',
                    'time': 'Ongoing',
                    'impact': '+recognition'
                },
                {
                    'step': 2,
                    'title': '🎓 Share Knowledge',
                    'description': 'Create content and mentor others',
                    'time': '5-10 hours/week',
                    'impact': '+personal brand'
                }
            ]
        
        # ============ NEXT MILESTONE ============
        if level == 'Junior':
            milestone = {
                'current': 'Junior',
                'next': 'Mid-Level',
                'target_score': 50,
                'points_needed': max(0, 50 - score),
                'time': '3-6 months',
                'salary': 'From $40k to $80k'
            }
        elif level == 'Mid-Level':
            milestone = {
                'current': 'Mid-Level',
                'next': 'Senior',
                'target_score': 75,
                'points_needed': max(0, 75 - score),
                'time': '6-12 months',
                'salary': 'From $80k to $120k+'
            }
        else:
            milestone = {
                'current': 'Senior',
                'next': 'Tech Lead / Architect',
                'target_score': 90,
                'points_needed': max(0, 90 - score),
                'time': '12+ months',
                'salary': 'From $120k to $180k+'
            }
        
        return jsonify({
            'strengths': strengths,
            'weaknesses': weaknesses,
            'improvement_plan': plan,
            'next_milestone': milestone
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500
