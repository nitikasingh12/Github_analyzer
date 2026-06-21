from datetime import datetime

# Skill database
SKILL_KEYWORDS = {
    'Python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
    'JavaScript': ['javascript', 'js', 'react', 'node', 'express', 'vue', 'angular'],
    'Java': ['java', 'spring', 'maven', 'gradle'],
    'C++': ['c++', 'cpp', 'c#', 'csharp'],
    'Docker': ['docker', 'kubernetes', 'k8s', 'container'],
    'AWS': ['aws', 'amazon', 's3', 'ec2', 'lambda'],
    'GCP': ['gcp', 'google cloud', 'firebase'],
    'MongoDB': ['mongodb', 'mongo', 'nosql'],
    'PostgreSQL': ['postgresql', 'postgres', 'sql'],
    'Redis': ['redis', 'cache'],
    'Machine Learning': ['tensorflow', 'pytorch', 'scikit-learn', 'ml', 'ai'],
    'Git': ['git', 'github', 'gitlab', 'bitbucket'],
}

def detect_skills(text):
    """Detect skills from text"""
    if not text:
        return []
    
    text = text.lower()
    detected = []
    
    for skill, keywords in SKILL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                detected.append(skill)
                break
    
    return list(set(detected))

def analyze_github_profile(username, github_data, repos):
    """Comprehensive GitHub profile analysis"""
    
    try:
        # Basic stats
        public_repos = github_data.get('public_repos', 0)
        followers = github_data.get('followers', 0)
        following = github_data.get('following', 0)
        bio = github_data.get('bio', '') or ''
        
        # Detect skills from bio and repo names
        bio_text = bio + ' ' + ' '.join([r.get('name', '') for r in repos[:10]])
        detected_skills = detect_skills(bio_text)
        
        # Calculate score (0-100)
        repo_score = min(public_repos / 5, 20)  # Max 20 points
        followers_score = min(followers / 2, 20)  # Max 20 points
        skills_score = min(len(detected_skills) * 2, 20)  # Max 20 points
        
        # Repository quality
        total_stars = sum(r.get('stargazers_count', 0) for r in repos) if repos else 0
        stars_score = min(total_stars / 10, 20)  # Max 20 points
        
        total_score = repo_score + followers_score + skills_score + stars_score
        
        # Seniority prediction
        if total_score >= 60:
            seniority = 'Senior'
        elif total_score >= 40:
            seniority = 'Mid-Level'
        else:
            seniority = 'Junior'
        
        return {
            'username': username,
            'overall_score': round(total_score, 2),
            'seniority_level': seniority,
            'public_repos': public_repos,
            'followers': followers,
            'following': following,
            'detected_skills': [{'name': skill, 'confidence': 0.85} for skill in detected_skills],
            'github_url': github_data.get('html_url'),
            'avatar_url': github_data.get('avatar_url'),
            'bio': bio,
            'company': github_data.get('company'),
            'location': github_data.get('location'),
            'total_stars': total_stars
        }
    
    except Exception as e:
        print(f"Error analyzing profile: {e}")
        return {
            'username': username,
            'overall_score': 0,
            'seniority_level': 'Unknown',
            'public_repos': 0,
            'followers': 0,
            'detected_skills': [],
            'error': str(e)
        }

def match_job_developer(developer_profile, job):
    """Calculate match score between job and developer (0-1)"""
    
    try:
        job_skills = [s.lower() for s in job.get('required_skills', [])]
        dev_skills = [s['name'].lower() for s in developer_profile.get('detected_skills', [])]
        
        if not job_skills:
            return 0.5
        
        # Skill matching
        matching_skills = len(set(job_skills) & set(dev_skills))
        skill_match = matching_skills / len(job_skills)
        
        # Seniority matching
        job_level = job.get('experience_level', 'mid')
        dev_level = developer_profile.get('seniority_level', 'Mid-Level').lower()
        
        seniority_match = 1.0
        if job_level == 'senior' and 'senior' not in dev_level:
            seniority_match = 0.7
        elif job_level == 'junior' and 'senior' in dev_level:
            seniority_match = 0.9
        
        # Overall score
        score = (skill_match * 0.6 + seniority_match * 0.4)
        return round(score, 2)
    
    except Exception as e:
        print(f"Error matching: {e}")
        return 0.5

def calculate_salary(skills, seniority):
    """Predict salary based on skills and seniority"""
    
    try:
        base_salaries = {
            'junior': 40000,
            'mid-level': 80000,
            'mid': 80000,
            'senior': 120000,
            'lead': 150000
        }
        
        base = base_salaries.get(seniority.lower(), 80000)
        
        # Skill bonuses
        premium_skills = ['Machine Learning', 'Docker', 'AWS', 'GCP', 'Kubernetes']
        skill_bonus = sum(1 for s in skills if s in premium_skills) * 0.1
        
        adjusted_salary = base * (1 + skill_bonus)
        
        return {
            'min': int(adjusted_salary * 0.85),
            'avg': int(adjusted_salary),
            'max': int(adjusted_salary * 1.15)
        }
    
    except Exception as e:
        print(f"Error calculating salary: {e}")
        return {
            'min': 50000,
            'avg': 80000,
            'max': 120000
        }
def get_actionable_tips(analysis):
    """Get specific tips to improve"""
    
    tips = []
    score = analysis['overall_score']
    skills = [s['name'] for s in analysis['detected_skills']]
    
    # Tip 1
    if score < 50:
        tips.append({
            'priority': 'HIGH',
            'tip': '📦 Build More Projects',
            'action': 'Create 2-3 new projects to showcase your skills',
            'examples': ['Todo app', 'Chat application', 'E-commerce site']
        })
    
    # Tip 2
    if 'Docker' not in skills:
        tips.append({
            'priority': 'HIGH',
            'tip': '🐳 Learn Docker',
            'action': 'Container knowledge is in-demand',
            'resource': 'docker.com/get-started'
        })
    
    # Tip 3
    if 'AWS' not in skills and 'GCP' not in skills:
        tips.append({
            'priority': 'HIGH',
            'tip': '☁️ Learn Cloud (AWS/GCP)',
            'action': 'Master at least one cloud platform',
            'resource': 'aws.amazon.com/training'
        })
    
    # Tip 4
    if len(skills) < 5:
        tips.append({
            'priority': 'MEDIUM',
            'tip': '🛠️ Expand Your Tech Stack',
            'action': 'Learn 2-3 more technologies',
            'suggested': list(set(['React', 'PostgreSQL', 'Python']) - set(skills))[:3]
        })
    
    # Tip 5
    tips.append({
        'priority': 'MEDIUM',
        'tip': '🔗 Contribute to Open Source',
        'action': 'Help other projects, gain reputation',
        'platforms': ['GitHub.com', 'FirstTimersOnly.com', 'GoodFirstIssue.dev']
    })
    
    return tips        