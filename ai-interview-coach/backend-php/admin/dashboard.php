<?php
session_start();
require_once '../config/db.php';

// Check if admin is logged in
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

$db = new Database();
$conn = $db->getConnection();

// Get statistics
$stats = [];

// Total users
$stmt = $conn->query("SELECT COUNT(*) as total FROM users");
$stats['total_users'] = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

// Total resumes
$stmt = $conn->query("SELECT COUNT(*) as total FROM resumes");
$stats['total_resumes'] = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

// Total tests
$stmt = $conn->query("SELECT COUNT(*) as total FROM tests");
$stats['total_tests'] = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

// Recent users (last 7 days)
$stmt = $conn->query("
    SELECT username, email, full_name, created_at 
    FROM users 
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    ORDER BY created_at DESC 
    LIMIT 10
");
$recent_users = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Recent tests
$stmt = $conn->query("
    SELECT t.*, u.username 
    FROM tests t 
    JOIN users u ON t.user_id = u.id 
    ORDER BY t.created_at DESC 
    LIMIT 10
");
$recent_tests = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - AI Interview Coach</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <style>
        body {
            background-color: #f5f7fb;
        }
        .sidebar {
            background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            min-height: 100vh;
            color: white;
        }
        .sidebar .nav-link {
            color: rgba(255,255,255,0.8);
            padding: 10px 20px;
            margin: 5px 0;
            border-radius: 5px;
        }
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            color: white;
            background: rgba(255,255,255,0.1);
        }
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-icon {
            font-size: 2.5rem;
            color: #4361ee;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2 px-0 sidebar">
                <div class="p-4">
                    <h4 class="mb-4">AI Interview Coach</h4>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="dashboard.php">
                                <i class="bi bi-speedometer2"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <i class="bi bi-people"></i> Users
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <i class="bi bi-file-text"></i> Resumes
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <i class="bi bi-graph-up"></i> Analytics
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <i class="bi bi-gear"></i> Settings
                            </a>
                        </li>
                        <li class="nav-item mt-4">
                            <a class="nav-link" href="logout.php">
                                <i class="bi bi-box-arrow-right"></i> Logout
                            </a>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9 col-lg-10">
                <!-- Top Bar -->
                <nav class="navbar navbar-light bg-white border-bottom py-3">
                    <div class="container-fluid">
                        <h4 class="mb-0">Admin Dashboard</h4>
                        <div class="d-flex align-items-center">
                            <span class="me-3">Welcome, <?php echo htmlspecialchars($_SESSION['admin_username']); ?></span>
                        </div>
                    </div>
                </nav>

                <div class="p-4">
                    <!-- Statistics Cards -->
                    <div class="row">
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Total Users</h6>
                                        <h3><?php echo $stats['total_users']; ?></h3>
                                    </div>
                                    <i class="bi bi-people-fill stat-icon"></i>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Resumes Analyzed</h6>
                                        <h3><?php echo $stats['total_resumes']; ?></h3>
                                    </div>
                                    <i class="bi bi-file-earmark-text-fill stat-icon"></i>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Tests Taken</h6>
                                        <h3><?php echo $stats['total_tests']; ?></h3>
                                    </div>
                                    <i class="bi bi-clipboard-check-fill stat-icon"></i>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Avg. Score</h6>
                                        <h3>72.5</h3>
                                    </div>
                                    <i class="bi bi-graph-up-arrow stat-icon"></i>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Recent Users -->
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header bg-primary text-white">
                                    <h5 class="mb-0">Recent Users</h5>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-hover">
                                            <thead>
                                                <tr>
                                                    <th>Username</th>
                                                    <th>Email</th>
                                                    <th>Joined</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($recent_users as $user): ?>
                                                <tr>
                                                    <td><?php echo htmlspecialchars($user['username']); ?></td>
                                                    <td><?php echo htmlspecialchars($user['email']); ?></td>
                                                    <td><?php echo date('M d, Y', strtotime($user['created_at'])); ?></td>
                                                </tr>
                                                <?php endforeach; ?>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Recent Tests -->
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header bg-primary text-white">
                                    <h5 class="mb-0">Recent Tests</h5>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-hover">
                                            <thead>
                                                <tr>
                                                    <th>User</th>
                                                    <th>Test Type</th>
                                                    <th>Score</th>
                                                    <th>Date</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($recent_tests as $test): ?>
                                                <tr>
                                                    <td><?php echo htmlspecialchars($test['username']); ?></td>
                                                    <td>
                                                        <span class="badge bg-<?php 
                                                            echo $test['test_type'] === 'text' ? 'info' : 
                                                                ($test['test_type'] === 'voice' ? 'warning' : 'success'); 
                                                        ?>">
                                                            <?php echo ucfirst($test['test_type']); ?>
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-<?php 
                                                            echo $test['score'] >= 70 ? 'success' : 
                                                                ($test['score'] >= 50 ? 'warning' : 'danger'); 
                                                        ?>">
                                                            <?php echo round($test['score'], 1); ?>
                                                        </span>
                                                    </td>
                                                    <td><?php echo date('M d', strtotime($test['created_at'])); ?></td>
                                                </tr>
                                                <?php endforeach; ?>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>