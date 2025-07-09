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

    def build_prompt(self, action, game_state):
        from prompts.prompt_utils import build_prompt
        return build_prompt(self, action, game_state)

    def talk(self, game_state) -> str:
        prompt = self.build_prompt("talk", game_state)
        return self.llm(prompt)

    def vote(self, game_state) -> str:
        prompt = self.build_prompt("vote", game_state)
        return self.llm(prompt)

    def night_action(self, game_state) -> Optional[str]:
        prompt = self.build_prompt("night_action", game_state)
        return self.llm(prompt)

    def receive_info(self, info: str):
        pass
