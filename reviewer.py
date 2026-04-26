from groq import Groq
import os
from dotenv import load_dotenv
from prompts import beginner_prompt, production_prompt, repo_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def review_code(code, language, mode):

    #system_prompt = get_prompt(language, mode)
    if mode == "Beginner":
       system_prompt = beginner_prompt(code, language)

    elif mode == "Production":
       system_prompt = production_prompt(code, language)

    else:
       system_prompt = beginner_prompt(code, language)

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