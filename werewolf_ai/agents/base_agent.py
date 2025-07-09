from typing import List, Optional
from memory.memory import AgentMemory
from llm.llm_interface import get_llm

class BaseAgent:
    def __init__(self, name: str, role: str, llm=None):
        self.name = name
        self.role = role
        self.memory = AgentMemory()
        self.status = "alive"
        self.llm = llm if llm is not None else get_llm()

    def talk(self, context: dict) -> str:
        raise NotImplementedError

    def vote(self, players_alive: List[str]) -> str:
        raise NotImplementedError

    def night_action(self, players_alive: List[str]) -> Optional[str]:
        return None

    def receive_info(self, info: str):
        pass
