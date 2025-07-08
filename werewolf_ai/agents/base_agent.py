from typing import List, Optional
from memory.memory import AgentMemory

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.memory = AgentMemory()
        self.status = "alive"

    def talk(self, context: dict) -> str:
        raise NotImplementedError

    def vote(self, players_alive: List[str]) -> str:
        raise NotImplementedError

    def night_action(self, players_alive: List[str]) -> Optional[str]:
        return None

    def receive_info(self, info: str):
        pass
