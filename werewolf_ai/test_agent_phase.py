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

# Paramètres de test
AGENT_NAME = "Marc"  # Nom de l'agent à tester (ex : "Paul", "Marie", "Julie", ...)
PHASE = "talk"  # "talk", "vote", "night_action"

# Création d'un état de jeu complexe
loups = [
    Werewolf("Paul"),
    Werewolf("Marc"),
    Werewolf("Julie")
]
villagers = [
    Villager("Marie"),
    Villager("Sophie"),
    Villager("Luc")
]
agents = loups + villagers
game = WerewolfGame(agents)
game.turn = 3

# Morts précédents
luc = next((a for a in agents if a.name == "Luc"), None)
if luc:
    luc.status = "dead"  # Luc est mort

# Mémoires variées
loups[0].memory.add("T1 : Marie m'a accusé")
loups[0].memory.add("T2 : J'ai voté contre Luc")
loups[0].memory.add("T2 : Loups connus : Marc ({}), Julie ({})".format(loups[1].agent_id, loups[2].agent_id))
loups[1].memory.add("T1 : J'ai été accusé par Sophie")
loups[1].memory.add("T2 : J'ai voté contre Luc")
loups[1].memory.add("T2 : Loups connus : Paul ({}), Julie ({})".format(loups[0].agent_id, loups[2].agent_id))
loups[2].memory.add("T1 : J'ai été accusée par Paul")
loups[2].memory.add("T2 : J'ai voté contre Luc")
loups[2].memory.add("T2 : Loups connus : Paul ({}), Marc ({})".format(loups[0].agent_id, loups[1].agent_id))
villagers[0].memory.add("T1 : J'ai été accusée par Paul")
villagers[0].memory.add("T2 : J'ai voté contre Luc")
villagers[1].memory.add("T1 : J'ai été accusée par Julie")
villagers[1].memory.add("T2 : J'ai voté contre Luc")

# Historique public
# (On simule 5 messages de discussion)
game.log = [
    "Paul : Je pense que Marie cache quelque chose.",
    "Marc : Je trouve Sophie trop discrète.",
    "Julie : On devrait surveiller Marie.",
    "Marie : Je soupçonne Paul, il est trop discret.",
    "Sophie : Luc était trop silencieux hier."
]

def parse_action_response(response, agents):
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

# Sélection de l'agent à tester
agent = next((a for a in agents if a.name == AGENT_NAME), None)
if not agent:
    print(f"Aucun agent nommé {AGENT_NAME} dans la partie.")
    exit(1)

# Affiche le contexte de test
print("\n=== CONTEXTE DE TEST ===\n")
print(f"Tour : {game.turn}")
print("Joueurs vivants :", ", ".join(f"{a.name} ({a.agent_id})" for a in agents if a.status == "alive"))
print("Morts :", ", ".join(f"{a.name} ({a.agent_id})" for a in agents if a.status == "dead"))
print(f"\nMémoire de {agent.name} :")
for m in agent.memory.get_recent(10):
    print("   ", m)
print("\nHistorique public :")
for msg in game.log:
    print("   ", msg)

# Teste uniquement l'action demandée
prompt = agent.build_prompt(PHASE, game)
print(f"\n--- PROMPT POUR {agent.name} ({agent.agent_id}) ---\n")
print(prompt)
response = getattr(agent, PHASE)(game)
print(f"\n--- RÉPONSE LLM DE {agent.name} ---\n")
print(response)

# Si l'action est vote ou night_action, on parse la cible
if PHASE in ("vote", "night_action"):
    if response is not None:
        cible = parse_action_response(response, agents)
        if cible:
            print(f"[PARSE] {agent.name} cible : {cible.agent_id} - {cible.name}")
            if PHASE == "vote":
                print(f"[ACTION] {agent.name} voterait pour {cible.name}")
            elif PHASE == "night_action":
                if agent.role == "Seer":
                    print(f"[ACTION] Rôle révélé à la voyante : {cible.role}")
                    agent.memory.add(f"Vision : {cible.name} ({cible.agent_id}) est {cible.role}")
                elif agent.role == "Werewolf":
                    cible.status = "dead"
                    print(f"[ACTION] {cible.name} est maintenant éliminé (statut : {cible.status})")
        else:
            print(f"[PARSE] {agent.name} : impossible d'extraire la cible.")
    else:
        print(f"[INFO] {agent.name} n'a pas d'action à parser pour cette phase.") 