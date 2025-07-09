from .system_templates import SYSTEM_PROMPTS
from collections import Counter

def build_prompt(agent, action, game_state):
    # Bloc de rappel des règles (toujours présent)
    regles = (
        "🧾 Règles du jeu – Loup-Garou (rappel)\n"
        "\nLe jeu alterne entre nuit et jour.\n"
        "\t•\t🌙 La nuit, certains rôles agissent en secret :\n"
        "\t•\tLes loups-garous votent (séparément) pour éliminer un joueur.\n"
        "\t•\tLa voyante peut inspecter le rôle d’un joueur.\n"
        "\t•\t🌞 Le jour, tous les joueurs discutent puis votent pour éliminer un suspect.\n"
        "\t•\tLe jeu continue jusqu’à ce que :\n"
        "\t•\tTous les loups soient morts → les villageois gagnent\n"
        "\t•\tLes loups soient en nombre égal ou supérieur aux autres → les loups gagnent\n"
        "\n🕵️ Ton rôle est secret. Tu dois défendre ton camp sans te faire démasquer.\n"
        "\n⸻\n"
    )
    # Calcul de la composition actuelle (vivants)
    roles = [a.role for a in game_state.agents if a.status == "alive"]
    counts = Counter(roles)
    role_labels = {
        "Werewolf": "loup-garou",
        "Villager": "villageois",
        "Seer": "voyante"
    }
    compo = []
    for role, label in role_labels.items():
        n = counts.get(role, 0)
        if n > 0:
            compo.append(f"{n} {label}{'s' if n > 1 and label != 'voyante' else ''}")
    compo_str = "Composition actuelle : " + ", ".join(compo) + ".\n"
    # 1. Prompt système
    base = SYSTEM_PROMPTS.get(agent.role, "")
    prompt = regles + compo_str + base + "\n"

    # 2. Rappel des règles (optionnel)
    if game_state.turn <= 2:
        prompt += "Rappel des règles : Discussion > Vote > Nuit. Le but de ton rôle est décrit ci-dessus.\n"

    # 3. État du jeu
    prompt += f"Tour actuel : {game_state.turn}\n"
    prompt += f"Joueurs encore en vie : {', '.join([f'{a.agent_id} - {a.name}' for a in game_state.agents if a.status == 'alive'])}\n"
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
        prompt += "Exprime-me toi dans ton rôle auprès des autres joueurs. Ta réponse doit être naturelle, cohérente avec la discussion et dans l'intérêt de ton rôle."
    elif action == "vote":
        prompt += "Vote pour un joueur à éliminer, dans ton intérêt pour gagner la partie, en répondant uniquement : ID - NOM - RAISON"
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
