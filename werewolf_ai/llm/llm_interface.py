from config import use_mock_llm
import os
from openai import OpenAI

def call_llm(prompt: str) -> str:
    # Version factice pour la structure minimale
    return "Réponse LLM simulée."

class MockLLM:
    def __call__(self, prompt: str) -> str:
        return call_llm(prompt)

class RealLLM:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_WEREWOLF_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"

    def __call__(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un agent du jeu Loup-Garou IA."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=256,
                temperature=0.7
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"[ERREUR LLM] {e}"

def get_llm():
    if use_mock_llm():
        return MockLLM()
    else:
        return RealLLM()
