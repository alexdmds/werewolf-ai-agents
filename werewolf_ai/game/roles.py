from agents.villager import Villager
from agents.werewolf import Werewolf
from agents.seer import Seer

def assign_roles(nb_players=5):
    agents = []
    if nb_players < 3:
        raise ValueError("Il faut au moins 3 joueurs")
    agents.append(Werewolf("Loup 1", []))
    agents.append(Seer("Voyante"))
    for i in range(nb_players - 2):
        agents.append(Villager(f"Villageois {i+1}"))
    return agents
