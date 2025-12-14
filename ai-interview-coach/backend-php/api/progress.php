<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: GET");
header("Access-Control-Allow-Headers: Content-Type");

require_once '../config/db.php';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (!isset($_GET['user_id'])) {
        echo json_encode(["success" => false, "message" => "User ID required"]);
        exit;
    }
    
    $db = new Database();
    $conn = $db->getConnection();
    $user_id = $_GET['user_id'];
    
    try {
        // Get user progress
        $stmt = $conn->prepare("
            SELECT * FROM user_progress WHERE user_id = :user_id
        ");
        $stmt->bindParam(":user_id", $user_id);
        $stmt->execute();
        
        $progress = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($progress) {
            echo json_encode([
                "success" => true,
                "progress" => $progress
            ]);
        } else {
            // Create default progress
            $stmt = $conn->prepare("
                INSERT INTO user_progress (user_id, current_test_type) 
                VALUES (:user_id, 'resume')
            ");
            $stmt->bindParam(":user_id", $user_id);
            $stmt->execute();
            
            echo json_encode([
                "success" => true,
                "progress" => [
                    "user_id" => $user_id,
                    "current_test_type" => "resume",
                    "has_uploaded_resume" => false,
                    "has_completed_text_test" => false,
                    "has_completed_voice_test" => false,
                    "has_completed_video_test" => false
                ]
            ]);
        }
        
    } catch (Exception $e) {
        echo json_encode([
            "success" => false,
            "message" => "Failed to get progress: " . $e->getMessage()
        ]);
    }
}
?>