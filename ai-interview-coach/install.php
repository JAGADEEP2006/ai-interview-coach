<?php
echo "<h2>AI Interview Coach Installation</h2>";

// Check PHP version
if (version_compare(PHP_VERSION, '7.4.0') < 0) {
    die("PHP 7.4 or higher is required. You are using " . PHP_VERSION);
}

// Check required extensions
$required_extensions = ['pdo_mysql', 'json', 'mbstring', 'fileinfo'];
$missing_extensions = [];

foreach ($required_extensions as $ext) {
    if (!extension_loaded($ext)) {
        $missing_extensions[] = $ext;
    }
}

if (!empty($missing_extensions)) {
    die("Missing PHP extensions: " . implode(', ', $missing_extensions));
}

// Check if database can be connected
try {
    $pdo = new PDO('mysql:host=localhost', 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo "✓ Database connection successful<br>";
} catch (PDOException $e) {
    die("✗ Database connection failed: " . $e->getMessage());
}

// Create database
try {
    $pdo->exec("CREATE DATABASE IF NOT EXISTS ai_interview_coach CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
    echo "✓ Database created<br>";
    
    $pdo->exec("USE ai_interview_coach");
    
    // Read SQL file
    $sql_file = __DIR__ . '/database.sql';
    if (file_exists($sql_file)) {
        $sql = file_get_contents($sql_file);
        $pdo->exec($sql);
        echo "✓ Tables created<br>";
    } else {
        echo "⚠ SQL file not found<br>";
    }
} catch (PDOException $e) {
    die("✗ Database setup failed: " . $e->getMessage());
}

// Create upload directories
$directories = [
    'backend-php/uploads/resumes',
    'backend-php/uploads/audio',
    'backend-php/uploads/video',
    'backend-python/output',
    'backend-python/ml-models'
];

foreach ($directories as $dir) {
    $path = __DIR__ . '/' . $dir;
    if (!file_exists($path)) {
        if (mkdir($path, 0777, true)) {
            echo "✓ Directory created: $dir<br>";
        } else {
            echo "⚠ Failed to create directory: $dir<br>";
        }
    } else {
        echo "✓ Directory exists: $dir<br>";
    }
}

// Check Python
exec('python --version 2>&1', $python_output, $python_return);
if ($python_return === 0) {
    echo "✓ Python found: " . $python_output[0] . "<br>";
} else {
    echo "⚠ Python not found or not in PATH<br>";
}

echo "<h3>Installation Complete!</h3>";
echo "<p>Next steps:</p>";
echo "<ol>";
echo "<li>Access the application at: <a href='http://localhost/ai-interview-coach'>http://localhost/ai-interview-coach</a></li>";
echo "<li>Admin panel: <a href='http://localhost/ai-interview-coach/admin'>http://localhost/ai-interview-coach/admin</a></li>";
echo "<li>Default admin credentials: admin / admin123</li>";
echo "<li>Test user: test@example.com / test123</li>";
echo "</ol>";
?>