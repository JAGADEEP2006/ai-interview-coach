<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type");

require_once '../config/db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents("php://input"));
    
    if (!isset($data->user_id) || !isset($data->answers)) {
        echo json_encode(["success" => false, "message" => "Missing data"]);
        exit;
    }
    
    $db = new Database();
    $conn = $db->getConnection();
    
    $user_id = $data->user_id;
    $answers = $data->answers;
    
    // Analyze each answer
    $total_score = 0;
    $all_feedback = [];
    $question_count = count((array)$answers);
    
    foreach ($answers as $question_id => $answer_text) {
        // Get question from database
        $stmt = $conn->prepare("SELECT question FROM questions WHERE id = :id");
        $stmt->bindParam(":id", $question_id);
        $stmt->execute();
        $question = $stmt->fetch(PDO::FETCH_ASSOC)['question'] ?? "General question";
        
        // Call Python AI analysis
        $analysis = analyzeTextWithPython($question, $answer_text);
        
        if ($analysis['success']) {
            $total_score += $analysis['overall_score'];
            $all_feedback[] = "Q" . $question_id . ": " . $analysis['feedback'];
        }
    }
    
    // Calculate average score
    $average_score = $question_count > 0 ? $total_score / $question_count : 0;
    $combined_feedback = implode("\n\n", $all_feedback);
    
    // Save to database
    $query = "INSERT INTO tests (user_id, test_type, score, feedback) 
              VALUES (:user_id, 'text', :score, :feedback)";
    
    $stmt = $conn->prepare($query);
    $stmt->bindParam(":user_id", $user_id);
    $stmt->bindParam(":score", $average_score);
    $stmt->bindParam(":feedback", $combined_feedback);
    
    if ($stmt->execute()) {
        echo json_encode([
            "success" => true,
            "message" => "Text test analyzed successfully",
            "score" => round($average_score, 2),
            "feedback" => $combined_feedback
        ]);
    } else {
        echo json_encode(["success" => false, "message" => "Failed to save results"]);
    }
}

function analyzeTextWithPython($question, $answer) {
    $python_script = __DIR__ . "/../../backend-python/text_ai.py";
    $command = "python " . escapeshellarg($python_script) . " " . 
               escapeshellarg($question) . " " . escapeshellarg($answer);
    $output = shell_exec($command);
    
    if ($output) {
        return json_decode($output, true);
    }
    
    return ["success" => false, "error" => "Python script execution failed"];
}
?>