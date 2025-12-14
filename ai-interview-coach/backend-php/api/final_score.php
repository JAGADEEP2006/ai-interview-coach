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
    
    // Get latest scores for each test type
    $scores = [
        'resume' => 0,
        'text' => 0,
        'voice' => 0,
        'video' => 0
    ];
    
    // Get resume score
    $stmt = $conn->prepare("SELECT score FROM resumes WHERE user_id = :user_id ORDER BY uploaded_at DESC LIMIT 1");
    $stmt->bindParam(":user_id", $user_id);
    $stmt->execute();
    if ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $scores['resume'] = (float)$row['score'];
    }
    
    // Get text test score
    $stmt = $conn->prepare("SELECT score FROM tests WHERE user_id = :user_id AND test_type = 'text' ORDER BY created_at DESC LIMIT 1");
    $stmt->bindParam(":user_id", $user_id);
    $stmt->execute();
    if ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $scores['text'] = (float)$row['score'];
    }
    
    // Get voice test score
    $stmt = $conn->prepare("SELECT score FROM tests WHERE user_id = :user_id AND test_type = 'voice' ORDER BY created_at DESC LIMIT 1");
    $stmt->bindParam(":user_id", $user_id);
    $stmt->execute();
    if ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $scores['voice'] = (float)$row['score'];
    }
    
    // Get video test score
    $stmt = $conn->prepare("SELECT score FROM tests WHERE user_id = :user_id AND test_type = 'video' ORDER BY created_at DESC LIMIT 1");
    $stmt->bindParam(":user_id", $user_id);
    $stmt->execute();
    if ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $scores['video'] = (float)$row['score'];
    }
    
    // Calculate overall score (weighted)
    $overall_score = (
        $scores['resume'] * 0.2 +
        $scores['text'] * 0.25 +
        $scores['voice'] * 0.25 +
        $scores['video'] * 0.3
    );
    
    // Determine status
    if ($overall_score >= 70) {
        $status = 'pass';
        $status_message = 'Congratulations! You are ready for real interviews.';
        $recommendations = [
            'Practice with different interviewers',
            'Research company-specific questions',
            'Prepare questions to ask the interviewer'
        ];
    } elseif ($overall_score >= 50) {
        $status = 'pending';
        $status_message = 'Good progress! You need more practice.';
        $recommendations = [
            'Focus on your weakest area',
            'Practice daily for 30 minutes',
            'Record and review your practice sessions'
        ];
    } else {
        $status = 'fail';
        $status_message = 'Needs significant improvement. Keep practicing!';
        $recommendations = [
            'Start with basic interview questions',
            'Work on confidence and communication',
            'Seek feedback from mentors',
            'Practice in front of a mirror'
        ];
    }
    
    // Generate detailed feedback
    $feedback = $this->generateDetailedFeedback($scores);
    
    // Save overall result
    $query = "INSERT INTO results (user_id, resume_score, text_score, voice_score, video_score, 
              overall_score, status, feedback) 
              VALUES (:user_id, :resume_score, :text_score, :voice_score, :video_score, 
              :overall_score, :status, :feedback)";
    
    $stmt = $conn->prepare($query);
    $stmt->bindParam(":user_id", $user_id);
    $stmt->bindParam(":resume_score", $scores['resume']);
    $stmt->bindParam(":text_score", $scores['text']);
    $stmt->bindParam(":voice_score", $scores['voice']);
    $stmt->bindParam(":video_score", $scores['video']);
    $stmt->bindParam(":overall_score", $overall_score);
    $stmt->bindParam(":status", $status);
    $stmt->bindParam(":feedback", $feedback);
    
    $stmt->execute();
    
    echo json_encode([
        "success" => true,
        "scores" => $scores,
        "overall_score" => round($overall_score, 2),
        "status" => $status,
        "status_message" => $status_message,
        "feedback" => $feedback,
        "recommendations" => $recommendations,
        "chart_data" => $this->prepareChartData($scores, $overall_score)
    ]);
}

function generateDetailedFeedback($scores) {
    $feedback = [];
    
    // Resume feedback
    if ($scores['resume'] >= 80) {
        $feedback[] = "Resume: Excellent! Your resume is well-structured and highlights key skills.";
    } elseif ($scores['resume'] >= 60) {
        $feedback[] = "Resume: Good. Consider adding more quantifiable achievements.";
    } else {
        $feedback[] = "Resume: Needs improvement. Focus on formatting and content clarity.";
    }
    
    // Text test feedback
    if ($scores['text'] >= 80) {
        $feedback[] = "Written Communication: Excellent grammar and clarity in written responses.";
    } elseif ($scores['text'] >= 60) {
        $feedback[] = "Written Communication: Good. Work on vocabulary and sentence structure.";
    } else {
        $feedback[] = "Written Communication: Needs practice. Focus on grammar and organization.";
    }
    
    // Voice test feedback
    if ($scores['voice'] >= 80) {
        $feedback[] = "Verbal Communication: Clear, confident speech with good fluency.";
    } elseif ($scores['voice'] >= 60) {
        $feedback[] = "Verbal Communication: Good. Work on pace and pronunciation.";
    } else {
        $feedback[] = "Verbal Communication: Needs significant improvement in clarity and confidence.";
    }
    
    // Video test feedback
    if ($scores['video'] >= 80) {
        $feedback[] = "Presentation Skills: Excellent body language, eye contact, and professionalism.";
    } elseif ($scores['video'] >= 60) {
        $feedback[] = "Presentation Skills: Good. Improve eye contact and posture.";
    } else {
        $feedback[] = "Presentation Skills: Focus on body language, eye contact, and professional presence.";
    }
    
    return implode("\n\n", $feedback);
}

function prepareChartData($scores, $overall) {
    return [
        'labels' => ['Resume', 'Text Test', 'Voice Test', 'Video Test', 'Overall'],
        'datasets' => [
            [
                'label' => 'Scores',
                'data' => [
                    $scores['resume'],
                    $scores['text'],
                    $scores['voice'],
                    $scores['video'],
                    $overall
                ],
                'backgroundColor' => [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(153, 102, 255, 0.6)'
                ]
            ]
        ]
    ];
}
?>