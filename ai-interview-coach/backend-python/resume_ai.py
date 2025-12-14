import spacy
import pdfplumber
import docx
import re
import json
import requests
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import os

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')

class ResumeAnalyzer:
    def __init__(self):
        # Use small English model (faster, free)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If spaCy model not available, use simple tokenizer
            self.nlp = None
        
        # Comprehensive skills database
        self.skills_db = [
            # Programming Languages
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift', 
            'kotlin', 'go', 'rust', 'typescript', 'scala', 'perl', 'r',
            
            # Web Development
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'express', 'spring', 'laravel', 'bootstrap', 'jquery', 'sass', 'less',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'redis', 
            'elasticsearch', 'cassandra', 'dynamodb',
            
            # Cloud & DevOps
            'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins',
            'ansible', 'terraform', 'git', 'github', 'gitlab', 'ci/cd',
            
            # Data Science & AI
            'machine learning', 'deep learning', 'data science', 'artificial intelligence',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'matplotlib', 'seaborn', 'jupyter', 'tableau', 'power bi',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin',
            
            # Soft Skills
            'leadership', 'communication', 'teamwork', 'problem solving',
            'project management', 'agile', 'scrum', 'time management',
            'critical thinking', 'creativity', 'adaptability'
        ]
        
        # Job categories with associated skills
        self.job_categories = {
            'Software Developer': ['python', 'java', 'javascript', 'c++', 'git', 'agile'],
            'Web Developer': ['html', 'css', 'javascript', 'react', 'node.js', 'php'],
            'Data Scientist': ['python', 'machine learning', 'data analysis', 'statistics', 'sql'],
            'DevOps Engineer': ['aws', 'docker', 'kubernetes', 'jenkins', 'linux'],
            'Mobile Developer': ['android', 'ios', 'react native', 'swift', 'kotlin'],
            'UI/UX Designer': ['figma', 'adobe xd', 'sketch', 'photoshop', 'illustrator'],
            'Project Manager': ['project management', 'agile', 'scrum', 'leadership', 'communication'],
            'Business Analyst': ['data analysis', 'sql', 'excel', 'requirements gathering', 'documentation']
        }
        
        # Education keywords
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'graduate', 'undergraduate', 'diploma', 'certificate', 'course'
        ]
    
    def extract_text(self, file_path):
        """Extract text from PDF or DOCX files"""
        text = ""
        try:
            if file_path.endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            elif file_path.endswith('.docx'):
                doc = docx.Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            else:
                # Try to read as text file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
        except Exception as e:
            print(f"Error extracting text: {e}")
        
        return text
    
    def analyze_resume(self, file_path):
        """Main analysis function"""
        try:
            # Extract text from resume
            text = self.extract_text(file_path)
            
            if not text or len(text.strip()) < 50:
                return {
                    'success': False,
                    'error': 'Resume text too short or could not be extracted'
                }
            
            print(f"Extracted text length: {len(text)} characters")
            
            # Extract basic information
            name = self.extract_name(text)
            email = self.extract_email(text)
            phone = self.extract_phone(text)
            
            # Extract skills using multiple methods
            skills = self.extract_skills(text)
            
            # Extract programming languages
            programming_languages = self.extract_programming_languages(text)
            
            # Extract education
            education = self.extract_education(text)
            
            # Extract experience
            experience_years = self.extract_experience(text)
            
            # Extract certifications
            certifications = self.extract_certifications(text)
            
            # Determine job categories
            job_categories = self.classify_job_categories(skills + programming_languages)
            
            # Calculate score
            score = self.calculate_score(skills, programming_languages, education, experience_years)
            
            # Sentiment analysis (confidence level)
            confidence_score = self.analyze_confidence(text)
            
            # Generate detailed analysis
            analysis = self.generate_analysis(
                skills, programming_languages, education, 
                experience_years, job_categories, score, confidence_score
            )
            
            # Generate recommendations
            recommendations = self.generate_recommendations(skills, programming_languages, score)
            
            return {
                'success': True,
                'basic_info': {
                    'name': name,
                    'email': email,
                    'phone': phone
                },
                'skills': skills[:15],  # Limit to top 15 skills
                'programming_languages': programming_languages,
                'education': education,
                'experience_years': experience_years,
                'certifications': certifications,
                'job_categories': job_categories[:3],  # Top 3 categories
                'score': min(score, 100),  # Cap at 100
                'confidence_score': confidence_score,
                'analysis': analysis,
                'recommendations': recommendations,
                'word_count': len(text.split()),
                'text_preview': text[:500] + "..." if len(text) > 500 else text
            }
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_name(self, text):
        """Extract name from resume (simple approach)"""
        # Look for patterns like "Name:" or at the beginning of document
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line.split()) <= 4:
                # Check if line looks like a name (capitalized words)
                words = line.split()
                if all(word[0].isupper() for word in words if word):
                    return line
        return "Not Found"
    
    def extract_email(self, text):
        """Extract email from text"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "Not Found"
    
    def extract_phone(self, text):
        """Extract phone number from text"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return "Not Found"
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        # Method 1: Direct keyword matching
        for skill in self.skills_db:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        # Method 2: Look for skills section
        skills_section_pattern = r'(?:skills|technical skills|competencies)[:\s]*(.*?)(?:\n\n|\n[A-Z]|$)'
        skills_section_match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if skills_section_match:
            skills_section = skills_section_match.group(1)
            # Extract individual skills from section
            skill_items = re.split(r'[,\n•\-*]', skills_section)
            for item in skill_items:
                item_clean = item.strip()
                if item_clean and len(item_clean.split()) <= 3:
                    found_skills.append(item_clean.title())
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def extract_programming_languages(self, text):
        """Extract programming languages"""
        programming_keywords = [
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift',
            'kotlin', 'go', 'rust', 'typescript', 'scala', 'perl', 'r',
            'html', 'css', 'sql', 'nosql', 'bash', 'shell'
        ]
        
        text_lower = text.lower()
        languages = []
        
        for lang in programming_keywords:
            if lang in text_lower:
                languages.append(lang.title())
        
        return list(set(languages))
    
    def extract_education(self, text):
        """Extract education information"""
        education_info = {
            'degrees': [],
            'institutions': [],
            'gpa': None
        }
        
        # Degree patterns
        degree_patterns = [
            r'\b(bachelor|b\.?s\.?|b\.?a\.?|b\.?tech|b\.?e)\b',
            r'\b(master|m\.?s\.?|m\.?a\.?|m\.?tech|m\.?e)\b',
            r'\b(ph\.?d|doctorate|doctoral)\b',
            r'\b(diploma|certificate)\b'
        ]
        
        text_lower = text.lower()
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                education_info['degrees'].extend([m.title() for m in matches])
        
        # Institution patterns
        institution_keywords = ['university', 'college', 'institute', 'school']
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in institution_keywords):
                # Check if this line might be an institution name
                if len(line.strip()) > 5 and len(line.strip().split()) <= 5:
                    education_info['institutions'].append(line.strip())
        
        # GPA pattern
        gpa_pattern = r'\bgpa\s*[:]?\s*(\d+\.\d+)\b'
        gpa_match = re.search(gpa_pattern, text_lower)
        if gpa_match:
            education_info['gpa'] = float(gpa_match.group(1))
        
        return education_info
    
    def extract_experience(self, text):
        """Extract years of experience"""
        # Pattern for years of experience
        exp_patterns = [
            r'(\d+)\s*(?:year|yr)s?\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\s*(?:year|yr)s?',
            r'(\d+)\+?\s*(?:year|yr)s?'
        ]
        
        text_lower = text.lower()
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    return int(matches[0])
                except:
                    continue
        
        # Fallback: count years mentioned
        year_matches = re.findall(r'\b(19|20)\d{2}\b', text)
        if year_matches:
            return max(1, len(year_matches) // 2)
        
        return 0
    
    def extract_certifications(self, text):
        """Extract certifications"""
        cert_patterns = [
            r'\b(certified|certification|certificate)\b.*?[\n,]',
            r'\b[A-Z]{2,}[\s\-]?[A-Z0-9]{2,}\b'  # Look for acronyms like AWS-CSA, PMP, etc.
        ]
        
        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                certifications.extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        # Common certifications
        common_certs = ['AWS', 'Azure', 'Google Cloud', 'PMP', 'Scrum', 'CISSP', 'CEH', 
                       'CCNA', 'OCP', 'MCSE', 'CISM', 'ITIL']
        
        text_upper = text.upper()
        for cert in common_certs:
            if cert.upper() in text_upper:
                certifications.append(cert)
        
        return list(set(certifications))[:10]  # Limit to 10
    
    def classify_job_categories(self, skills):
        """Classify resume into job categories based on skills"""
        category_scores = {}
        
        for category, keywords in self.job_categories.items():
            score = sum(1 for skill in skills if any(keyword in skill.lower() for keyword in keywords))
            if score > 0:
                category_scores[category] = score
        
        # Sort categories by score
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top categories with match percentage
        result = []
        for category, score in sorted_categories[:5]:
            match_percentage = min(100, (score / len(self.job_categories[category])) * 100)
            result.append({
                'category': category,
                'match_score': round(match_percentage, 1),
                'matched_skills': [s for s in skills if any(k in s.lower() for k in self.job_categories[category])]
            })
        
        return result
    
    def calculate_score(self, skills, programming_langs, education, experience):
        """Calculate resume score (0-100)"""
        score = 0
        
        # Skills (40 points max)
        skills_score = min(len(skills) * 2, 40)
        score += skills_score
        
        # Programming languages (20 points max)
        prog_score = min(len(programming_langs) * 4, 20)
        score += prog_score
        
        # Education (20 points max)
        if education['degrees']:
            if any('ph.d' in deg.lower() or 'doctor' in deg.lower() for deg in education['degrees']):
                edu_score = 20
            elif any('master' in deg.lower() or 'm.' in deg.lower() for deg in education['degrees']):
                edu_score = 15
            elif any('bachelor' in deg.lower() or 'b.' in deg.lower() for deg in education['degrees']):
                edu_score = 10
            else:
                edu_score = 5
        else:
            edu_score = 0
        score += edu_score
        
        # Experience (20 points max)
        if experience >= 5:
            exp_score = 20
        elif experience >= 3:
            exp_score = 15
        elif experience >= 1:
            exp_score = 10
        else:
            exp_score = 5
        score += exp_score
        
        # Bonus for certifications (up to 10 points)
        cert_bonus = min(len(self.extract_certifications(" ".join(skills))) * 2, 10)
        score += cert_bonus
        
        return min(score, 100)
    
    def analyze_confidence(self, text):
        """Analyze confidence level from resume text"""
        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity  # -1 to 1
            
            # Convert to confidence score (0-100)
            confidence = 50 + (sentiment * 50)
            return max(0, min(100, confidence))
        except:
            return 70  # Default confidence
    
    def generate_analysis(self, skills, programming_langs, education, experience, job_categories, score, confidence):
        """Generate detailed analysis text"""
        analysis_parts = []
        
        # Overall assessment
        if score >= 85:
            analysis_parts.append("🌟 **Excellent Resume!** Your resume shows strong potential for job applications.")
        elif score >= 70:
            analysis_parts.append("✅ **Good Resume!** Your resume is well-structured with room for improvement.")
        elif score >= 50:
            analysis_parts.append("📋 **Average Resume.** Consider enhancing certain sections for better impact.")
        else:
            analysis_parts.append("🔄 **Needs Improvement.** Focus on adding more relevant content and skills.")
        
        # Skills analysis
        if skills:
            analysis_parts.append(f"**Skills Identified:** {len(skills)} relevant skills including {', '.join(skills[:5])}.")
        else:
            analysis_parts.append("**Skills:** Consider adding more technical and soft skills.")
        
        # Programming languages
        if programming_langs:
            analysis_parts.append(f"**Technical Skills:** Strong in {', '.join(programming_langs)}.")
        
        # Experience
        if experience >= 3:
            analysis_parts.append(f"**Experience:** Good professional experience ({experience} years).")
        elif experience > 0:
            analysis_parts.append(f"**Experience:** Some professional experience ({experience} years).")
        else:
            analysis_parts.append("**Experience:** Consider adding internships or project experience.")
        
        # Job categories
        if job_categories:
            top_category = job_categories[0]
            analysis_parts.append(f"**Best Fit:** {top_category['category']} ({top_category['match_score']}% match).")
        
        # Confidence
        if confidence >= 80:
            analysis_parts.append("**Confidence:** Resume shows high confidence and professionalism.")
        
        return " ".join(analysis_parts)
    
    def generate_recommendations(self, skills, programming_langs, score):
        """Generate improvement recommendations"""
        recommendations = []
        
        if score < 70:
            recommendations.append("🔹 **Add more skills** - Include both technical and soft skills")
            recommendations.append("🔹 **Quantify achievements** - Use numbers to show impact")
            recommendations.append("🔹 **Improve formatting** - Use clear sections and bullet points")
            recommendations.append("🔹 **Include projects** - Add personal or academic projects")
            recommendations.append("🔹 **Get certifications** - Consider relevant online certifications")
        
        if len(programming_langs) < 3:
            recommendations.append("💻 **Learn new technologies** - Expand your technical skill set")
        
        if len(skills) < 10:
            recommendations.append("🎯 **Diversify skills** - Add industry-relevant skills")
        
        # Always include these general recommendations
        general_recs = [
            "📝 **Customize for each job** - Tailor your resume for specific roles",
            "🔍 **Proofread carefully** - Check for spelling and grammar errors",
            "📊 **Use action verbs** - Start bullet points with strong verbs",
            "🎨 **Keep it professional** - Use clean, readable formatting",
            "🚀 **Highlight achievements** - Focus on results, not just responsibilities"
        ]
        
        recommendations.extend(general_recs[:5 - len(recommendations)])
        
        return recommendations[:5]  # Return top 5 recommendations

def analyze_resume_file(file_path):
    """Main function to analyze a resume file"""
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze_resume(file_path)
    return result

if __name__ == "__main__":
    # Test with a sample file
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            result = analyze_resume_file(file_path)
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({"success": False, "error": "File not found"}, indent=2))
    else:
        # Create a dummy resume for testing
        dummy_resume = """
        John Doe
        Software Developer
        Phone: (123) 456-7890
        Email: john.doe@email.com
        LinkedIn: linkedin.com/in/johndoe
        
        SUMMARY
        Experienced software developer with 5 years of expertise in Python, JavaScript, and cloud technologies.
        
        SKILLS
        Python, JavaScript, React, Node.js, AWS, Docker, Git, SQL, MongoDB
        
        EXPERIENCE
        Senior Developer - Tech Corp (2019-2024)
        - Developed web applications using Python and React
        - Implemented AWS cloud solutions saving $50k annually
        - Led team of 5 developers
        
        EDUCATION
        Bachelor of Science in Computer Science
        State University (2015-2019)
        GPA: 3.8
        
        CERTIFICATIONS
        AWS Certified Solutions Architect
        Python Developer Certificate
        """
        
        # Save dummy resume to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(dummy_resume)
            temp_path = f.name
        
        try:
            result = analyze_resume_file(temp_path)
            print(json.dumps(result, indent=2))
        finally:
            os.unlink(temp_path)