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

    def talk(self, game_state) -> str:
        prompt = self.build_prompt("talk", game_state)
        return self.llm(prompt)

    def vote(self, game_state) -> str:
        prompt = self.build_prompt("vote", game_state)
        return self.llm(prompt)

    def receive_info(self, info: str):
        pass
