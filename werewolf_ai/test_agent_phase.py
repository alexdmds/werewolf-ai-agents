import os
from game.roles import assign_roles
from game.game_engine import WerewolfGame
from agents.seer import Seer
from agents.werewolf import Werewolf
from agents.villager import Villager
from llm.llm_interface import RealLLM
import config
import re

# Force l'utilisation du vrai LLM
config.USE_MOCK_LLM = False

# Choix de l'agent à tester et de la phase
AGENT_TYPE = "Werewolf"  # "Seer", "Werewolf", "Villager"
PHASE = "night_action"       # "talk", "vote", "night_action"

# Création d'un état de jeu minimal
agents = [
    Werewolf("Paul", ["Paul"]),
    Seer("Marie"),
    Villager("Luc"),
    Villager("Sophie")
]
game = WerewolfGame(agents)
game.turn = 2  # Par exemple, tour 2

# Simule un contexte riche
# 1. Morts précédents
agents[2].status = "dead"  # Luc est mort
# 2. Mémoire de l'agent testé
if AGENT_TYPE == "Seer":
    agents[1].memory.add("T1 : Paul m'a accusée")
    agents[1].memory.add("T1 : J'ai voté contre Luc")
    agents[1].memory.add("T2 : Paul a affirmé être simple villageois")
if AGENT_TYPE == "Werewolf":
    agents[0].memory.add("T1 : Marie m'a suspecté")
    agents[0].memory.add("T1 : J'ai voté contre Luc")
    agents[0].memory.add("T2 : Sophie a défendu Marie")
if AGENT_TYPE == "Villager":
    agents[3].memory.add("T1 : J'ai été accusée par Paul")
    agents[3].memory.add("T1 : J'ai voté contre Luc")
    agents[3].memory.add("T2 : Marie a dit avoir eu une vision")
# 3. Historique public
# (On simule 3 messages de discussion)
game.log = [
    "Paul : Je pense que Marie cache quelque chose.",
    "Marie : Je soupçonne Paul, il est trop discret.",
    "Sophie : Luc était trop silencieux hier."
]

# On peut simuler des morts ou des événements si besoin
# agents[2].status = "dead"
# agents[1].memory.add("J'ai eu une vision sur Loup 1 : il est loup !")

# Sélection de l'agent à tester
if AGENT_TYPE == "Seer":
    agent = agents[1]
elif AGENT_TYPE == "Werewolf":
    agent = agents[0]
else:
    agent = agents[2]

# Remplace le LLM de l'agent par RealLLM
agent.llm = RealLLM()

def parse_llm_action(response):
    """
    Extrait l'ID (6 caractères hex) de la réponse du LLM (format : ID - NOM - RAISON).
    Ignore tout texte avant le premier ID. Tolère 'Je vote pour :' ou autres préfixes.
    """
    # Cherche le premier motif d'ID hexadécimal suivi de ' - NOM - RAISON'
    match = re.search(r"([0-9a-fA-F]{6})\s*-\s*([^-\n]+)\s*-\s*(.+)", response)
    if match:
        agent_id, name, reason = match.groups()
        return agent_id.strip(), name.strip(), reason.strip()
    return None, None, None


def apply_vote_action(agent_id, agents):
    """Trouve l'agent par ID et le retourne (pour simuler l'élimination, etc.)."""
    for ag in agents:
        if ag.agent_id == agent_id:
            return ag
    return None

def parse_night_action(response, agents):
    """
    Extrait l'ID (6 caractères hex) ou le nom d'un joueur dans la réponse du LLM pour la night_action.
    Retourne l'agent cible si trouvé.
    """
    # Cherche d'abord un ID
    match = re.search(r"([0-9a-fA-F]{6})", response)
    if match:
        agent_id = match.group(1)
        for ag in agents:
            if ag.agent_id == agent_id and ag.status == "alive":
                return ag
    # Sinon, cherche un nom de joueur vivant dans la réponse
    for ag in agents:
        if ag.status == "alive" and ag.name.lower() in response.lower():
            return ag
    return None

# Appel de la phase choisie
if PHASE == "talk":
    prompt = agent.build_prompt("talk", game)
    print("\n--- PROMPT GÉNÉRÉ ---\n")
    print(prompt)
    print("\n--- RÉPONSE LLM ---\n")
    print(agent.talk(game))
elif PHASE == "vote":
    prompt = agent.build_prompt("vote", game)
    print("\n--- PROMPT GÉNÉRÉ ---\n")
    print(prompt)
    print("\n--- RÉPONSE LLM ---\n")
    response = agent.vote(game)
    print(response)
    voted_id, voted_name, voted_reason = parse_llm_action(response)
    if voted_id:
        print(f"\n[PARSE] LLM a voté pour : ID={voted_id}, NOM={voted_name}, RAISON={voted_reason}")
        target = apply_vote_action(voted_id, agents)
        if target:
            print(f"[ACTION] L'agent ciblé est : {target} (statut actuel : {target.status})")
        else:
            print("[ACTION] Aucun agent trouvé avec cet ID !")
    else:
        print("[PARSE] Impossible d'extraire l'ID de la réponse LLM.")
elif PHASE == "night_action":
    prompt = agent.build_prompt("night_action", game)
    print("\n--- PROMPT GÉNÉRÉ ---\n")
    print(prompt)
    print("\n--- RÉPONSE LLM ---\n")
    response = agent.night_action(game)
    print(response)
    target = parse_night_action(response, agents)
    if target:
        print(f"\n[PARSE] LLM cible : {target.agent_id} - {target.name}")
        print(f"[ACTION] Rôle révélé à la voyante : {target.role}")
        # On peut simuler l'ajout à la mémoire de la voyante :
        if agent.role == "Seer":
            agent.memory.add(f"Vision : {target.name} ({target.agent_id}) est {target.role}")
    else:
        print("[PARSE] Impossible d'extraire la cible de la night action.")
else:
    print("Phase non reconnue. Modifiez PHASE dans le script.") 