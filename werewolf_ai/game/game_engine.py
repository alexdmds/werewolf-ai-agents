from typing import List
import os
from collections import defaultdict

class WerewolfGame:
    def __init__(self, agents: List):
        self.agents = agents
        self.turn = 0
        self.game_over = False
        # logs[channel] = list[str]
        self.logs = defaultdict(list)          # ex. logs["public"], logs["wolves"], logs["master"]
        # map agent_id -> set(channel)
        self.subscriptions = defaultdict(set)
        self._init_subscriptions()
    
    def _init_subscriptions(self):
        for agent in self.agents:
            self.subscriptions[agent.agent_id] = set()
            self.subscriptions["public"].add(agent.agent_id)
            if agent.role == "Werewolf":
                self.subscriptions["wolves"].add(agent.agent_id)
            if agent.role == "Seer":
                self.subscriptions["seer"].add(agent.agent_id)

    def record_event(self, msg: str, *, channels: list[str], to_file=True):
        """
        channels  → ex. ["public"], ["wolves"], ["master"], ["seer:ID"], ["lovers"]
        """
        for ch in channels:
            if ch != "master":
                self.logs[ch].append(msg)
                if to_file:
                    self._append_to_file(f"logs/{ch}.txt", msg)
        #On ajoute dans master dans tous les cas
        self.logs["master"].append(msg)
        # Push dans les mémoires abonnées
        for agent in self.agents:
            if any(ch in self.subscriptions[agent.agent_id] for ch in channels):
                agent.memory.add(msg, turn=self.turn)

    def _append_to_file(self, filepath: str, msg: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


    def play(self, max_turns=10):
        print("=== Début de la partie ===")
        print("Joueurs en jeu :", ", ".join([a.name + f" ({a.role})" for a in self.agents]))
        self.turn = 0
        while not self.game_over and self.turn < max_turns:
            self.turn += 1
            print(f"\n===== Tour {self.turn} =====")
            self.night_phase()
            self.check_win_condition()
            if self.game_over:
                break
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
                self.record_event(f"{seer.name} (voyante) espionne {cible.name} → {cible.role}", channels=["master"])
        # 2. Loups : Premier tour de vote (séquentiel, chaque loup voit les votes précédents)
        wolves = [a for a in self.agents if a.role == "Werewolf" and a.status == "alive"]
        wolf_votes_1 = {}
        for wolf in wolves:
            cible_id = wolf.vote_to_kill(self)
            self.record_event(f"{wolf.name} vote pour {cible_id}", channels=["wolves", "master"])
            wolf_votes_1[wolf.agent_id] = cible_id
        # Résultats visibles à tous les loups
        votes_info_1 = ", ".join([f"{w.name} → {wolf_votes_1[w.agent_id]}" for w in wolves])
        self.record_event(f"Premier tour : votes des loups : {votes_info_1}", channels=["wolves", "master"])
        # 3. Loups : Deuxième tour de vote (séquentiel, chaque loup voit les votes précédents)
        wolf_votes_2 = {}
        for wolf in wolves:
            cible_id = wolf.vote_to_kill(self)
            wolf_votes_2[wolf.agent_id] = cible_id
            self.record_event(f"{wolf.name} vote pour {cible_id}", channels=["wolves", "master"])
        #On donne les résultats aux loups
        votes_info_2 = ", ".join([f"{w.name} → {wolf_votes_2[w.agent_id]}" for w in wolves])
        self.record_event(f"Deuxième tour : votes des loups : {votes_info_2}", channels=["wolves", "master"])

        # 4. Calcul de la majorité simple sur le second tour puis élimination
        vote_targets = [cible_id for cible_id in wolf_votes_2.values() if cible_id]
        if vote_targets:
            from collections import Counter
            count = Counter(vote_targets)
            max_votes = max(count.values())
            top_targets = [cid for cid, nb in count.items() if nb == max_votes]
            if len(top_targets) == 1:
                cible_majoritaire = top_targets[0]
                cible_agent = next((a for a in self.agents if a.agent_id == cible_majoritaire and a.status == "alive"), None)
                if cible_agent:
                    cible_agent.status = "dead"
                    self.night_victim = cible_agent
                    print(f">>> Victime de la nuit : {cible_agent.name} <<<")
                    self.record_event(f"Victime de la nuit : {cible_agent.name}", channels=["wolves", "master"])
                    # Annonce publique avec rôle
                    self.record_event(f"Le village découvre au matin que {cible_agent.name} était {cible_agent.role} !", channels=["public", "master"])
                else:
                    print(">>> Les loups n'ont pas voté pour un joueur vivant <<<")
                    self.night_victim = None
                    self.record_event(">>> Les loups n'ont pas voté pour un joueur vivant <<<", channels=["wolves", "master"])
            else:
                print(">>> Pas de majorité, personne n'est éliminé cette nuit. <<<")
                self.night_victim = None
                self.record_event(">>> Pas de majorité, personne n'est éliminé cette nuit. <<<", channels=["wolves", "master"])
        else:
            print(">>> Aucun vote de loup valide cette nuit. <<<")
            self.night_victim = None
            self.record_event(">>> Aucun vote de loup valide cette nuit. <<<", channels=["wolves", "master"])

    def day_phase(self):
        print("\n--- Phase de jour ---")
        # 1. Annonce de la victime de la nuit
        if hasattr(self, 'night_victim') and self.night_victim:
            print(f"Le village découvre au matin que {self.night_victim.name} qui était {self.night_victim.role} a été tué pendant la nuit !")
            self.record_event(f"Le village découvre au matin que {self.night_victim.name} qui était {self.night_victim.role} a été tué pendant la nuit !", channels=["public", "master"])
        else:
            print("Le village découvre au matin qu'il n'y a pas eu de victime cette nuit.")
            self.record_event("Le village découvre au matin qu'il n'y a pas eu de victime cette nuit.", channels=["public", "master"])
        # 2. Chaque agent vivant prend la parole
        for agent in self.agents:
            if hasattr(agent, "talk") and agent.status == "alive":
                msg = agent.talk(self)
                print(f"{agent.name} dit : {msg}")
                self.record_event(f"{agent.name} dit : {msg}", channels=["public", "master"])
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
        
        #On enregistre les votes
        votes_info = ", ".join([f"{a.name} → {votes.get(a.agent_id, 0)}" for a in alive])
        self.record_event(f"Votes du jour : {votes_info}", channels=["public", "master"])
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
                    print(f"{cible_agent.name} qui était {cible_agent.role} est éliminé par le village !")
                    self.record_event(f"{cible_agent.name} qui était {cible_agent.role} est éliminé par le village !", channels=["public", "master"])
            else:
                print("Égalité au vote, personne n'est éliminé.")
                self.record_event("Égalité au vote, personne n'est éliminé.", channels=["public", "master"])
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
        elif not villagers:
            print("\nVictoire des loups-garous !")
            self.game_over = True

    def get_deaths_summary(self):
        morts = [a for a in self.agents if a.status == "dead"]
        if not morts:
            return "Aucun joueur n'a été éliminé."
        return "Joueurs éliminés : " + ", ".join(f"{a.name} ({a.role})" for a in morts)