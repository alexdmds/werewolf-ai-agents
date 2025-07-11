from config import use_mock_llm
import os
from langchain_openai import ChatOpenAI

# S'assurer que la clé OpenAI attendue par langchain_openai est bien présente
def ensure_openai_key():
    if "OPENAI_WEREWOLF_KEY" in os.environ:
        os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_WEREWOLF_KEY"]


def call_llm(prompt: str) -> str:
    # Version factice pour la structure minimale
    return "Réponse LLM simulée."

class MockLLM:
    def __call__(self, prompt: str) -> str:
        return call_llm(prompt)

class RealLLM:
    def __init__(self):
        ensure_openai_key()
        self.model = "gpt-4o-mini"
        self.llm = ChatOpenAI(model=self.model)

    def __call__(self, prompt: str) -> str:
        try:
            # On fournit le prompt comme message utilisateur, le prompt système est déjà inclus dans build_prompt
            response = self.llm.invoke(prompt)
            # ChatOpenAI renvoie un Message, on extrait le contenu
            return response.content.strip() if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"[ERREUR LLM] {e}"

def get_llm():
    if use_mock_llm():
        return MockLLM()
    else:
        return RealLLM()
