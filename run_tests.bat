@echo off

set tests_folder="tests"

@echo Running unit tests...
@echo.

python -m unittest discover --verbose --start-directory %tests_folder% --pattern "*.py"

pause
