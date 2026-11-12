import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL = os.getenv("OLLAMA_MODEL")

SCHEMA = """
Table: students

Columns:
student_id, first_name, last_name, email,
register_number, age, religion, cgpa

Generate PostgreSQL SELECT queries only.
Use only the students table.
Never invent column names or values.
Return only SQL without markdown.
For highest CGPA, exclude NULL values and
order by cgpa DESC LIMIT 1.
For lowest CGPA, exclude NULL values and
order by cgpa ASC LIMIT 1.
"""


def generate_sql(question):
    match = re.search(
        r"([A-Za-z]+)(?:'s)?\s+registration\s+number",
        question,
        re.IGNORECASE
    )

    if match:
        first_name = match.group(1)

        return (
            "SELECT register_number FROM students "
            f"WHERE LOWER(first_name) = LOWER('{first_name}') "
            "AND register_number IS NOT NULL LIMIT 1;"
        )

    prompt = f"""
    You are a PostgreSQL Text-to-SQL agent.

    Database schema:
    {SCHEMA}

    User question:
    {question}

    Generate one valid SELECT query.
    Return only SQL.
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()

    sql = response.json()["message"]["content"]
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql
