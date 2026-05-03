AI Code Mentor — Streamlit app for prompt-driven code reviews using Groq.

Quick start

- Create and activate a venv:

```powershell
python -m venv venv
& venv\Scripts\Activate.ps1
```

- Install deps:

```bash
pip install -r requirements.txt
```

- Add API key in `.env`:

```
GROQ_API_KEY=your_api_key_here
```

Run

```bash
streamlit run app.py
```

Or run the CLI reviewer:

```bash
python main.py
```

Requires Python 3.8+. See `requirements.txt`.


```
ai-code
├─ app.py
├─ github_utils.py
├─ main.py
├─ prompts.py
├─ README.md
├─ requirements.txt
├─ reviewer.py
└─ test.py

```
```
ai-code
├─ app.py
├─ github_utils.py
├─ main.py
├─ prompts.py
├─ README.md
├─ requirements.txt
├─ reviewer.py
└─ test.py

```