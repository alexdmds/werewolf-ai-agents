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
AGENT_NAME = "Marie"  # Nom de l'agent à tester (ex : "Paul", "Marie", "Julie", ...)
PHASE = "spy"  # "talk", "vote", "spy", "vote_to_kill"

# Création d'un état de jeu complexe
seer = Seer("Marie")
loups = [
    Werewolf("Paul"),
    Werewolf("Marc"),
    Werewolf("Julie")
]
villagers = [
    Villager("Sophie"),
    Villager("Luc")
]
agents = [seer] + loups + villagers
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
prompt = None
if PHASE == "spy" and agent.role == "Seer":
    prompt = agent.build_prompt("spy", game)
    print(f"\n--- PROMPT POUR {agent.name} ({agent.agent_id}) ---\n")
    print(prompt)
    cible_id = agent.spy(game)
    if cible_id:
        cible = next((a for a in agents if a.agent_id == cible_id), None)
        print(f"[ACTION] Voyante espionne : {cible.name} ({cible.agent_id}) rôle : {cible.role}")
    else:
        print("[ACTION] Voyante : aucune cible trouvée.")
elif PHASE == "vote_to_kill" and agent.role == "Werewolf":
    prompt = agent.build_prompt("vote_to_kill", game)
    print(f"\n--- PROMPT POUR {agent.name} ({agent.agent_id}) ---\n")
    print(prompt)
    cible_id = agent.vote_to_kill(game)
    if cible_id:
        cible = next((a for a in agents if a.agent_id == cible_id), None)
        print(f"[ACTION] Loup voterait pour éliminer : {cible.name} ({cible.agent_id})")
    else:
        print("[ACTION] Loup : aucune cible trouvée.")
else:
    prompt = agent.build_prompt(PHASE, game)
    print(f"\n--- PROMPT POUR {agent.name} ({agent.agent_id}) ---\n")
    print(prompt)
    response = getattr(agent, PHASE)(game)
    print(f"\n--- RÉPONSE LLM DE {agent.name} ---\n")
    print(response)
    if PHASE == "vote":
        if response is not None:
            cible = next((a for a in agents if a.agent_id == response or a.name.lower() in str(response).lower()), None)
            if cible:
                print(f"[ACTION] {agent.name} voterait pour {cible.name}")
            else:
                print(f"[PARSE] {agent.name} : impossible d'extraire la cible.")
        else:
            print(f"[INFO] {agent.name} n'a pas d'action à parser pour cette phase.") 