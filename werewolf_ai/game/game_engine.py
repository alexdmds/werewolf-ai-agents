from typing import List

class WerewolfGame:
    def __init__(self, agents: List):
        self.agents = agents
        self.turn = 0
        self.log = []
        self.game_over = False

    def play(self):
        print("=== Début de la partie ===")
        print("Joueurs en jeu :", ", ".join([a.name + f" ({a.role})" for a in self.agents]))
        while not self.is_game_over():
            self.turn += 1
            print(f"\n===== Tour {self.turn} =====")
            self.run_night_phase()
            self.run_day_phase()
            self.check_win_condition()
        print("=== Fin de la partie ===")

    def run_night_phase(self):
        print("\n--- Phase de nuit ---")
        for agent in self.agents:
            if hasattr(agent, "night_action") and agent.status == "alive":
                action = agent.night_action([a.name for a in self.agents if a.status == "alive"])
                if action:
                    print(f"{agent.name} ({agent.role}) agit la nuit : {action}")

    def run_day_phase(self):
        print("\n--- Phase de jour ---")
        for agent in self.agents:
            if hasattr(agent, "talk") and agent.status == "alive":
                msg = agent.talk({})
                print(f"{agent.name} dit : {msg}")
        self.resolve_votes()

    def resolve_votes(self):
        print("\nRésolution des votes (exemple minimal)")
        votes = {}
        alive = [a for a in self.agents if a.status == "alive"]
        for agent in alive:
            vote = agent.vote([a.name for a in alive if a.name != agent.name])
            if vote:
                votes.setdefault(vote, 0)
                votes[vote] += 1
                print(f"{agent.name} vote contre {vote}")
        if votes:
            eliminated = max(votes, key=votes.get)
            for agent in alive:
                if agent.name == eliminated:
                    agent.status = "dead"
                    print(f"{eliminated} est éliminé !")
                    break
        else:
            print("Aucun vote exprimé.")

    def check_win_condition(self):
        print("\nVérification de la condition de victoire (exemple minimal)")
        # Affiche le statut des joueurs
        for agent in self.agents:
            print(f"{agent.name} : {agent.status}")
        # Condition de victoire minimale :
        wolves = [a for a in self.agents if a.role == "Werewolf" and a.status == "alive"]
        villagers = [a for a in self.agents if a.role != "Werewolf" and a.status == "alive"]
        if not wolves:
            print("\nVictoire des villageois !")
            self.game_over = True
        elif len(wolves) >= len(villagers):
            print("\nVictoire des loups-garous !")
            self.game_over = True

    def is_game_over(self):
        return getattr(self, "game_over", False)

    def get_alive_names(self):
        return [a.name for a in self.agents if a.status == "alive"]

    def get_deaths_summary(self):
        morts = [a for a in self.agents if a.status == "dead"]
        res = []
        for a in morts:
            # On suppose que la cause et le rôle ne sont pas encore stockés, on met un placeholder
            res.append(f"{a.name} (mort, rôle: {a.role})")
        return res

    def get_last_discussion(self, n=3):
        # On suppose que self.log contient les messages publics (à adapter si besoin)
        return self.log[-n:] if len(self.log) >= n else self.log
