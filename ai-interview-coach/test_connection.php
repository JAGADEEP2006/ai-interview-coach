<?php
header('Content-Type: text/plain');

echo "=== AI Interview Coach System Test ===\n\n";

// Test 1: PHP Version
echo "1. PHP Version: " . PHP_VERSION . "\n";
echo "   Status: " . (version_compare(PHP_VERSION, '7.4.0') >= 0 ? "✓ OK" : "✗ Too old") . "\n\n";

// Test 2: Required Extensions
$extensions = ['pdo_mysql', 'json', 'mbstring', 'fileinfo', 'curl'];
echo "2. Required Extensions:\n";
foreach ($extensions as $ext) {
    echo "   - $ext: " . (extension_loaded($ext) ? "✓ Loaded" : "✗ Missing") . "\n";
}
echo "\n";

// Test 3: Database Connection
echo "3. Database Connection:\n";
try {
    $pdo = new PDO('mysql:host=localhost;dbname=ai_interview_coach', 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo "   ✓ Connected successfully\n";
    
    // Check tables
    $stmt = $pdo->query("SHOW TABLES");
    $tables = $stmt->fetchAll(PDO::FETCH_COLUMN);
    echo "   ✓ Tables found: " . count($tables) . "\n";
    foreach ($tables as $table) {
        echo "     - $table\n";
    }
} catch (PDOException $e) {
    echo "   ✗ Connection failed: " . $e->getMessage() . "\n";
}
echo "\n";

// Test 4: Directory Permissions
$dirs = [
    'backend-php/uploads' => 'Uploads directory',
    'backend-python/output' => 'Python output directory'
];

echo "4. Directory Permissions:\n";
foreach ($dirs as $dir => $desc) {
    $path = __DIR__ . '/' . $dir;
    if (file_exists($path)) {
        if (is_writable($path)) {
            echo "   ✓ $desc: Writable\n";
        } else {
            echo "   ✗ $desc: Not writable\n";
        }
    } else {
        echo "   ✗ $desc: Does not exist\n";
    }
}
echo "\n";

// Test 5: Python Dependencies
echo "5. Python Dependencies:\n";
$python_script = __DIR__ . '/backend-python/test_deps.py';
file_put_contents($python_script, "import sys\nprint('Python ' + sys.version)");

exec('python ' . escapeshellarg($python_script) . ' 2>&1', $output, $return_code);
if ($return_code === 0) {
    echo "   ✓ Python: " . $output[0] . "\n";
} else {
    echo "   ✗ Python: Not working\n";
}
unlink($python_script);

// Test 6: Web Server
echo "6. Web Server Test:\n";
$url = 'http://localhost/ai-interview-coach/index.html';
$headers = @get_headers($url);
if ($headers && strpos($headers[0], '200')) {
    echo "   ✓ Web server responding\n";
} else {
    echo "   ✗ Web server not responding\n";
}

echo "\n=== Test Complete ===\n";
echo "If all tests pass, the system should be working correctly.\n";
echo "Access the application at: http://localhost/ai-interview-coach\n";
?>