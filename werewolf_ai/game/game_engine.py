from typing import List

class WerewolfGame:
    def __init__(self, agents: List):
        self.agents = agents
        self.turn = 0
        self.log = []
        self.game_over = False

    def play(self, max_turns=100):
        print("=== Début de la partie ===")
        print("Joueurs en jeu :", ", ".join([a.name + f" ({a.role})" for a in self.agents]))
        self.turn = 0
        while not self.is_game_over() and self.turn < max_turns:
            self.turn += 1
            print(f"\n===== Tour {self.turn} =====")
            self.night_phase()
            self.day_phase()
            self.check_win_condition()
        if self.turn >= max_turns:
            print(f"\n=== Fin de la partie : nombre maximal de tours ({max_turns}) atteint ===")
        else:
            print("=== Fin de la partie ===")

    def night_phase(self):
        print("\n--- Phase de nuit ---")
        # 1. Voyante agit en premier
        seer = next((a for a in self.agents if a.role == "Seer" and a.status == "alive"), None)
        if seer:
            cible_id = seer.spy(self)
            cible = next((a for a in self.agents if a.agent_id == cible_id), None) if cible_id else None
            print(f"Voyante ({seer.name}) agit : {cible.name if cible else 'aucune cible'}")
        # 2. Loups votent individuellement
        wolves = [a for a in self.agents if a.role == "Werewolf" and a.status == "alive"]
        wolf_votes = {}
        for wolf in wolves:
            cible_id = wolf.vote_to_kill(self)
            wolf_votes[wolf.agent_id] = cible_id
            cible = next((a for a in self.agents if a.agent_id == cible_id), None) if cible_id else None
            print(f"Loup {wolf.name} a voté : {cible.name if cible else 'aucune cible'}")
        # 3. On informe chaque loup du vote de chaque loup
        for wolf in wolves:
            votes_info = ", ".join([f"{w.name} → {wolf_votes[w.agent_id]}" for w in wolves])
            wolf.memory.add(f"Votes des loups cette nuit : {votes_info}")
        # 4. Calcul de la majorité
        vote_targets = [cible_id for cible_id in wolf_votes.values() if cible_id]
        if vote_targets:
            from collections import Counter
            count = Counter(vote_targets)
            cible_majoritaire, nb = count.most_common(1)[0]
            if nb > len(wolves)//2:
                # Trouve l'agent cible
                cible_agent = next((a for a in self.agents if a.agent_id == cible_majoritaire and a.status == "alive"), None)
                if cible_agent:
                    cible_agent.status = "dead"
                    self.night_victim = cible_agent
                    print(f">>> Victime de la nuit : {cible_agent.name} <<<")
                else:
                    self.night_victim = None
            else:
                self.night_victim = None
                print(">>> Pas de majorité, personne n'est éliminé cette nuit. <<<")
        else:
            self.night_victim = None
            print(">>> Aucun vote de loup valide cette nuit. <<<")

    def day_phase(self):
        print("\n--- Phase de jour ---")
        # 1. Annonce de la victime de la nuit
        if hasattr(self, 'night_victim') and self.night_victim:
            print(f"Le village découvre au matin que {self.night_victim.name} a été tué pendant la nuit !")
        else:
            print("Le village découvre au matin qu'il n'y a pas eu de victime cette nuit.")
        # 2. Chaque agent vivant prend la parole
        for agent in self.agents:
            if hasattr(agent, "talk") and agent.status == "alive":
                msg = agent.talk(self)
                print(f"{agent.name} dit : {msg}")
        # 3. Chaque agent vivant vote publiquement
        votes = {}
        alive = [a for a in self.agents if a.status == "alive"]
        alive_ids = [a.agent_id for a in alive]
        for agent in alive:
            vote = agent.vote(self)
            # On attend un ID d'agent
            if vote and vote in alive_ids:
                votes.setdefault(vote, 0)
                votes[vote] += 1
                cible = next((a for a in alive if a.agent_id == vote), None)
                print(f"{agent.name} vote contre {cible.name if cible else vote}")
            else:
                print(f"{agent.name} n'a pas voté pour un joueur vivant (vote ignoré)")
        # 4. Élimination par majorité
        if votes:
            from collections import Counter
            count = Counter(votes)
            cible_majoritaire, nb = count.most_common(1)[0]
            # Vérifie s'il y a égalité
            if list(count.values()).count(nb) == 1:
                cible_agent = next((a for a in alive if a.agent_id == cible_majoritaire), None)
                if cible_agent:
                    cible_agent.status = "dead"
                    print(f"{cible_agent.name} est éliminé par le village !")
            else:
                print("Égalité au vote, personne n'est éliminé.")
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
