from .base_agent import BaseAgent

class Villager(BaseAgent):
    def __init__(self, name: str, llm=None, agent_id=None):
        super().__init__(name, "Villager", llm=llm, agent_id=agent_id)

    def talk(self, game_state):
        return super().talk(game_state)

    def vote(self, game_state):
        return super().vote(game_state)

    # Un villageois n'a pas d'action de nuit
