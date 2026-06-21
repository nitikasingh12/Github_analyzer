from datetime import datetime

class CareerSuggestions:
    """Generate improvement suggestions for developers"""
    
    def __init__(self, analysis, repos, github_data):
        self.analysis = analysis
        self.repos = repos
        self.github_data = github_data
    
    def get_all_suggestions(self):
        """Get complete improvement suggestions"""
        
        suggestions = {
            'strengths': self.get_strengths(),
            'weaknesses': self.get_weaknesses(),
            'skill_gaps': self.get_skill_gaps(),
            'improvement_plan': self.get_improvement_plan(),
            'next_milestone': self.get_next_milestone(),
            'estimated_timeline': self.get_timeline()
        }
        
        return suggestions
    
    # ============ STRENGTHS ============
    
    def get_strengths(self):
        """What they're doing WELL"""
        
        strengths = []
        score = self.analysis['overall_score']
        repos_count = self.analysis['public_repos']
        followers = self.analysis['followers']
        skills = [s['name'] for s in self.analysis['detected_skills']]
        
        # Strength 1: Good score
        if score >= 60:
            strengths.append({
                'title': '⭐ Strong Developer Profile',
                'description': f'Your score of {score}/100 shows solid experience',
                'emoji': '⭐'
            })
        
        # Strength 2: Many repos
        if repos_count >= 20:
            strengths.append({
                'title': '📦 Productive Developer',
                'description': f'You have {repos_count} public repositories - showing consistency',
                'emoji': '📦'
            })
        
        # Strength 3: Community engagement
        if followers >= 50:
            strengths.append({
                'title': '👥 Community Presence',
                'description': f'{followers} followers - your work is noticed',
                'emoji': '👥'
            })
        
        # Strength 4: Diverse skills
        if len(skills) >= 5:
            strengths.append({
                'title': '🛠️ Multi-skilled Developer',
                'description': f'Knowledge in {len(skills)} different technologies',
                'emoji': '🛠️'
            })
        
        # Strength 5: Account history
        account_age = self.get_account_age()
        if account_age >= 3:
            strengths.append({
                'title': '⏰ Experienced Developer',
                'description': f'{account_age} years of GitHub history',
                'emoji': '⏰'
            })
        
        return strengths
    
    # ============ WEAKNESSES ============
    
    def get_weaknesses(self):
        """What needs IMPROVEMENT"""
        
        weaknesses = []
        score = self.analysis['overall_score']
        repos_count = self.analysis['public_repos']
        followers = self.analysis['followers']
        skills = [s['name'] for s in self.analysis['detected_skills']]
        bio = self.analysis['bio']
        
        # Weakness 1: Low score
        if score < 40:
            weaknesses.append({
                'title': '📉 Low Developer Score',
                'description': f'Your score is {score}/100. Build more projects!',
                'severity': 'HIGH',
                'emoji': '📉'
            })
        
        # Weakness 2: Few repos
        if repos_count < 5:
            weaknesses.append({
                'title': '📦 Lack of Portfolio',
                'description': 'Only {repos_count} repos. Need more projects to showcase skills',
                'severity': 'HIGH',
                'emoji': '📦'
            })
        
        # Weakness 3: No followers
        if followers < 10:
            weaknesses.append({
                'title': '👥 Low Community Engagement',
                'description': 'Few followers. Contribute to open source projects!',
                'severity': 'MEDIUM',
                'emoji': '👥'
            })
        
        # Weakness 4: Limited skills
        if len(skills) < 3:
            weaknesses.append({
                'title': '🛠️ Limited Tech Stack',
                'description': f'Only {len(skills)} skills detected. Learn more technologies!',
                'severity': 'MEDIUM',
                'emoji': '🛠️'
            })
        
        # Weakness 5: No bio
        if not bio or bio == '':
            weaknesses.append({
                'title': '✍️ Missing Bio/Description',
                'description': 'Add a professional bio to your GitHub profile',
                'severity': 'LOW',
                'emoji': '✍️'
            })
        
        # Weakness 6: Missing skills
        missing = self.get_missing_skills()
        if missing:
            weaknesses.append({
                'title': '❌ Missing In-Demand Skills',
                'description': f'You don\'t have: {", ".join(missing[:3])}',
                'severity': 'MEDIUM',
                'emoji': '❌'
            })
        
        # Weakness 7: No documentation
        poorly_documented = sum(
            1 for r in self.repos 
            if not r.get('description') or len(r.get('description', '')) < 10
        )
        if poorly_documented > len(self.repos) * 0.5:
            weaknesses.append({
                'title': '📝 Poor Documentation',
                'description': f'{poorly_documented} repos lack proper descriptions',
                'severity': 'LOW',
                'emoji': '📝'
            })
        
        return weaknesses
    
    # ============ SKILL GAPS ============
    
    def get_skill_gaps(self):
        """What skills are MISSING"""
        
        current_skills = [s['name'] for s in self.analysis['detected_skills']]
        
        # In-demand skills that they DON'T have
        in_demand = [
            'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
            'React', 'Vue', 'Angular', 'Node.js',
            'PostgreSQL', 'MongoDB', 'Redis',
            'Machine Learning', 'TensorFlow', 'PyTorch',
            'DevOps', 'CI/CD', 'GitHub Actions'
        ]
        
        missing = [skill for skill in in_demand if skill not in current_skills]
        
        # Categorize by importance
        skill_gaps = {
            'critical': missing[:3],  # Top 3 missing
            'important': missing[3:6],  # Next 3
            'nice_to_have': missing[6:]  # Rest
        }
        
        return {
            'missing_skills': missing,
            'by_priority': skill_gaps,
            'total_missing': len(missing)
        }
    
    # ============ IMPROVEMENT PLAN ============
    
    def get_improvement_plan(self):
        """Step-by-step improvement guide"""
        
        level = self.analysis['seniority_level']
        score = self.analysis['overall_score']
        
        plan = []
        
        # JUNIOR PATH
        if level == 'Junior' or score < 40:
            plan = [
                {
                    'step': 1,
                    'title': '🎯 Build More Projects',
                    'description': 'Create 5-10 small projects',
                    'examples': [
                        '- Todo List App',
                        '- Weather App',
                        '- Chat Application',
                        '- E-commerce Site'
                    ],
                    'estimated_time': '2-3 months',
                    'impact': '+15 score points'
                },
                {
                    'step': 2,
                    'title': '📚 Learn New Technologies',
                    'description': 'Pick 3 new skills and master them',
                    'examples': [
                        '- Learn Docker (containers)',
                        '- Learn React or Vue (frontend)',
                        '- Learn PostgreSQL (database)'
                    ],
                    'estimated_time': '1-2 months per skill',
                    'impact': '+10 score points'
                },
                {
                    'step': 3,
                    'title': '🔗 Contribute to Open Source',
                    'description': 'Make 5-10 PRs to real open source projects',
                    'examples': [
                        '- Find project on GitHub',
                        '- Find "good first issue" label',
                        '- Submit pull request',
                        '- Get feedback and merge'
                    ],
                    'estimated_time': '1-2 months',
                    'impact': '+20 score points, +followers'
                },
                {
                    'step': 4,
                    'title': '⭐ Get Projects Noticed',
                    'description': 'Share your best projects',
                    'examples': [
                        '- Write good README',
                        '- Add documentation',
                        '- Share on social media',
                        '- Help others use your code'
                    ],
                    'estimated_time': '2-3 weeks',
                    'impact': '+stars, +followers'
                }
            ]
        
        # MID-LEVEL PATH
        elif level == 'Mid-Level' or (40 <= score < 60):
            plan = [
                {
                    'step': 1,
                    'title': '🏗️ Build Complex Projects',
                    'description': 'Create 2-3 production-grade applications',
                    'examples': [
                        '- Full-stack web application',
                        '- Mobile app with backend',
                        '- System design project'
                    ],
                    'estimated_time': '2-3 months',
                    'impact': '+20 score points'
                },
                {
                    'step': 2,
                    'title': '☁️ Learn Cloud & DevOps',
                    'description': 'Master deployment and infrastructure',
                    'examples': [
                        '- AWS (EC2, S3, Lambda)',
                        '- Docker & Kubernetes',
                        '- GitHub Actions CI/CD'
                    ],
                    'estimated_time': '6-8 weeks',
                    'impact': '+15 score points, +salary'
                },
                {
                    'step': 3,
                    'title': '👨‍🏫 Help Others & Code Review',
                    'description': 'Review pull requests, answer questions',
                    'examples': [
                        '- Review 10+ PRs',
                        '- Answer Stack Overflow questions',
                        '- Mentor junior developers',
                        '- Write blog posts'
                    ],
                    'estimated_time': 'Ongoing',
                    'impact': '+reputation, +followers'
                },
                {
                    'step': 4,
                    'title': '📊 Build Something Unique',
                    'description': 'Create a tool/library others will use',
                    'examples': [
                        '- Create npm package',
                        '- Create Python library',
                        '- Build useful tool'
                    ],
                    'estimated_time': '2-3 months',
                    'impact': '+50 score points, +visibility'
                }
            ]
        
        # SENIOR PATH
        else:
            plan = [
                {
                    'step': 1,
                    'title': '🚀 Lead Major Projects',
                    'description': 'Own projects from concept to production',
                    'examples': [
                        '- Architecture design',
                        '- Tech decisions',
                        '- Team coordination'
                    ],
                    'estimated_time': 'Ongoing',
                    'impact': '+recognition'
                },
                {
                    'step': 2,
                    'title': '🎓 Share Knowledge',
                    'description': 'Create content and mentor others',
                    'examples': [
                        '- Write technical blog',
                        '- Create YouTube tutorials',
                        '- Give talks at conferences',
                        '- Mentor 3-5 juniors'
                    ],
                    'estimated_time': '5-10 hours/week',
                    'impact': '+personal brand'
                },
                {
                    'step': 3,
                    'title': '🌟 Contribute to Major Projects',
                    'description': 'Contribute to famous open source',
                    'examples': [
                        '- Linux kernel',
                        '- Django, Flask',
                        '- React, Vue',
                        '- Kubernetes'
                    ],
                    'estimated_time': '10+ hours/week',
                    'impact': '+prestige, +job offers'
                }
            ]
        
        return plan
    
    # ============ NEXT MILESTONE ============
    
    def get_next_milestone(self):
        """What's the next goal?"""
        
        level = self.analysis['seniority_level']
        score = self.analysis['overall_score']
        
        if level == 'Junior':
            return {
                'current_level': 'Junior',
                'next_level': 'Mid-Level',
                'target_score': 50,
                'current_score': score,
                'points_needed': 50 - score,
                'estimated_time': '3-6 months',
                'key_actions': [
                    'Build 5 more projects',
                    'Learn Docker & AWS',
                    'Contribute to 5 open source projects',
                    'Get 100 followers'
                ],
                'salary_impact': 'From $40k to $80k'
            }
        
        elif level == 'Mid-Level':
            return {
                'current_level': 'Mid-Level',
                'next_level': 'Senior',
                'target_score': 75,
                'current_score': score,
                'points_needed': 75 - score,
                'estimated_time': '6-12 months',
                'key_actions': [
                    'Build 2-3 complex projects',
                    'Lead open source project',
                    'Mentor 2-3 junior developers',
                    'Master cloud platform (AWS/GCP)',
                    'Get 500+ followers'
                ],
                'salary_impact': 'From $80k to $120k+'
            }
        
        else:  # Senior
            return {
                'current_level': 'Senior',
                'next_level': 'Tech Lead / Architect',
                'target_score': 90,
                'current_score': score,
                'points_needed': 90 - score,
                'estimated_time': '12+ months',
                'key_actions': [
                    'Lead major technical initiatives',
                    'Publish research/papers',
                    'Speak at major conferences',
                    'Build influential open source project',
                    'Get 2000+ followers'
                ],
                'salary_impact': 'From $120k to $180k+'
            }
    
    # ============ TIMELINE ============
    
    def get_timeline(self):
        """When can they reach next level?"""
        
        return {
            '3_months': {
                'title': 'Quick Wins (3 months)',
                'actions': [
                    '✅ Improve README on all repos',
                    '✅ Create 2 new projects',
                    '✅ Submit 3 open source PRs',
                    '✅ Write 2 blog posts'
                ],
                'expected_score_gain': '+10-15 points'
            },
            '6_months': {
                'title': 'Significant Growth (6 months)',
                'actions': [
                    '✅ Build 1 major project',
                    '✅ Master 1 new technology',
                    '✅ 20+ GitHub contributions',
                    '✅ 1000 GitHub activity'
                ],
                'expected_score_gain': '+20-30 points'
            },
            '12_months': {
                'title': 'Major Milestone (12 months)',
                'actions': [
                    '✅ Reach target score',
                    '✅ Advance to next level',
                    '✅ Potential 50% salary increase',
                    '✅ Better job opportunities'
                ],
                'expected_score_gain': '+40-50 points total'
            }
        }
    
    # ============ HELPER METHODS ============
    
    def get_missing_skills(self):
        """Get list of missing important skills"""
        current = [s['name'] for s in self.analysis['detected_skills']]
        important = ['Docker', 'AWS', 'Kubernetes', 'React', 'PostgreSQL']
        return [s for s in important if s not in current]
    
    def get_account_age(self):
        """Get GitHub account age in years"""
        # This would need created_at from GitHub API
        return 2  # Default