<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

require_once '../config/db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    if (!$data || !isset($data['user_id'])) {
        echo json_encode([
            "success" => false,
            "message" => "Invalid request data"
        ]);
        exit;
    }
    
    $db = new Database();
    $conn = $db->getConnection();
    $user_id = $data['user_id'];
    $duration = $data['duration'] ?? 0;
    
    try {
        // Simulate video analysis
        $eye_contact_score = rand(70, 95);
        $posture_score = rand(65, 90);
        $gesture_score = rand(60, 88);
        $expression_score = rand(68, 92);
        
        $overall_score = ($eye_contact_score * 0.4) + 
                        ($posture_score * 0.3) + 
                        ($gesture_score * 0.2) + 
                        ($expression_score * 0.1);
        
        $feedback = generateVideoFeedback($eye_contact_score, $posture_score, $gesture_score, $expression_score);
        
        // Save to database
        $stmt = $conn->prepare("
            INSERT INTO tests (user_id, test_type, score, duration, feedback, is_completed, completion_date)
            VALUES (:user_id, 'video', :score, :duration, :feedback, TRUE, NOW())
        ");
        
        $stmt->bindParam(":user_id", $user_id);
        $stmt->bindParam(":score", $overall_score);
        $stmt->bindParam(":duration", $duration);
        $stmt->bindParam(":feedback", $feedback);
        
        if ($stmt->execute()) {
            $test_id = $conn->lastInsertId();
            
            // Update user progress
            $stmt = $conn->prepare("
                UPDATE user_progress 
                SET has_completed_video_test = TRUE,
                    current_test_type = 'results',
                    last_activity = NOW()
                WHERE user_id = :user_id
            ");
            $stmt->bindParam(":user_id", $user_id);
            $stmt->execute();
            
            echo json_encode([
                "success" => true,
                "message" => "Video test submitted successfully",
                "score" => round($overall_score, 2),
                "overall_score" => round($overall_score, 2),
                "analysis" => [
                    "eye_contact_score" => $eye_contact_score,
                    "posture_score" => $posture_score,
                    "gesture_score" => $gesture_score,
                    "expression_score" => $expression_score
                ],
                "feedback" => $feedback,
                "test_id" => $test_id
            ]);
        } else {
            throw new Exception("Failed to save test");
        }
        
    } catch (Exception $e) {
        echo json_encode([
            "success" => false,
            "message" => "Video test failed: " . $e->getMessage()
        ]);
    }
}

function generateVideoFeedback($eye_contact, $posture, $gesture, $expression) {
    $feedback = [];
    
    if ($eye_contact >= 85) {
        $feedback[] = "Excellent eye contact maintained throughout.";
    } elseif ($eye_contact >= 70) {
        $feedback[] = "Good eye contact, could be more consistent.";
    } else {
        $feedback[] = "Work on maintaining better eye contact.";
    }
    
    if ($posture >= 85) {
        $feedback[] = "Confident and professional posture.";
    } elseif ($posture >= 70) {
        $feedback[] = "Generally good posture.";
    } else {
        $feedback[] = "Improve posture for better presence.";
    }
    
    if ($gesture >= 85) {
        $feedback[] = "Effective use of hand gestures.";
    } elseif ($gesture >= 70) {
        $feedback[] = "Appropriate gestures used.";
    } else {
        $feedback[] = "Consider using more natural gestures.";
    }
    
    if ($expression >= 85) {
        $feedback[] = "Positive and engaging facial expressions.";
    } elseif ($expression >= 70) {
        $feedback[] = "Good facial expressions.";
    } else {
        $feedback[] = "Work on more expressive facial responses.";
    }
    
    return implode(" ", $feedback);
}
?>