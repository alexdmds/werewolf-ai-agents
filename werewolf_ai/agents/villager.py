from .base_agent import BaseAgent

class Villager(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name, "Villager")

    def talk(self, context):
        return "Je suis un simple villageois."

    def vote(self, players_alive):
        # Vote aléatoire pour l'exemple minimal
        return players_alive[0] if players_alive else None
