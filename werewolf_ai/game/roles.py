import random
from agents.villager import Villager
from agents.werewolf import Werewolf
from agents.seer import Seer
from llm.llm_interface import RealLLM

def assign_roles(nb_players=5):
    agents = []
    if nb_players < 3:
        raise ValueError("Il faut au moins 3 joueurs")
    def gen_id():
        return ''.join(random.choices('0123456789abcdef', k=6))
    llm = RealLLM()
    # Noms prédéfinis (loups, voyante, villageois)
    wolf_names = ["Paul", "Marc", "Julie", "Nina", "Alex"]
    villager_names = ["Luc", "Sophie", "Julie", "Marc", "Nina", "Alex"]
    seer_name = "Marie"
    # 1. Voyante
    agents.append(Seer(seer_name, llm=llm, agent_id=gen_id()))
    # 2. Loups (environ 1/3 des joueurs, arrondi sup)
    n_wolves = max(1, nb_players // 3)
    for i in range(n_wolves):
        agents.append(Werewolf(wolf_names[i], [], llm=llm, agent_id=gen_id()))
    # 3. Villageois (le reste)
    used_names = set([seer_name] + wolf_names[:n_wolves])
    v_names = [n for n in villager_names if n not in used_names]
    while len(agents) < nb_players:
        agents.append(Villager(v_names.pop(0), llm=llm, agent_id=gen_id()))
    return agents
