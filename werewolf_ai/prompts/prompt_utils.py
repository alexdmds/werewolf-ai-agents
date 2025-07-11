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

    # 4. Morts précédents (on prend les messages du channel 'public' qui annoncent les morts)
    morts_logs = [msg for msg in game_state.logs.get("public", []) if "a été tué" in msg or "a été éliminé" in msg]
    if morts_logs:
        prompt += "Morts précédents :\n\t• " + "\n\t• ".join(morts_logs[-3:]) + "\n"
    else:
        prompt += "Aucun mort pour l'instant.\n"

    # 5. Mémoire personnelle de l'agent
    mem = agent.memory.get_recent(3)
    if mem:
        prompt += "Mémoire :\n\t• " + "\n\t• ".join(mem) + "\n"
    else:
        prompt += "Mémoire : (aucun événement marquant)\n"

    # 6. Historique des discussions accessibles (channels)
    # Tout le monde a accès à 'public'
    # Les loups à 'wolves', la voyante à 'seer'
    discussions = []
    discussions += game_state.logs.get("public", [])[-3:]
    if agent.role == "Werewolf":
        discussions += game_state.logs.get("wolves", [])[-3:]
    if agent.role == "Seer":
        discussions += game_state.logs.get("seer", [])[-3:]
    # On retire les doublons tout en gardant l'ordre
    seen = set()
    discussions_unique = []
    for msg in discussions:
        if msg not in seen:
            discussions_unique.append(msg)
            seen.add(msg)
    if discussions_unique:
        prompt += "Discussions accessibles :\n\t• " + "\n\t• ".join(discussions_unique[-3:]) + "\n"
    else:
        prompt += "Discussions accessibles : (aucune discussion récente)\n"

    # 7. Instruction/action à exécuter
    if action == "talk":
        prompt += "Répond aux derniers messages, de façon naturelle comme dans une discussion. Attention ce que tu dis est publique. Parle dans le but de défendre ton rôle et de convaincre les autres joueurs. Sois très concis."
    elif action == "vote":
        prompt += "Vote pour éliminer un joueur encore vivant du village. Attention ce vote est publique. Agis dans l'intérêt de ton camp et dans ton intérêt. Réponds uniquement par celui que tu veux éliminer : ID - NOM - RAISON"
    elif action == "spy":
        prompt += "Choisis un joueur dont tu souhaites connaitre le rôle (que tu ne connais pas déjà) pour aider les villageois à démasquer les loups."
    elif action == "vote_to_kill":
        prompt += "Choisis une victime à éliminer dans l'intérêt des loups."
    else:
        prompt += "Agis selon l'action demandée."
    return prompt
