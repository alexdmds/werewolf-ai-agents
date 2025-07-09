from typing import List
import os

class WerewolfGame:
    def __init__(self, agents: List):
        self.agents = agents
        self.turn = 0
        self.log = []
        self.game_over = False
        # Multi-niveaux d’historiques
        self.public_log = []
        self.wolf_log = []
        self.master_log = []
        self.agent_private_logs = {a.agent_id: [] for a in agents}

    def log_public(self, msg: str):
        self.public_log.append(msg)
        self.master_log.append(f"[PUBLIC] {msg}")
        self.append_to_file("logs/public_log.txt", msg)

    def log_wolf(self, msg: str):
        self.wolf_log.append(msg)
        self.master_log.append(f"[WOLF] {msg}")
        self.append_to_file("logs/wolf_log.txt", msg)

    def log_master(self, msg: str):
        self.master_log.append(f"[MASTER] {msg}")
        self.append_to_file("logs/master_log.txt", msg)

    def log_agent(self, agent_id: str, msg: str):
        if agent_id in self.agent_private_logs:
            self.agent_private_logs[agent_id].append(msg)
            self.append_to_file(f"logs/private_{agent_id}.txt", msg)
        self.master_log.append(f"[PRIVATE:{agent_id}] {msg}")

    def append_to_file(self, filepath: str, msg: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

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
            if cible:
                self.log_master(f"{seer.name} (voyante) espionne {cible.name} → {cible.role}")
                self.log_agent(seer.agent_id, f"{cible.name} est un {cible.role}")
        # 2. Loups : Premier tour de vote
        wolves = [a for a in self.agents if a.role == "Werewolf" and a.status == "alive"]
        wolf_votes_1 = {}
        for wolf in wolves:
            cible_id = wolf.vote_to_kill(self)
            wolf_votes_1[wolf.agent_id] = cible_id
        # Résultats visibles à tous les loups (mémoire partagée + log)
        votes_info_1 = ", ".join([f"{w.name} → {wolf_votes_1[w.agent_id]}" for w in wolves])
        for wolf in wolves:
            wolf.memory.add(f"Premier tour : votes des loups : {votes_info_1}")
            self.log_wolf(f"[TOUR 1] {wolf.name} vote pour {wolf_votes_1[wolf.agent_id]}")
        # 3. Loups : Deuxième tour de vote (séquentiel, chaque loup voit les votes précédents)
        wolf_votes_2 = {}
        votes_so_far = []
        for wolf in wolves:
            # Mémoire : votes précédents
            if votes_so_far:
                wolf.memory.add(f"Deuxième tour : votes précédents : {', '.join(votes_so_far)}")
            cible_id = wolf.vote_to_kill(self)
            wolf_votes_2[wolf.agent_id] = cible_id
            cible = next((a for a in self.agents if a.agent_id == cible_id), None) if cible_id else None
            vote_str = f"{wolf.name} → {cible.name if cible else 'aucune cible'}"
            votes_so_far.append(vote_str)
            # Log et mémoire partagée
            for w in wolves:
                w.memory.add(f"Deuxième tour : {vote_str}")
            self.log_wolf(f"[TOUR 2] {vote_str}")
        # 4. Calcul de la majorité sur le second tour
        vote_targets = [cible_id for cible_id in wolf_votes_2.values() if cible_id]
        if vote_targets:
            from collections import Counter
            count = Counter(vote_targets)
            cible_majoritaire, nb = count.most_common(1)[0]
            if nb > len(wolves)//2:
                cible_agent = next((a for a in self.agents if a.agent_id == cible_majoritaire and a.status == "alive"), None)
                if cible_agent:
                    cible_agent.status = "dead"
                    self.night_victim = cible_agent
                    print(f">>> Victime de la nuit : {cible_agent.name} <<<")
                    self.log_public(f"Victime de la nuit : {cible_agent.name}")
            else:
                self.night_victim = None
                print(">>> Pas de majorité, personne n'est éliminé cette nuit. <<<")
                self.log_public(">>> Pas de majorité, personne n'est éliminé cette nuit. <<<")
        else:
            self.night_victim = None
            print(">>> Aucun vote de loup valide cette nuit. <<<")
            self.log_public(">>> Aucun vote de loup valide cette nuit. <<<")

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
