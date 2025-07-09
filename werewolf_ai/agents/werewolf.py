from .base_agent import BaseAgent
from typing import List

class Werewolf(BaseAgent):
    def __init__(self, name: str, allies: list = None, agent_id=None):
        super().__init__(name, "Werewolf", agent_id=agent_id)
        self.allies = allies or []

    def talk(self, game_state):
        return super().talk(game_state)

    def vote(self, game_state):
        return super().vote(game_state)

    def night_action(self, game_state):
        return super().night_action(game_state)
