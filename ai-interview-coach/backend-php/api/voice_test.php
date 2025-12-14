<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type");

require_once '../config/db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $db = new Database();
    $conn = $db->getConnection();
    
    if (!isset($_FILES['audio']) || !isset($_POST['user_id'])) {
        echo json_encode(["success" => false, "message" => "Missing data"]);
        exit;
    }
    
    $user_id = $_POST['user_id'];
    $question_id = $_POST['question_id'] ?? 0;
    $audio_file = $_FILES['audio'];
    
    // Validate audio file
    $allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/webm'];
    $max_size = 10 * 1024 * 1024; // 10MB
    
    if (!in_array($audio_file['type'], $allowed_types)) {
        echo json_encode(["success" => false, "message" => "Invalid audio format"]);
        exit;
    }
    
    if ($audio_file['size'] > $max_size) {
        echo json_encode(["success" => false, "message" => "Audio file too large"]);
        exit;
    }
    
    // Create upload directory
    $upload_dir = "../uploads/audio/";
    if (!file_exists($upload_dir)) {
        mkdir($upload_dir, 0777, true);
    }
    
    // Generate unique filename
    $filename = uniqid() . '_' . time() . '.wav';
    $file_path = $upload_dir . $filename;
    
    // Convert to WAV if needed
    if ($audio_file['type'] !== 'audio/wav') {
        // For simplicity, we'll just move it
        // In production, convert to WAV using FFmpeg
    }
    
    if (move_uploaded_file($audio_file['tmp_name'], $file_path)) {
        // Get question text from database
        $question_text = "Tell me about yourself"; // Default
        if ($question_id > 0) {
            $stmt = $conn->prepare("SELECT question FROM questions WHERE id = :id");
            $stmt->bindParam(":id", $question_id);
            $stmt->execute();
            if ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $question_text = $row['question'];
            }
        }
        
        // Call Python AI analysis
        $python_result = analyzeVoiceWithPython($file_path, $question_text);
        
        if ($python_result['success']) {
            // Save to database
            $query = "INSERT INTO tests (user_id, test_type, score, feedback) 
                      VALUES (:user_id, 'voice', :score, :feedback)";
            
            $stmt = $conn->prepare($query);
            $stmt->bindParam(":user_id", $user_id);
            $stmt->bindParam(":score", $python_result['overall_score']);
            $stmt->bindParam(":feedback", $python_result['feedback']);
            
            if ($stmt->execute()) {
                echo json_encode([
                    "success" => true,
                    "message" => "Voice test analyzed successfully",
                    "data" => $python_result
                ]);
            } else {
                echo json_encode(["success" => false, "message" => "Failed to save results"]);
            }
        } else {
            echo json_encode(["success" => false, "message" => "AI analysis failed"]);
        }
        
        // Clean up audio file
        unlink($file_path);
    } else {
        echo json_encode(["success" => false, "message" => "Failed to upload audio"]);
    }
}

function analyzeVoiceWithPython($audio_path, $question) {
    $python_script = __DIR__ . "/../../backend-python/voice_ai.py";
    $command = "python " . escapeshellarg($python_script) . " " . 
               escapeshellarg($audio_path) . " " . escapeshellarg($question);
    $output = shell_exec($command);
    
    if ($output) {
        return json_decode($output, true);
    }
    
    return ["success" => false, "error" => "Python script execution failed"];
}
?>