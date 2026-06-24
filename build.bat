@echo off
echo Building RACI-VS desktop app...
echo.

pyinstaller ^
  --name "RACI-VS" ^
  --noconsole ^
  --onedir ^
  --add-data "static;static" ^
  --add-data "templates;templates" ^
  --add-data "examples;examples" ^
  launcher.py

echo.
if %ERRORLEVEL% == 0 (
    echo Build successful.
    echo Output: dist\RACI-VS\RACI-VS.exe
    echo.
    echo To create the Setup.msi installer, push a v*.*.* tag to trigger the GitHub Actions workflow.
) else (
    echo Build failed. Check the output above for errors.
)
echo.
