@echo off
set root=C:\xampp\htdocs\ai-interview-coach

call :checkdir  %root%\frontend
call :checkfile %root%\frontend\index.html
call :checkfile %root%\frontend\login.html
call :checkfile %root%\frontend\register.html
call :checkfile %root%\frontend\dashboard.html
call :checkfile %root%\frontend\upload_resume.html
call :checkfile %root%\frontend\text_test.html
call :checkfile %root%\frontend\voice_test.html
call :checkfile %root%\frontend\video_test.html
call :checkfile %root%\frontend\results.html
call :checkdir  %root%\frontend\css
call :checkfile %root%\frontend\css\style.css
call :checkdir  %root%\frontend\js
call :checkfile %root%\frontend\js\main.js
call :checkdir  %root%\frontend\assets

call :checkdir %root%\backend-php
call :checkdir %root%\backend-php\config
call :checkfile %root%\backend-php\config\db.php
call :checkdir %root%\backend-php\api
call :checkfile %root%\backend-php\api\auth.php
call :checkfile %root%\backend-php\api\resume.php
call :checkfile %root%\backend-php\api\text_test.php
call :checkfile %root%\backend-php\api\voice_test.php
call :checkfile %root%\backend-php\api\video_test.php
call :checkfile %root%\backend-php\api\final_score.php
call :checkdir %root%\backend-php\uploads
call :checkdir %root%\backend-php\uploads\resumes
call :checkdir %root%\backend-php\uploads\audio
call :checkdir %root%\backend-php\uploads\video
call :checkdir %root%\backend-php\admin
call :checkfile %root%\backend-php\admin\login.php
call :checkfile %root%\backend-php\admin\dashboard.php

call :checkdir %root%\backend-python
call :checkfile %root%\backend-python\resume_ai.py
call :checkfile %root%\backend-python\text_ai.py
call :checkfile %root%\backend-python\voice_ai.py
call :checkfile %root%\backend-python\video_ai.py
call :checkdir %root%\backend-python\ml-models
call :checkdir %root%\backend-python\output

echo.
echo Verification complete.
pause
exit /b

:checkdir
if exist %~1\ (
  echo [OK]   DIR  %~1
) else (
  echo [MISSING] DIR  %~1
)
exit /b

:checkfile
if exist %~1 (
  echo [OK]   FILE %~1
) else (
  echo [MISSING] FILE %~1
)
exit /b
