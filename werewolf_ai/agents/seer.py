from .base_agent import BaseAgent

class Seer(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name, "Seer")

    def talk(self, context):
        return "Je ressens des choses étranges cette nuit..."

    def vote(self, players_alive):
        return players_alive[0] if players_alive else None

    def night_action(self, players_alive):
        # Visionne le premier joueur vivant qui n'est pas elle-même
        for p in players_alive:
            if p != self.name:
                return p
        return None

    def receive_info(self, info: str):
        self.memory.add(f"Vision: {info}")
