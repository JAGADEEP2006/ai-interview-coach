import language_tool_python
import re
from textblob import TextBlob
import json

class TextAnalyzer:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')
    
    def analyze_text(self, question, answer):
        """Analyze text answer for grammar, vocabulary, and clarity"""
        try:
            # Grammar check
            matches = self.tool.check(answer)
            grammar_errors = len(matches)
            
            # Spelling mistakes
            spelling_errors = sum(1 for match in matches if match.ruleIssueType == 'misspelling')
            
            # Calculate grammar score (100 - errors * 2, minimum 0)
            grammar_score = max(0, 100 - (grammar_errors * 2))
            
            # Vocabulary richness (unique words percentage)
            words = re.findall(r'\b\w+\b', answer.lower())
            unique_words = set(words)
            vocab_score = (len(unique_words) / max(len(words), 1)) * 50
            
            # Clarity score based on sentence structure
            clarity_score = self.calculate_clarity_score(answer)
            
            # Relevance to question
            relevance_score = self.calculate_relevance_score(question, answer)
            
            # Overall score (weighted average)
            overall_score = (
                grammar_score * 0.3 +
                vocab_score * 0.2 +
                clarity_score * 0.3 +
                relevance_score * 0.2
            )
            
            # Generate feedback
            feedback = self.generate_feedback(
                grammar_errors, spelling_errors, 
                grammar_score, vocab_score, 
                clarity_score, relevance_score
            )
            
            return {
                'success': True,
                'grammar_errors': grammar_errors,
                'spelling_errors': spelling_errors,
                'grammar_score': round(grammar_score, 2),
                'vocabulary_score': round(vocab_score, 2),
                'clarity_score': round(clarity_score, 2),
                'relevance_score': round(relevance_score, 2),
                'overall_score': round(overall_score, 2),
                'feedback': feedback,
                'suggestions': self.get_suggestions(matches)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculate_clarity_score(self, text):
        """Calculate clarity based on sentence length and complexity"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0
        
        # Average sentence length score
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 10 <= avg_length <= 20:
            length_score = 100
        elif 5 <= avg_length < 10 or 20 < avg_length <= 25:
            length_score = 70
        else:
            length_score = 40
        
        # Sentence structure variety (simple metric)
        structure_variety = min(len(set(len(s.split()) for s in sentences)) * 20, 100)
        
        return (length_score + structure_variety) / 2
    
    def calculate_relevance_score(self, question, answer):
        """Calculate how relevant the answer is to the question"""
        # Simple keyword matching
        question_keywords = set(re.findall(r'\b\w+\b', question.lower()))
        answer_keywords = set(re.findall(r'\b\w+\b', answer.lower()))
        
        common_keywords = question_keywords.intersection(answer_keywords)
        
        if not question_keywords:
            return 50
        
        relevance = len(common_keywords) / len(question_keywords) * 100
        return min(relevance, 100)
    
    def generate_feedback(self, grammar_errors, spelling_errors, 
                         grammar_score, vocab_score, clarity_score, relevance_score):
        """Generate comprehensive feedback"""
        feedback = []
        
        # Grammar feedback
        if grammar_errors == 0:
            feedback.append("Excellent grammar! No errors detected.")
        elif grammar_errors <= 3:
            feedback.append(f"Good grammar with only {grammar_errors} minor errors.")
        else:
            feedback.append(f"Needs improvement: {grammar_errors} grammar errors found.")
        
        # Spelling feedback
        if spelling_errors == 0:
            feedback.append("Perfect spelling!")
        elif spelling_errors <= 2:
            feedback.append(f"Minor spelling issues: {spelling_errors} errors.")
        else:
            feedback.append(f"Spelling needs attention: {spelling_errors} errors found.")
        
        # Vocabulary feedback
        if vocab_score >= 80:
            feedback.append("Rich vocabulary usage.")
        elif vocab_score >= 60:
            feedback.append("Good vocabulary range.")
        else:
            feedback.append("Consider using more varied vocabulary.")
        
        # Clarity feedback
        if clarity_score >= 80:
            feedback.append("Clear and well-structured answers.")
        elif clarity_score >= 60:
            feedback.append("Generally clear, but could be more concise.")
        else:
            feedback.append("Try to structure your answers more clearly.")
        
        # Relevance feedback
        if relevance_score >= 80:
            feedback.append("Answers are highly relevant to questions.")
        elif relevance_score >= 60:
            feedback.append("Answers are mostly relevant.")
        else:
            feedback.append("Try to focus your answers more directly on the questions.")
        
        return " ".join(feedback)
    
    def get_suggestions(self, matches):
        """Get specific suggestions for improvement"""
        suggestions = []
        error_types = {}
        
        for match in matches[:5]:  # Limit to top 5 suggestions
            error_type = match.ruleId
            if error_type not in error_types:
                error_types[error_type] = match.message
        
        for error_type, message in error_types.items():
            suggestions.append(f"{error_type}: {message}")
        
        return suggestions[:3]  # Return top 3 suggestions

# Example usage
if __name__ == "__main__":
    analyzer = TextAnalyzer()
    question = "Tell me about your experience with Python"
    answer = "I have 3 years of experience with Python. I used it for data analysis and web development."
    
    result = analyzer.analyze_text(question, answer)
    print(json.dumps(result, indent=2))