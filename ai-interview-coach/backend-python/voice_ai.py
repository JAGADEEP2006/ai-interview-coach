import speech_recognition as sr
import librosa
import numpy as np
from textblob import TextBlob
import language_tool_python
import json
import tempfile
import os

class VoiceAnalyzer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tool = language_tool_python.LanguageTool('en-US')
    
    def analyze_audio(self, audio_path, question):
        """Analyze audio recording for speech quality"""
        try:
            # Convert audio to text
            text = self.speech_to_text(audio_path)
            
            if not text:
                return {
                    'success': False,
                    'error': 'Could not transcribe audio. Please speak clearly.'
                }
            
            # Analyze transcription
            text_analysis = self.analyze_text(text, question)
            
            # Analyze audio features
            audio_features = self.analyze_audio_features(audio_path)
            
            # Calculate overall score
            overall_score = (
                text_analysis['clarity_score'] * 0.3 +
                text_analysis['fluency_score'] * 0.3 +
                audio_features['confidence_score'] * 0.2 +
                audio_features['pace_score'] * 0.2
            )
            
            # Generate feedback
            feedback = self.generate_feedback(
                text_analysis, audio_features, text
            )
            
            return {
                'success': True,
                'transcription': text,
                'text_analysis': text_analysis,
                'audio_features': audio_features,
                'overall_score': round(overall_score, 2),
                'feedback': feedback
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def speech_to_text(self, audio_path):
        """Convert speech to text using Google Speech Recognition"""
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
    
    def analyze_text(self, text, question):
        """Analyze transcribed text"""
        # Grammar check
        matches = self.tool.check(text)
        grammar_errors = len(matches)
        grammar_score = max(0, 100 - (grammar_errors * 3))
        
        # Fluency (based on sentence structure)
        sentences = text.split('.')
        fluency_score = self.calculate_fluency_score(sentences)
        
        # Clarity (vocabulary and structure)
        clarity_score = self.calculate_clarity_score(text)
        
        # Relevance to question
        relevance_score = self.calculate_relevance_score(question, text)
        
        return {
            'grammar_errors': grammar_errors,
            'grammar_score': round(grammar_score, 2),
            'fluency_score': round(fluency_score, 2),
            'clarity_score': round(clarity_score, 2),
            'relevance_score': round(relevance_score, 2)
        }
    
    def analyze_audio_features(self, audio_path):
        """Analyze audio features like pace, pauses, etc."""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path)
            
            # Calculate speaking rate (words per minute approximation)
            duration = librosa.get_duration(y=y, sr=sr)
            words = len(librosa.effects.split(y, top_db=30)) / 10  # Approximation
            wpm = (words / duration) * 60 if duration > 0 else 0
            
            # Pace score (optimal 120-150 WPM)
            if 120 <= wpm <= 150:
                pace_score = 100
            elif 100 <= wpm < 120 or 150 < wpm <= 180:
                pace_score = 70
            else:
                pace_score = 50
            
            # Detect pauses (silence)
            intervals = librosa.effects.split(y, top_db=30)
            pause_count = len(intervals) - 1
            pause_score = max(0, 100 - (pause_count * 5))
            
            # Confidence (based on volume consistency)
            rms = librosa.feature.rms(y=y)
            volume_variance = np.var(rms)
            confidence_score = max(0, 100 - (volume_variance * 100))
            
            return {
                'duration': round(duration, 2),
                'estimated_wpm': round(wpm, 2),
                'pace_score': round(pace_score, 2),
                'pause_count': pause_count,
                'pause_score': round(pause_score, 2),
                'confidence_score': round(min(confidence_score, 100), 2)
            }
            
        except Exception as e:
            print(f"Audio feature analysis error: {e}")
            return {
                'duration': 0,
                'estimated_wpm': 0,
                'pace_score': 50,
                'pause_count': 0,
                'pause_score': 50,
                'confidence_score': 50
            }
    
    def calculate_fluency_score(self, sentences):
        """Calculate fluency based on sentence structure"""
        if not sentences or len(sentences) < 2:
            return 50
        
        # Check for sentence length variety
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if len(lengths) < 2:
            return 60
        
        avg_length = sum(lengths) / len(lengths)
        
        # Optimal sentence length 10-20 words
        if 10 <= avg_length <= 20:
            return 80
        elif 5 <= avg_length < 10 or 20 < avg_length <= 25:
            return 70
        else:
            return 60
    
    def calculate_clarity_score(self, text):
        """Calculate clarity score"""
        words = text.lower().split()
        if len(words) < 10:
            return 30
        
        # Simple clarity metrics
        unique_words = set(words)
        vocab_ratio = len(unique_words) / len(words)
        
        # Sentence count
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        if vocab_ratio > 0.6 and sentence_count > 1:
            return 85
        elif vocab_ratio > 0.4 and sentence_count > 0:
            return 70
        else:
            return 55
    
    def calculate_relevance_score(self, question, answer):
        """Calculate relevance between question and answer"""
        q_words = set(question.lower().split())
        a_words = set(answer.lower().split())
        
        if not q_words:
            return 50
        
        common_words = q_words.intersection(a_words)
        relevance = len(common_words) / len(q_words) * 100
        return min(relevance, 100)
    
    def generate_feedback(self, text_analysis, audio_features, transcription):
        """Generate comprehensive feedback"""
        feedback = []
        
        # Grammar feedback
        if text_analysis['grammar_errors'] == 0:
            feedback.append("Excellent grammar in your speech!")
        elif text_analysis['grammar_errors'] <= 2:
            feedback.append(f"Good grammar with {text_analysis['grammar_errors']} minor errors.")
        else:
            feedback.append(f"Grammar needs improvement: {text_analysis['grammar_errors']} errors found.")
        
        # Fluency feedback
        if text_analysis['fluency_score'] >= 80:
            feedback.append("Very fluent speech delivery.")
        elif text_analysis['fluency_score'] >= 60:
            feedback.append("Good fluency, could be more natural.")
        else:
            feedback.append("Work on speaking more fluently without pauses.")
        
        # Pace feedback
        wpm = audio_features['estimated_wpm']
        if 120 <= wpm <= 150:
            feedback.append("Perfect speaking pace.")
        elif wpm < 120:
            feedback.append("Try speaking a bit faster.")
        else:
            feedback.append("Try speaking a bit slower for better clarity.")
        
        # Confidence feedback
        if audio_features['confidence_score'] >= 80:
            feedback.append("You sound confident!")
        elif audio_features['confidence_score'] >= 60:
            feedback.append("Good confidence level.")
        else:
            feedback.append("Try to speak with more confidence.")
        
        # Pause feedback
        if audio_features['pause_count'] <= 2:
            feedback.append("Good use of pauses.")
        elif audio_features['pause_count'] <= 5:
            feedback.append("Moderate use of pauses.")
        else:
            feedback.append("Too many pauses. Try to speak more continuously.")
        
        return " ".join(feedback)

if __name__ == "__main__":
    analyzer = VoiceAnalyzer()
    # Test with sample
    result = analyzer.analyze_audio("sample.wav", "Tell me about yourself")
    print(json.dumps(result, indent=2))