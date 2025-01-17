@echo off
:: Define directories
set SOURCE_DIR=C:\Users\Ayan\Pictures\up\upscayl_png_digital-art-4x_3x
set DEST_DIR=C:\Users\Ayan\Documents\GitHub\wallpapers\wallpapers

:: Notify start of copy process
echo [INFO] Copying files from %SOURCE_DIR% to %DEST_DIR% (Replacing existing files)...
xcopy "%SOURCE_DIR%\*" "%DEST_DIR%\" /E /H /C /I /Y
if %errorlevel% equ 0 (
    echo [SUCCESS] Files copied successfully.
) else (
    echo [ERROR] Failed to copy files.
    pause
    exit /b 1
)

:: Notify and run image optimization script
echo [INFO] Running image optimization script...
python "C:\Users\Ayan\Documents\GitHub\wallpapers\image.opt.py"
if %errorlevel% equ 0 (
    echo [SUCCESS] Image optimization completed.
) else (
    echo [ERROR] Image optimization script failed.
    pause
    exit /b 1
)

:: Notify and run analyser script
echo [INFO] Running analysis script...
python "C:\Users\Ayan\Documents\GitHub\wallpapers\analyser.py"
if %errorlevel% equ 0 (
    echo [SUCCESS] Analysis completed.
) else (
    echo [ERROR] Analysis script failed.
    pause
    exit /b 1
)

:: Notify completion
echo [INFO] All tasks completed successfully!
pause
