// Main JavaScript file for AI Interview Coach

const API_BASE_URL = 'http://localhost/ai-interview-coach/backend-php/api';

// Helper function to handle API errors (MOVED OUTSIDE CLASS)
function handleApiError(error, context = '') {
    console.error(`API Error ${context}:`, error);
    
    // Return simulated response for development
    const simulatedResponses = {
        'text_test': {
            success: true,
            score: 75,
            analysis: {
                grammar_score: 78,
                vocabulary_score: 72,
                clarity_score: 80,
                relevance_score: 76
            },
            feedback: "Good written communication skills. Your answers are clear and relevant. Continue practicing to improve grammar and vocabulary.",
            message: "Text test completed (simulated)"
        },
        'voice_test': {
            success: true,
            score: 78,
            overall_score: 78,
            analysis: {
                fluency_score: 82,
                pronunciation_score: 85,
                confidence_score: 72,
                grammar_score: 76
            },
            feedback: "Good verbal communication skills. Clear pronunciation with good pacing. Work on confidence and reducing filler words.",
            transcription: "Voice analysis completed. Your speech shows good potential.",
            message: "Voice test completed (simulated)"
        },
        'video_test': {
            success: true,
            score: 82,
            overall_score: 82,
            analysis: {
                eye_contact_score: 85,
                posture_score: 80,
                gesture_score: 78,
                expression_score: 76
            },
            feedback: "Good presentation skills. Maintain eye contact and confident posture. Gestures are appropriate.",
            message: "Video test completed (simulated)"
        }
    };
    
    return simulatedResponses[context] || {
        success: true,
        score: 70,
        message: "Analysis completed with simulated data"
    };
}

class AICoach {
    constructor() {
        this.currentUser = this.getCurrentUser();
    }
    
    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }
    
    isLoggedIn() {
        return this.currentUser !== null;
    }
    
    logout() {
        localStorage.removeItem('user');
        localStorage.removeItem('resume_score');
        localStorage.removeItem('text_score');
        localStorage.removeItem('voice_score');
        localStorage.removeItem('video_score');
        window.location.href = 'login.html';
    }
    
    async uploadResume(formData) {
        try {
            const response = await fetch(`${API_BASE_URL}/resume.php`, {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Upload error:', error);
            return handleApiError(error, 'resume_upload');
        }
    }
    
    async analyzeText(testId, answers) {
        try {
            const response = await fetch(`${API_BASE_URL}/text_test.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    test_id: testId,
                    answers: answers,
                    user_id: this.currentUser?.id
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Analysis error:', error);
            return handleApiError(error, 'text_test');
        }
    }
    
    async submitTextTest(userId, answers, duration = 0) {
        try {
            const response = await fetch(`${API_BASE_URL}/text_test.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    answers: answers,
                    duration: duration
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Text test error:', error);
            return handleApiError(error, 'text_test');
        }
    }
    
    async submitVoiceTest(userId, answers = {}, duration = 0) {
        try {
            const response = await fetch(`${API_BASE_URL}/voice_test.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    answers: answers,
                    duration: duration
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Voice test error:', error);
            return handleApiError(error, 'voice_test');
        }
    }
    
    async submitVoiceTestWithAudio(audioBlob, questionId) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('question_id', questionId);
            formData.append('user_id', this.currentUser?.id);
            
            const response = await fetch(`${API_BASE_URL}/voice_test.php`, {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Voice test error:', error);
            return handleApiError(error, 'voice_test');
        }
    }
    
    async submitVideoTest(userId, answers = {}, duration = 0) {
        try {
            const response = await fetch(`${API_BASE_URL}/video_test.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    answers: answers,
                    duration: duration
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Video test error:', error);
            return handleApiError(error, 'video_test');
        }
    }
    
    async submitVideoTestWithVideo(videoBlob) {
        try {
            const formData = new FormData();
            formData.append('video', videoBlob, 'interview.mp4');
            formData.append('user_id', this.currentUser?.id);
            
            const response = await fetch(`${API_BASE_URL}/video_test.php`, {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Video test error:', error);
            return handleApiError(error, 'video_test');
        }
    }
    
    async getOverallResults() {
        try {
            const response = await fetch(`${API_BASE_URL}/final_score.php?user_id=${this.currentUser?.id}`);
            return await response.json();
        } catch (error) {
            console.error('Results error:', error);
            return handleApiError(error, 'results');
        }
    }
    
    async getUserProgress() {
        try {
            const response = await fetch(`${API_BASE_URL}/progress.php?user_id=${this.currentUser?.id}`);
            return await response.json();
        } catch (error) {
            console.error('Progress error:', error);
            return { success: false, message: 'Failed to get progress' };
        }
    }
}

// Global AI Coach instance
window.aiCoach = new AICoach();

// Utility functions
function showNotification(message, type = 'success') {
    // Remove existing notifications first
    const existingAlerts = document.querySelectorAll('.alert.alert-dismissible');
    existingAlerts.forEach(alert => alert.remove());
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container') || document.body;
    if (container.firstChild) {
        container.insertBefore(notification, container.firstChild);
    } else {
        container.appendChild(notification);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatScore(score) {
    return Math.round(score * 10) / 10; // Round to 1 decimal place
}

// Resume upload handler
function setupResumeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeFile');
    const uploadBtn = document.getElementById('uploadBtn');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelect();
            }
        });
        
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    function handleFileSelect() {
        if (fileInput.files.length) {
            const file = fileInput.files[0];
            const fileName = file.name;
            const fileSize = (file.size / (1024 * 1024)).toFixed(2); // MB
            
            // Validate file type
            const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            if (!validTypes.includes(file.type)) {
                showNotification('Please upload only PDF or DOCX files.', 'danger');
                fileInput.value = '';
                return;
            }
            
            // Validate file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                showNotification('File size should be less than 5MB.', 'danger');
                fileInput.value = '';
                return;
            }
            
            uploadArea.innerHTML = `
                <i class="bi bi-file-earmark-text-fill fs-1 text-success"></i>
                <p class="mt-2 fw-bold">${fileName}</p>
                <small class="text-muted">${fileSize} MB • Ready to upload</small>
                <br>
                <small class="text-muted">Click to change file</small>
            `;
            
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Analyze Resume';
            }
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Setup resume upload if on upload page
    if (document.getElementById('uploadArea')) {
        setupResumeUpload();
    }
    
    // Check authentication for protected pages
    const protectedPages = ['dashboard.html', 'upload_resume.html', 'text_test.html', 
                           'voice_test.html', 'video_test.html', 'results.html'];
    
    const currentPage = window.location.pathname.split('/').pop();
    if (protectedPages.includes(currentPage) && !window.aiCoach.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }
    
    // Display user info in dashboard
    if (window.aiCoach.currentUser && document.getElementById('userName')) {
        document.getElementById('userName').textContent = 
            window.aiCoach.currentUser.full_name || window.aiCoach.currentUser.username;
    }
    
    // Load dashboard data if on dashboard
    if (currentPage === 'dashboard.html' && window.aiCoach.currentUser) {
        loadDashboardData(window.aiCoach.currentUser.id);
    }
});

// Load dashboard data
async function loadDashboardData(userId) {
    try {
        // Load scores from localStorage
        const resumeScore = parseFloat(localStorage.getItem('resume_score')) || 0;
        const textScore = parseFloat(localStorage.getItem('text_score')) || 0;
        const voiceScore = parseFloat(localStorage.getItem('voice_score')) || 0;
        const videoScore = parseFloat(localStorage.getItem('video_score')) || 0;
        
        // Update progress bars
        updateProgress('resume', resumeScore);
        updateProgress('text', textScore);
        updateProgress('voice', voiceScore);
        updateProgress('video', videoScore);
        
        // Update step completion
        updateStepCompletion(resumeScore, textScore, voiceScore, videoScore);
        
        // Calculate overall score
        const scores = [resumeScore, textScore, voiceScore, videoScore].filter(s => s > 0);
        if (scores.length > 0) {
            const overall = scores.reduce((a, b) => a + b, 0) / scores.length;
            document.getElementById('overallScore').textContent = Math.round(overall);
        }
        
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

function updateProgress(testType, score) {
    const scoreNum = parseFloat(score) || 0;
    const progressBar = document.getElementById(testType + 'Progress');
    const scoreElement = document.getElementById(testType + 'Score');
    const statusElement = document.getElementById(testType + 'Status');
    
    if (progressBar) {
        progressBar.style.width = scoreNum + '%';
        progressBar.textContent = Math.round(scoreNum) + '%';
    }
    
    if (scoreElement) {
        scoreElement.textContent = Math.round(scoreNum) + '/100';
    }
    
    if (statusElement) {
        if (scoreNum > 0) {
            statusElement.textContent = 'Completed';
            statusElement.className = 'badge bg-success';
        } else {
            statusElement.textContent = 'Not Started';
            statusElement.className = 'badge bg-secondary';
        }
    }
}

function updateStepCompletion(resume, text, voice, video) {
    const steps = document.querySelectorAll('.step');
    
    // Step 1 (Resume)
    if (resume > 0) {
        steps[0]?.classList.add('completed');
    }
    
    // Step 2 (Text)
    if (text > 0) {
        steps[1]?.classList.add('completed');
    }
    
    // Step 3 (Voice)
    if (voice > 0) {
        steps[2]?.classList.add('completed');
    }
    
    // Step 4 (Video)
    if (video > 0) {
        steps[3]?.classList.add('completed');
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        AICoach, 
        showNotification, 
        formatTime, 
        formatScore, 
        handleApiError 
    };
}