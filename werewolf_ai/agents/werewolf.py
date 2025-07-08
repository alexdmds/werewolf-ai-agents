from .base_agent import BaseAgent
from typing import List

class Werewolf(BaseAgent):
    def __init__(self, name: str, allies: List[str] = None):
        super().__init__(name, "Werewolf")
        self.allies = allies or []

    def talk(self, context):
        return "Je ne suis pas un loup-garou, faites-moi confiance !"

    def vote(self, players_alive):
        return players_alive[0] if players_alive else None

    def night_action(self, players_alive):
        # Choisit la première cible vivante qui n'est pas un loup
        for p in players_alive:
            if p not in self.allies and p != self.name:
                return p
        return None
