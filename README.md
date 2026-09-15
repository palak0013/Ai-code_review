# AI Code Review Assistant

An AI-powered code review application built with **Python** and **Streamlit** that analyzes uploaded source files, pasted code, and GitHub repositories. The application provides intelligent feedback on code quality, identifies potential issues, suggests improvements, and explains recommended changes to help developers write cleaner and more maintainable code.


## Live Demo

**Application:** [AI Code Review Assistant](https://ai-code-review-2gsp.onrender.com)

---

## Features

- Analyze source code by uploading files
- Review public GitHub repositories
- Paste code directly using the built-in editor
- Supports Beginner and Production review modes
- Detects common coding issues and best practice violations
- Generates improved code suggestions with explanations
- Syntax-highlighted code display
- Supports multiple programming languages

### Supported Languages

- Python
- Java
- JavaScript
- C
- C++

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Frontend | Streamlit |
| Backend | Python |
| AI Model | Groq LLM |
| Version Control | Git & GitHub |

---

## Project Structure

```text
AI-CODE/
│
├── app.py
├── reviewer.py
├── github_utils.py
├── prompts.py
├── requirements.txt
├── README.md
└── .env
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/palak0013/Ai-code_review.git
cd your-repository
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_api_key
```

---

## Run the Application

```bash
streamlit run app.py
```

---

## Usage
The application provides three ways to review code.

### Upload File

1. Select **Upload File**
2. Upload a supported source file
3. Click **Analyze File**

### GitHub Repository

1. Select **GitHub Repo**
2. Enter a public GitHub repository URL
3. Click **Load Repo Files**
4. Select the files to analyze
5. Click **Analyze Repo**

### Code Editor

1. Enable **Use Code Editor**
2. Paste your source code
3. Click **Review Code**

---

## Sample Review

The application analyzes code and provides:

- Detected issues
- Suggested improvements
- Improved implementation
- Explanation of recommendations

---
