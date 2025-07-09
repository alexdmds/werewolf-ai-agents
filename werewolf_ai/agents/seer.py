from .base_agent import BaseAgent

class Seer(BaseAgent):
    def __init__(self, name: str, llm=None, agent_id=None):
        super().__init__(name, "Seer", llm=llm, agent_id=agent_id)

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

    def spy(self, game_state):
        prompt = self.build_prompt("spy", game_state)
        response = self.llm(prompt)
        import re
        match = re.search(r"([0-9a-fA-F]{6})", response)
        cible = None
        if match:
            agent_id = match.group(1)
            for ag in game_state.agents:
                if ag.agent_id == agent_id and ag.status == "alive":
                    cible = ag
                    break
        if not cible:
            for ag in game_state.agents:
                if ag.status == "alive" and ag.name.lower() in response.lower():
                    cible = ag
                    break
        if cible:
            self.memory.add(f"Vision : {cible.name} ({cible.agent_id}) est {cible.role}")
            return cible.agent_id
        return None
