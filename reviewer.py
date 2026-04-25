from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_prompt(language, mode):

    if mode == "Beginner":
        return f"""
You are a beginner-friendly coding mentor.

Language: {language}

Rules:
- Keep code simple
- Add comments
- Use basic syntax
- Do NOT over-engineer

OUTPUT FORMAT:

ISSUES:
- List problems

IMPROVED CODE:
```{language.lower()}


EXPLANATION:
- Explain in simple English
"""

    elif mode == "Production":
        return f"""
You are an expert developer.

Language: {language}

Rules:
- Write clean and optimized code
- Keep it professional

OUTPUT FORMAT:

ISSUES:
- Problems

IMPROVED CODE:
```{language.lower()}

EXPLANATION:
- Brief explanation
"""

    return ""

def review_code(code, language, mode):

    system_prompt = get_prompt(language, mode)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Review this {language} code:\n\n{code}"
                }
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"