# 🐺 Loup-Garou IA – Architecture du Projet

## 📦 Structure générale du projet

```text
werewolf_ai/
├── agents/                  # Définition des rôles d’agents IA
│   ├── base_agent.py        # Classe mère avec méthodes génériques
│   ├── villager.py          # Villageois : rôle honnête, pas d’action de nuit
│   ├── werewolf.py          # Loup-garou : bluffe + tue la nuit
│   ├── seer.py              # Voyante : vision nocturne
│   └── …                    # Autres rôles : sorcière, chasseur, etc.
│
├── game/                    # Orchestration du jeu (moteur, tours, états)
│   ├── game_engine.py       # Maître du jeu : boucle principale
│   ├── phase_controller.py  # Gère les phases jour/nuit
│   ├── roles.py             # Attribution aléatoire des rôles
│   ├── game_state.py        # Suivi des vivants, morts, votes…
│   ├── actions.py           # Enum et objets représentant les actions
│
├── llm/                     # Interface avec les modèles de langage
│   ├── llm_interface.py     # Appels API aux LLM (OpenAI, Mistral…)
│   ├── parser.py            # Nettoyage et parsing des réponses
│
├── memory/                  # Mémoires contextuelles par agent
│   ├── memory.py            # Classe AgentMemory (log + résumé)
│   └── summarizer.py        # (Optionnel) résumés automatiques par LLM
│
├── prompts/                 # Templates de prompts
│   ├── system_templates.py  # Prompts systèmes par rôle (personnalité)
│   ├── prompt_utils.py      # Génération dynamique de prompts par tour
│
├── main.py                  # Point d’entrée du jeu (lance une partie)
├── config.py                # Config globale : nb joueurs, options debug…
├── requirements.txt         # Dépendances Python
├── README.md                # Description du projet
└── logs/                    # Logs des parties (markdown ou txt)
```

---

## 👤 Structure des classes

### 🔹 BaseAgent (dans `agents/base_agent.py`)

Classe mère commune à tous les rôles. Ne contient aucun comportement propre à un rôle, mais une structure de base.

**Attributs :**
- `name: str` → nom public de l’agent  
- `role: str` → rôle (ex. “Villager”, “Werewolf”, etc.)  
- `memory: AgentMemory` → mémoire personnelle de l’agent  
- `status: str` → `"alive"` ou `"dead"`

**Méthodes :**
- `talk(context: dict) -> str`  
  L’agent génère un message public pendant la phase de jour (discussion).
- `vote(players_alive: List[str]) -> str`  
  L’agent choisit un joueur à éliminer.
- `night_action(players_alive: List[str]) -> Optional[str]`  
  L’agent effectue son action de nuit s’il en a une (loup, voyante…).
- `receive_info(info: str)`  
  L’agent reçoit une info du Game Master (ex : une vision ou une mort).

👉 Chaque rôle hérite de `BaseAgent` et surcharge certaines méthodes (notamment `talk()` et `night_action()`) pour adapter son comportement.

---

### 🐺 Exemple : `Werewolf(BaseAgent)` (dans `agents/werewolf.py`)

**Surcharges :**
- `talk()` → bluffe, détourne les soupçons  
- `night_action()` → choisit un joueur à tuer (via LLM)  
- Accès éventuel à une liste d’autres loups (coopération)

---

### 🔮 Exemple : `Seer(BaseAgent)` (dans `agents/seer.py`)

**Surcharges :**
- `night_action()` → vision d’un joueur (renvoie son rôle)  
- `receive_info()` → stocke la révélation dans la mémoire

---

### 🧠 AgentMemory (dans `memory/memory.py`)

Permet à chaque agent de se souvenir de ce qu’il a vu ou entendu.

**Méthodes clés :**
- `add(message: str)` → ajoute un fait ou une observation  
- `get_recent(n: int)` → récupère les derniers événements  
- `get_summary()` → retourne un résumé textuel (manuel ou via LLM)

---

### 🎮 WerewolfGame (dans `game/game_engine.py`)

Classe principale du moteur de jeu. Ordonne les phases, les actions, les votes et vérifie les conditions de victoire.

**Attributs :**
- `agents: List[BaseAgent]` → liste des joueurs en jeu  
- `turn: int` → compteur de tours  
- `log: List[str]` → journal textuel du jeu

**Méthodes principales :**
- `play()` → lance la partie complète (nuit/jour)  
- `run_night_phase()` → collecte les actions de nuit  
- `run_day_phase()` → gère la discussion + votes  
- `resolve_votes()` → élimine un joueur  
- `check_win_condition()` → vérifie si une faction a gagné

---

### 🧩 AgentAction (dans `game/actions.py`)

Représente une action prise par un agent.

**Champs :**
- `actor: str` → nom de l’agent qui agit  
- `type: ActionType` → `"VOTE"`, `"KILL"`, `"PEEK"`, etc.  
- `target: str` → nom de la cible  
- `reason: Optional[str]` → justification (utile pour le log ou le prompt)

---

### 🧠 Interaction avec le LLM (dans `llm/llm_interface.py`)

Contient :
- `call_llm(prompt: str) -> str` → envoie un prompt et retourne la réponse  
- Gère les appels API, les retries, les logs éventuels

⚠️ **Particularité**  
Les agents n’ont pas de mémoire native : on leur redonne à chaque appel leur historique résumé dans le prompt.

---

### 📜 Prompts et Personnalités (dans `prompts/system_templates.py`)

Pour chaque rôle, on définit un prompt système du style :

```text
Tu es un loup-garou. Tu fais semblant d’être villageois.
Tu dois manipuler subtilement les autres joueurs.
Tu sais que les autres loups sont : Agent B, Agent C.
Réponds de manière crédible.
```

---

🚀 **main.py : lancement d’une partie**

Contient typiquement :

```python
from game.game_engine import WerewolfGame
from game.roles import assign_roles

agents = assign_roles(nb_players=5)
game = WerewolfGame(agents)
game.play()
```

---

🔧 **À faire pour démarrer**

✅ Créer 3 rôles de base :
- Villageois (ne fait rien la nuit)
- Loup-Garou (vote la nuit, bluffe le jour)
- Voyante (voit un rôle la nuit)

✅ Implémenter :
- `talk()`
- `vote()`
- `night_action()`
- Prompts systèmes pour chaque rôle

✅ Orchestration basique :
- Alternance jour/nuit
- Élimination et fin du jeu
- Log textuel de la partie (markdown ou terminal)

---

🧠 **Extensions faciles ensuite**
- Ajouter des rôles (sorcière, chasseur…)
- Ajouter une mémoire plus poussée
- Ajouter une UI simple (Streamlit ?)
- Ajouter un joueur humain dans la boucle

---

🎯 **Objectifs du projet**

Ce projet est conçu pour :
- être collaboratif (séparation claire des rôles)
- être fun à tester (logs lisibles, surprises dans les réponses)
- permettre des démos rapides et virales
