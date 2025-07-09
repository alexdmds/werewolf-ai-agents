from .base_agent import BaseAgent

class Seer(BaseAgent):
    def __init__(self, name: str, agent_id=None):
        super().__init__(name, "Seer", agent_id=agent_id)

    def talk(self, game_state):
        return super().talk(game_state)

    def vote(self, game_state):
        return super().vote(game_state)

    def night_action(self, game_state):
        return super().night_action(game_state)

    def receive_info(self, info: str):
        self.memory.add(f"Vision: {info}")
