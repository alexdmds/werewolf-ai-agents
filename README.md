# Werewolf AI Agents

## Architecture des actions

### Actions nocturnes
- **Voyante** : méthode `spy(game_state)`
    - Génère un prompt spécifique, appelle le LLM, parse la cible, ajoute la vision à la mémoire, retourne l'ID de la cible.
- **Loup-garou** : méthode `vote_to_kill(game_state)`
    - Génère un prompt spécifique, appelle le LLM, parse la cible, retourne l'ID de la cible.
- **Villageois** : n'a pas d'action de nuit.

> Il n'existe plus de méthode générique `night_action`. Chaque rôle a une interface explicite adaptée à sa mécanique.

### Boucle de jeu (exemple)
```python
# Nuit
seer = next((a for a in agents if a.role == "Seer" and a.status == "alive"), None)
if seer:
    cible_id = seer.spy(game_state)
    # ...
wolves = [a for a in agents if a.role == "Werewolf" and a.status == "alive"]
wolf_votes = {wolf.agent_id: wolf.vote_to_kill(game_state) for wolf in wolves}
# ...

# Jour
for agent in agents:
    if agent.status == "alive":
        print(agent.talk(game_state))
for agent in agents:
    if agent.status == "alive":
        vote_id = agent.vote(game_state)
        # ...
```

### Prompts
- Le prompt est généré selon l'action : `spy`, `vote_to_kill`, `talk`, `vote`.
- Les instructions sont adaptées à chaque action (ex : "Choisis un joueur à espionner." pour la voyante).

### Séparation des responsabilités
- **Agents** : chaque rôle implémente ses propres méthodes d'action.
- **Moteur de jeu** : orchestre la séquence des actions, applique les effets globaux (élimination, révélation, etc.).
- **Prompts** : générés dynamiquement selon l'action et le contexte.
- **Tests** : n'appliquent aucun effet, ils appellent simplement les méthodes d'action et observent le résultat.

### Exemple d'appel d'action nocturne
```python
# Pour la voyante
cible_id = seer.spy(game_state)
# Pour un loup
cible_id = werewolf.vote_to_kill(game_state)
```

---

Pour toute extension (nouveau rôle, nouvelle action), il suffit d'ajouter une méthode dédiée dans la classe de rôle concernée et d'adapter le moteur de jeu pour l'appeler au bon moment.
