<?php
class Database {
    private $host = "localhost";
    private $db_name = "ai_interview_coach";
    private $username = "root";
    private $password = "";
    public $conn;
    private $error;

    public function getConnection() {
        $this->conn = null;
        try {
            $this->conn = new PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->db_name . ";charset=utf8mb4",
                $this->username,
                $this->password,
                array(
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES => false,
                    PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            );
        } catch(PDOException $exception) {
            $this->error = "Connection error: " . $exception->getMessage();
            error_log($this->error);
            // Return false instead of echoing in production
            return false;
        }
        return $this->conn;
    }

    public function getError() {
        return $this->error;
    }

    // Helper function for executing queries
    public function executeQuery($sql, $params = []) {
        try {
            $stmt = $this->conn->prepare($sql);
            $stmt->execute($params);
            return $stmt;
        } catch (PDOException $e) {
            $this->error = "Query error: " . $e->getMessage();
            error_log($this->error);
            return false;
        }
    }

    // Helper function for fetching single row
    public function fetchOne($sql, $params = []) {
        $stmt = $this->executeQuery($sql, $params);
        if ($stmt) {
            return $stmt->fetch();
        }
        return false;
    }

    // Helper function for fetching all rows
    public function fetchAll($sql, $params = []) {
        $stmt = $this->executeQuery($sql, $params);
        if ($stmt) {
            return $stmt->fetchAll();
        }
        return false;
    }
}
?>