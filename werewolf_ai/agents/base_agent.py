# Pour activer le suivi LangSmith, installez : pip install langsmith
import os
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "<VOTRE_CLE_API_LANGSMITH>")

from langsmith import traceable
from typing import List, Optional
from memory.memory import AgentMemory
from llm.llm_interface import get_llm
import random

class BaseAgent:
    def __init__(self, name: str, role: str, llm=None, agent_id=None):
        self.name = name
        self.role = role
        self.memory = AgentMemory()
        self.status = "alive"
        self.llm = llm if llm is not None else get_llm()
        if agent_id is None:
            self.agent_id = ''.join(random.choices('0123456789abcdef', k=6))
        else:
            self.agent_id = agent_id

    def __repr__(self):
        return f"<{self.role} {self.name} ({self.agent_id})>"

    def build_prompt(self, action, game_state):
        from prompts.prompt_utils import build_prompt
        return build_prompt(self, action, game_state)

    @traceable
    def talk(self, game_state) -> str:
        prompt = self.build_prompt("talk", game_state)
        return self.llm(prompt)

    @traceable
    def vote(self, game_state) -> str:
        prompt = self.build_prompt("vote", game_state)
        return self.llm(prompt)

    def receive_info(self, info: str):
        pass
