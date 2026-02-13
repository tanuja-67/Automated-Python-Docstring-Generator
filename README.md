# Python Docstring Generator

An AI-powered Streamlit application that automatically generates Python docstrings using Large Language Models (LLMs) with a human-in-the-loop approval workflow.


## Overview

This project helps developers improve Python code documentation by:

* Parsing Python files using the `ast` module
* Generating docstrings using AI (Google Gemini / OpenAI)
* Validating docstrings against PEP 257 standards
* Allowing users to review, edit, accept, or reject generated docstrings
* Inserting approved docstrings into original source code
* Exporting consolidated documentation


## Features

* AI-based docstring generation
* Support for Google, NumPy, and reST docstring styles
* Documentation coverage analysis
* Human-in-the-loop approval workflow
* Safe AST-based code modification (no code execution)
* Multi-file upload support
* Export options: Markdown, Text, and Python format

## Project Structure

.
├── app.py
├── requirements.txt
├── services/
│   ├── ast_parser.py
│   ├── docstring_generator.py
│   ├── validator.py
│   ├── coverage.py
│   ├── api_manager.py
│   ├── code_inserter.py
│   └── exporter.py
└── utils/
    └── file_utils.py

## Installation

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file:

env
GOOGLE_API_KEY_1=your_key
GOOGLE_API_KEY_2=your_backup_key
OPENAI_API_KEY=your_openai_key


### 3. Run the application

```bash
streamlit run app.py
```

Open in your browser:
http://localhost:8501

## Workflow

1. Upload Python file(s) or paste code
2. View documentation coverage report
3. Generate docstrings using AI
4. Review and validate generated docstrings
5. Accept, edit, or reject each docstring
6. Download updated code and consolidated documentation


## Security

* Uses static AST parsing (no execution of uploaded code)
* API keys stored securely in environment variables
* Automatic fallback between AI providers


## Technology Stack

* Python
* Streamlit
* Python AST module
* Google Gemini API
* OpenAI API


## License

MIT License

