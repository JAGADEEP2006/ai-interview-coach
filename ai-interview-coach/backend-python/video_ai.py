import cv2
import mediapipe as mp
import numpy as np
import json
import tempfile
import os
from datetime import datetime

class VideoAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        
    def analyze_video(self, video_path):
        """Analyze video for body language and eye contact"""
        try:
            # Extract video features
            features = self.extract_video_features(video_path)
            
            # Calculate scores
            eye_contact_score = self.calculate_eye_contact_score(features['eye_contact_frames'])
            posture_score = self.calculate_posture_score(features['posture_data'])
            gesture_score = self.calculate_gesture_score(features['gesture_data'])
            expression_score = self.calculate_expression_score(features['expression_data'])
            
            # Overall score
            overall_score = (
                eye_contact_score * 0.4 +
                posture_score * 0.3 +
                gesture_score * 0.2 +
                expression_score * 0.1
            )
            
            # Generate feedback
            feedback = self.generate_feedback(
                eye_contact_score, posture_score, 
                gesture_score, expression_score,
                features
            )
            
            return {
                'success': True,
                'analysis': {
                    'eye_contact_score': round(eye_contact_score, 2),
                    'posture_score': round(posture_score, 2),
                    'gesture_score': round(gesture_score, 2),
                    'expression_score': round(expression_score, 2),
                    'overall_score': round(overall_score, 2),
                    'total_frames': features['total_frames'],
                    'duration': features['duration']
                },
                'feedback': feedback,
                'recommendations': self.get_recommendations(overall_score)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_video_features(self, video_path):
        """Extract features from video"""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        # Initialize MediaPipe
        face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        eye_contact_frames = 0
        posture_data = []
        gesture_data = []
        expression_data = []
        
        frame_count = 0
        while cap.isOpened() and frame_count < min(total_frames, 300):  # Limit to 300 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            face_results = face_mesh.process(rgb_frame)
            pose_results = pose.process(rgb_frame)
            
            # Analyze eye contact
            if face_results.multi_face_landmarks:
                eye_contact = self.detect_eye_contact(face_results.multi_face_landmarks[0])
                if eye_contact:
                    eye_contact_frames += 1
            
            # Analyze posture
            if pose_results.pose_landmarks:
                posture = self.analyze_posture(pose_results.pose_landmarks)
                posture_data.append(posture)
            
            # Analyze gestures
            if pose_results.pose_landmarks:
                gesture = self.detect_gestures(pose_results.pose_landmarks)
                gesture_data.append(gesture)
            
            # Analyze facial expression
            if face_results.multi_face_landmarks:
                expression = self.analyze_expression(face_results.multi_face_landmarks[0])
                expression_data.append(expression)
            
            frame_count += 1
        
        cap.release()
        
        return {
            'total_frames': total_frames,
            'duration': duration,
            'eye_contact_frames': eye_contact_frames,
            'posture_data': posture_data,
            'gesture_data': gesture_data,
            'expression_data': expression_data
        }
    
    def detect_eye_contact(self, face_landmarks):
        """Detect if person is looking at camera"""
        # Simplified eye contact detection
        # Using relative positions of eye landmarks
        left_eye = []
        right_eye = []
        
        # Left eye landmarks (indices 33, 133, 157, 158, 159, 160, 161, 173)
        left_eye_indices = [33, 133, 157, 158, 159, 160, 161, 173]
        for idx in left_eye_indices:
            landmark = face_landmarks.landmark[idx]
            left_eye.append((landmark.x, landmark.y))
        
        # Right eye landmarks (indices 362, 263, 387, 388, 389, 390, 391, 466)
        right_eye_indices = [362, 263, 387, 388, 389, 390, 391, 466]
        for idx in right_eye_indices:
            landmark = face_landmarks.landmark[idx]
            right_eye.append((landmark.x, landmark.y))
        
        # Calculate eye aspect ratio (simplified)
        left_ear = self.eye_aspect_ratio(left_eye)
        right_ear = self.eye_aspect_ratio(right_eye)
        
        # If eyes are open (not blinking) and centered
        if left_ear > 0.2 and right_ear > 0.2:
            return True
        return False
    
    def eye_aspect_ratio(self, eye_points):
        """Calculate eye aspect ratio"""
        if len(eye_points) < 6:
            return 0
        
        # Vertical distances
        A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
        B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
        
        # Horizontal distance
        C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
        
        if C == 0:
            return 0
        
        ear = (A + B) / (2.0 * C)
        return ear
    
    def analyze_posture(self, pose_landmarks):
        """Analyze posture from pose landmarks"""
        # Get key points
        left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
        
        # Calculate shoulder alignment
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        hip_diff = abs(left_hip.y - right_hip.y)
        
        # Calculate spine alignment
        avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        avg_hip_y = (left_hip.y + right_hip.y) / 2
        
        spine_angle = abs(avg_shoulder_y - avg_hip_y)
        
        return {
            'shoulder_alignment': shoulder_diff,
            'hip_alignment': hip_diff,
            'spine_straightness': spine_angle
        }
    
    def detect_gestures(self, pose_landmarks):
        """Detect hand gestures"""
        left_hand_raised = False
        right_hand_raised = False
        
        # Check if hands are above shoulders
        left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        if left_wrist.y < left_shoulder.y:
            left_hand_raised = True
        if right_wrist.y < right_shoulder.y:
            right_hand_raised = True
        
        return {
            'left_hand_raised': left_hand_raised,
            'right_hand_raised': right_hand_raised,
            'gesturing': left_hand_raised or right_hand_raised
        }
    
    def analyze_expression(self, face_landmarks):
        """Analyze facial expression"""
        # Simplified smile detection
        mouth_left = face_landmarks.landmark[61]
        mouth_right = face_landmarks.landmark[291]
        mouth_top = face_landmarks.landmark[13]
        mouth_bottom = face_landmarks.landmark[14]
        
        mouth_width = abs(mouth_right.x - mouth_left.x)
        mouth_height = abs(mouth_bottom.y - mouth_top.y)
        
        # Smile ratio
        if mouth_height > 0:
            smile_ratio = mouth_width / mouth_height
            smiling = smile_ratio > 2.0
        else:
            smiling = False
        
        return {
            'smiling': smiling,
            'mouth_openness': mouth_height
        }
    
    def calculate_eye_contact_score(self, eye_contact_frames):
        """Calculate eye contact score"""
        # Base score on percentage of frames with eye contact
        if eye_contact_frames == 0:
            return 30
        
        # Assuming we analyzed 300 frames max
        percentage = (eye_contact_frames / 300) * 100
        
        if percentage >= 70:
            return 90
        elif percentage >= 50:
            return 75
        elif percentage >= 30:
            return 60
        else:
            return 40
    
    def calculate_posture_score(self, posture_data):
        """Calculate posture score"""
        if not posture_data:
            return 50
        
        # Average alignment scores
        shoulder_scores = []
        spine_scores = []
        
        for posture in posture_data:
            # Good posture has low differences
            shoulder_score = max(0, 100 - (posture['shoulder_alignment'] * 1000))
            spine_score = max(0, 100 - (posture['spine_straightness'] * 1000))
            
            shoulder_scores.append(shoulder_score)
            spine_scores.append(spine_score)
        
        avg_shoulder = np.mean(shoulder_scores) if shoulder_scores else 50
        avg_spine = np.mean(spine_scores) if spine_scores else 50
        
        return (avg_shoulder + avg_spine) / 2
    
    def calculate_gesture_score(self, gesture_data):
        """Calculate gesture score"""
        if not gesture_data:
            return 50
        
        gesture_counts = [g['gesturing'] for g in gesture_data]
        gesture_percentage = sum(gesture_counts) / len(gesture_counts) * 100
        
        # Moderate gesturing is best (30-60%)
        if 30 <= gesture_percentage <= 60:
            return 85
        elif 20 <= gesture_percentage < 30 or 60 < gesture_percentage <= 70:
            return 70
        elif gesture_percentage > 70:
            return 60  # Too much gesturing
        else:
            return 40  # Too little gesturing
    
    def calculate_expression_score(self, expression_data):
        """Calculate facial expression score"""
        if not expression_data:
            return 50
        
        smile_counts = [e['smiling'] for e in expression_data]
        smile_percentage = sum(smile_counts) / len(smile_counts) * 100
        
        # Some smiling is good, but not forced
        if 20 <= smile_percentage <= 50:
            return 80
        elif smile_percentage > 50:
            return 65  # Might be forced
        else:
            return 40  # Too serious
    
    def generate_feedback(self, eye_score, posture_score, gesture_score, expression_score, features):
        """Generate feedback based on scores"""
        feedback = []
        
        # Eye contact feedback
        if eye_score >= 80:
            feedback.append("Excellent eye contact with the camera.")
        elif eye_score >= 60:
            feedback.append("Good eye contact, maintain it consistently.")
        else:
            feedback.append("Improve eye contact by looking at the camera more.")
        
        # Posture feedback
        if posture_score >= 80:
            feedback.append("Great posture - you appear confident and professional.")
        elif posture_score >= 60:
            feedback.append("Good posture overall.")
        else:
            feedback.append("Try to sit up straight for better presence.")
        
        # Gesture feedback
        if gesture_score >= 80:
            feedback.append("Effective use of hand gestures.")
        elif gesture_score >= 60:
            feedback.append("Good gesture usage.")
        else:
            feedback.append("Try using hand gestures to emphasize points.")
        
        # Expression feedback
        if expression_score >= 80:
            feedback.append("Natural and positive facial expressions.")
        elif expression_score >= 60:
            feedback.append("Good facial expressions.")
        else:
            feedback.append("Try to smile naturally to appear more approachable.")
        
        # Duration feedback
        duration = features['duration']
        if 60 <= duration <= 120:
            feedback.append("Perfect answer length.")
        elif duration < 60:
            feedback.append("Consider giving more detailed answers.")
        else:
            feedback.append("Try to be more concise in your answers.")
        
        return " ".join(feedback)
    
    def get_recommendations(self, overall_score):
        """Get improvement recommendations"""
        recommendations = []
        
        if overall_score >= 80:
            recommendations = [
                "You're interview-ready! Maintain your current approach.",
                "Practice with different types of questions.",
                "Record mock interviews regularly to stay sharp."
            ]
        elif overall_score >= 60:
            recommendations = [
                "Focus on maintaining consistent eye contact.",
                "Practice your posture in front of a mirror.",
                "Work on speaking clearly and confidently.",
                "Record yourself answering common interview questions."
            ]
        else:
            recommendations = [
                "Practice basic interview questions daily.",
                "Work on maintaining eye contact with the camera.",
                "Record and review your practice sessions.",
                "Focus on speaking clearly and at a moderate pace.",
                "Practice good posture while sitting."
            ]
        
        return recommendations

if __name__ == "__main__":
    analyzer = VideoAnalyzer()
    # Test with sample
    result = analyzer.analyze_video("sample.mp4")
    print(json.dumps(result, indent=2)) 
