@echo off

:: Set the paths
set "NEW_LIBRARY_PATH=D:\Projects\AI\_Models"
set "A1111_MODELS_PATH=D:\Projects\AI\diSty\stable-diffusion-webui\models"
set "COMFY_MODELS_PATH=D:\Projects\AI\diSty\comfyui\models"

:: Remove existing folders (if they exist)
if exist "%A1111_MODELS_PATH%" rmdir "%A1111_MODELS_PATH%"
if exist "%COMFY_MODELS_PATH%" rmdir "%COMFY_MODELS_PATH%"

:: Create symlinks (requires administrator privileges)
mklink /D "%A1111_MODELS_PATH%" "%NEW_LIBRARY_PATH%"
mklink /D "%COMFY_MODELS_PATH%" "%NEW_LIBRARY_PATH%"

echo Symlinks created successfully.
pause