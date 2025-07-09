from .system_templates import SYSTEM_PROMPTS

def build_prompt(agent, action, game_state):
    # 1. Prompt système
    base = SYSTEM_PROMPTS.get(agent.role, "")
    prompt = base + "\n"

    # 2. Rappel des règles (optionnel)
    if game_state.turn <= 2:
        prompt += "Rappel des règles : Discussion > Vote > Nuit. Le but de ton rôle est décrit ci-dessus.\n"

    # 3. État du jeu
    prompt += f"Tour actuel : {game_state.turn}\n"
    prompt += f"Joueurs encore en vie : {', '.join(game_state.get_alive_names())}\n"
    morts = game_state.get_deaths_summary()
    if morts:
        prompt += "Morts précédents :\n\t• " + "\n\t• ".join(morts) + "\n"
    else:
        prompt += "Aucun mort pour l'instant.\n"

    # 4. Mémoire personnelle de l'agent
    mem = agent.memory.get_recent(3)
    if mem:
        prompt += "Mémoire :\n\t• " + "\n\t• ".join(mem) + "\n"
    else:
        prompt += "Mémoire : (aucun événement marquant)\n"

    # 5. Historique public récent
    histo = game_state.get_last_discussion(3)
    if histo:
        prompt += "Discussion précédente :\n\t• " + "\n\t• ".join(histo) + "\n"
    else:
        prompt += "Discussion précédente : (aucune discussion récente)\n"

    # 6. Instruction/action à exécuter
    if action == "talk":
        prompt += "Exprime ton avis sur les autres joueurs."
    elif action == "vote":
        prompt += "Vote pour un joueur en répondant uniquement : NOM – RAISON"
    elif action == "night_action":
        if agent.role == "Werewolf":
            prompt += "Choisis une victime à éliminer."
        elif agent.role == "Seer":
            prompt += "Choisis un joueur à espionner."
        else:
            prompt += "Agis selon ton rôle."
    else:
        prompt += "Agis selon l'action demandée."
    return prompt
