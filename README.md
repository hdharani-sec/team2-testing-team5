# ENPM611 Project Application - GitHub Issues Analysis (Poetry Project) - Milestone 3 - Group 2
This section documents the testing activities performed for Milestone 3 of the ENPM611 project.  
The goal of this milestone was to create a comprehensive suite of unit tests, identify bugs through white-box testing, and achieve at least 90% statement coverage. 

---
## Testing Overview
The testing effort focused on building robust unit tests for the following modules:
- `analyses.py`
- `config.py`
- `data_loader.py`
- `model.py`

The tests examine normal flows, edge cases, invalid inputs, plotting behavior, parsing logic, and configuration handling.  
Python’s `unittest` framework was used to implement the tests, and the `coverage` tool was used to measure statement coverage.

---
## Test Setup Instructions
### 1. Create and activate a virtual environment
Fork the repository and clone the fork to your local machine. In the root directory of the application, create a virtual environment, and activate that environment from the root of the project:
```bash
python -m venv .env
source .env/bin/activate        # (Mac/Linux)
.env\Scripts\activate           # (Windows)
```

### 2. Install dependencies
Install all required packages from requirements.txt:
``` pip install -r requirements.txt ```

### 3. Run all unit tests
Use the coverage tool to execute the full test suite:
``` python -m coverage run -m unittest discover ``` 

### 4. Generate the coverage report
After the tests finish running, generate a readable report:
``` python -m coverage report --omit="test_*" ```

---
## Output
- team_2_test_failures.txt
Full terminal output of the test run

- team_2_test_coverage.txt
Full terminal coverage output

- Pull Request link to the testing branch
