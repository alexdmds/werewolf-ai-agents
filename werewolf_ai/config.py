# Configuration globale du projet Loup-Garou IA

# Si True, on utilise un LLM mocké (réponse simulée)
# Si False, on utilise un vrai appel API (ex: OpenAI, Mistral...)
USE_MOCK_LLM = True

def use_mock_llm():
    """Retourne True si on doit utiliser le mock LLM, False sinon."""
    return USE_MOCK_LLM
