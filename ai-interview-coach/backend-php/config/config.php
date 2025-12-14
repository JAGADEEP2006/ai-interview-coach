<?php
// Application Configuration
define('APP_NAME', 'AI Interview Coach');
define('APP_VERSION', '1.0.0');
define('APP_URL', 'http://localhost/ai-interview-coach');

// File Upload Settings
define('MAX_UPLOAD_SIZE', 5242880); // 5MB
define('ALLOWED_RESUME_TYPES', ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']);
define('ALLOWED_AUDIO_TYPES', ['audio/wav', 'audio/mpeg', 'audio/mp3']);
define('ALLOWED_VIDEO_TYPES', ['video/mp4', 'video/webm']);

// AI Settings
define('PYTHON_PATH', 'python');
define('RESUME_AI_SCRIPT', __DIR__ . '/../../backend-python/resume_ai.py');
define('TEXT_AI_SCRIPT', __DIR__ . '/../../backend-python/text_ai.py');
define('VOICE_AI_SCRIPT', __DIR__ . '/../../backend-python/voice_ai.py');
define('VIDEO_AI_SCRIPT', __DIR__ . '/../../backend-python/video_ai.py');

// Test Settings
define('TEXT_TEST_DURATION', 1800); // 30 minutes in seconds
define('VOICE_TEST_DURATION', 300); // 5 minutes in seconds
define('VIDEO_TEST_DURATION', 300); // 5 minutes in seconds
define('QUESTIONS_PER_TEST', 5);
?>