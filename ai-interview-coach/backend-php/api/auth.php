<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");

require_once '../config/db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents("php://input"));
    
    if (isset($data->action)) {
        $db = new Database();
        $conn = $db->getConnection();
        
        switch($data->action) {
            case 'register':
                registerUser($conn, $data);
                break;
            case 'login':
                loginUser($conn, $data);
                break;
            default:
                echo json_encode(["success" => false, "message" => "Invalid action"]);
        }
    }
}

function registerUser($conn, $data) {
    if (!isset($data->username) || !isset($data->email) || !isset($data->password)) {
        echo json_encode(["success" => false, "message" => "Missing required fields"]);
        return;
    }
    
    $username = $data->username;
    $email = $data->email;
    $password = password_hash($data->password, PASSWORD_DEFAULT);
    $full_name = $data->full_name ?? '';
    
    $query = "INSERT INTO users (username, email, password, full_name) 
              VALUES (:username, :email, :password, :full_name)";
    
    $stmt = $conn->prepare($query);
    $stmt->bindParam(":username", $username);
    $stmt->bindParam(":email", $email);
    $stmt->bindParam(":password", $password);
    $stmt->bindParam(":full_name", $full_name);
    
    if ($stmt->execute()) {
        echo json_encode(["success" => true, "message" => "Registration successful"]);
    } else {
        echo json_encode(["success" => false, "message" => "Registration failed"]);
    }
}

function loginUser($conn, $data) {
    if (!isset($data->email) || !isset($data->password)) {
        echo json_encode(["success" => false, "message" => "Missing credentials"]);
        return;
    }
    
    $email = $data->email;
    $password = $data->password;
    
    $query = "SELECT * FROM users WHERE email = :email";
    $stmt = $conn->prepare($query);
    $stmt->bindParam(":email", $email);
    $stmt->execute();
    
    if ($stmt->rowCount() > 0) {
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if (password_verify($password, $user['password'])) {
            unset($user['password']);
            echo json_encode([
                "success" => true,
                "message" => "Login successful",
                "user" => $user
            ]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid credentials"]);
        }
    } else {
        echo json_encode(["success" => false, "message" => "User not found"]);
    }
}
?>