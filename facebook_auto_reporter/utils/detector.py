import json
import logging
import openai

class ViolationDetector:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        self.ai_model = "gpt-4"
        self.logger = logging.getLogger(__name__)
        
    def analyze_content_for_violations(self, content_data):
        """Content analyze করে violations detect করুন"""
        violations_found = []
        
        try:
            # Analyze profile info
            if content_data.get('profile_info'):
                profile_violations = self.analyze_profile_info(content_data['profile_info'])
                violations_found.extend(profile_violations)
            
            # Analyze posts
            for post in content_data.get('posts', []):
                post_violations = self.analyze_post_content(post)
                violations_found.extend(post_violations)
                
            # Analyze images
            for image_url in content_data.get('images', []):
                image_violations = self.analyze_image_content(image_url)
                violations_found.extend(image_violations)
                
        except Exception as e:
            self.logger.error(f"Violation analysis failed: {e}")
            
        return violations_found
    
    def analyze_profile_info(self, profile_info):
        """Profile information analyze করুন"""
        prompt = f"""
        Analyze this Facebook profile for policy violations:
        
        Profile Name: {profile_info.get('name', '')}
        Bio: {profile_info.get('bio', '')}
        Profile URL: {profile_info.get('profile_url', '')}
        
        Check for these violation types:
        - Impersonation (using someone else's identity)
        - Fake account (bot or completely fake profile)
        - Hate speech in bio
        - Underage user (based on profile content)
        - Illegal activity promotion
        
        Return analysis in this exact JSON format:
        {{
            "violations": [
                {{
                    "violation_type": "violation_name",
                    "confidence_score": 85,
                    "evidence": "specific evidence from profile",
                    "report_category": "Facebook report category name"
                }}
            ]
        }}
        
        If no violations found, return empty violations array.
        """
        
        return self.call_ai_api(prompt)
    
    def analyze_post_content(self, post):
        """Post content analyze করুন"""
        prompt = f"""
        Analyze this Facebook post for policy violations:
        
        Post Text: {post.get('text', '')}
        Timestamp: {post.get('timestamp', '')}
        Reactions: {post.get('reactions', 0)}
        
        Check for:
        - Harassment or bullying
        - Hate speech
        - Sexual content
        - Violence or graphic content
        - Self-harm promotion
        - Spam or scams
        - Illegal activity
        - Copyright violation
        
        Return analysis in JSON format as specified before.
        """
        
        return self.call_ai_api(prompt)
    
    def analyze_image_content(self, image_url):
        """Image content analyze করুন (based on URL analysis)"""
        prompt = f"""
        Analyze this Facebook image URL for potential policy violations:
        
        Image URL: {image_url}
        
        Based on the URL pattern and context, check for:
        - Profile picture violations
        - Cover photo violations  
        - Nudity or sexual content
        - Violent or graphic content
        - Hate symbols
        - Copyright infringement
        
        Note: This is URL-based analysis only.
        
        Return analysis in JSON format.
        """
        
        return self.call_ai_api(prompt)
    
    def call_ai_api(self, prompt):
        """AI API call করুন"""
        try:
            response = openai.ChatCompletion.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": "You are a Facebook policy violation expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('violations', [])
            
        except Exception as e:
            self.logger.error(f"AI API call failed: {e}")
            return []