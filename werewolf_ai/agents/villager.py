from .base_agent import BaseAgent

class Villager(BaseAgent):
    def __init__(self, name: str, llm=None, agent_id=None):
        super().__init__(name, "Villager", llm=llm, agent_id=agent_id)

    def talk(self, game_state):
        return super().talk(game_state)

    def vote(self, game_state):
        prompt = self.build_prompt("vote", game_state)
        response = self.llm(prompt)
        import re
        match = re.search(r"([0-9a-fA-F]{6})", response)
        if match:
            return match.group(1)
        for ag in game_state.agents:
            if ag.status == "alive" and ag.name.lower() in response.lower():
                return ag.agent_id
        return None

    # Un villageois n'a pas d'action de nuit
