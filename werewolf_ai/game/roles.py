import random
from agents.villager import Villager
from agents.werewolf import Werewolf
from agents.seer import Seer

def assign_roles(nb_players=5):
    agents = []
    if nb_players < 3:
        raise ValueError("Il faut au moins 3 joueurs")
    def gen_id():
        return ''.join(random.choices('0123456789abcdef', k=6))
    agents.append(Werewolf("Paul", [], agent_id=gen_id()))
    agents.append(Seer("Marie", agent_id=gen_id()))
    for i, name in enumerate(["Luc", "Sophie", "Julie", "Marc", "Nina", "Alex"], start=1):
        if len(agents) < nb_players:
            agents.append(Villager(name, agent_id=gen_id()))
    return agents
