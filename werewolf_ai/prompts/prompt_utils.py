from collections import Counter

def build_prompt(agent, action, game_state):
    # 1. Introduction
    intro = (
        f"Tu es un joueur du jeu 'Le loup-garou'. Ton nom est {agent.name}. Tu vas agir et jouer dans ton intérêt pour gagner la partie."
    )

    # 2. Liste claire des joueurs
    joueurs = []
    for a in game_state.agents:
        status = "vivant" if a.status == "alive" else "mort"
        if a.status == "dead":
            role = a.role
        elif a.agent_id == agent.agent_id:
            role = a.role
        else:
            role = "?"
        moi = " <= TOI" if a.agent_id == agent.agent_id else ""
        joueurs.append(f"- {a.name} (ID: {a.agent_id}) | {status} | rôle: {role}{moi}")
    joueurs_str = "Liste des joueurs :\n" + "\n".join(joueurs)

    # 3. Rappel concis des règles
    regles = (
        "Règles : Nuit : les loups votent pour tuer, la voyante inspecte. Jour : discussion puis vote public pour éliminer un suspect.\n"
        "Victoire : village si plus de loup vivant, loups si plus de villageois.\n"
    )

    # 4. Structure de la partie actuelle
    tour = f"Tour actuel : {game_state.turn}"
    structure = f"{tour}"

    # 5. Rôle et objectif
    objectifs = {
        "Werewolf": "Tu es loup-garou. Ton but : qu'à la fin il ne reste que des loups. Collabore avec tes alliés loups, élimine les autres.",
        "Villager": "Tu es villageois. Ton but : survivre et éliminer tous les loups-garous.",
        "Seer": "Tu es la voyante. Ton but : aider le village en découvrant le rôle d'un joueur chaque nuit."
    }
    role_str = f"Rôle : {agent.role}\nObjectif : {objectifs.get(agent.role, '')}"

    # 6. Mémoire personnelle
    mem = agent.memory.get_recent(5)
    mem_str = "Mémoire personnelle :\n" + ("\n".join(f"- {m}" for m in mem) if mem else "(aucun événement)")

    # 7. Historique des channels accessibles
    channels = list(game_state.subscriptions.get(agent.agent_id, []))
    if "public" not in channels:
        channels.append("public")
    logs = []
    for ch in channels:
        logs += game_state.logs.get(ch, [])[-10:]
    seen = set()
    logs_unique = []
    for msg in logs:
        if msg not in seen:
            logs_unique.append(msg)
            seen.add(msg)
    histo_str = "Historique accessible :\n" + ("\n".join(f"- {m}" for m in logs_unique[-10:]) if logs_unique else "(aucun événement)")

    # 8. Consigne d'action claire
    consignes = {
        "talk": "Réponds aux discussions du village de façon naturelle et informelle. Sois concis, pertinent, et défends ton camp.",
        "vote": "Vote pour éliminer un joueur vivant dans le but de ton camp. Réponds uniquement par : ID - NOM - RAISON.",
        "spy": "Choisis un joueur dont tu veux connaitre le rôle, dans le but de ton camp. Réponds uniquement par l'ID.",
        "vote_to_kill": "Choisis une victime à éliminer, dans le but de ton camp. Réponds uniquement par l'ID."
    }
    consigne = consignes.get(action, "Agis selon l'action demandée.")

    # Construction finale structurée
    prompt = (
        intro + "\n\n" +
        joueurs_str + "\n\n" +
        regles + "\n" +
        structure + "\n\n" +
        role_str + "\n\n" +
        mem_str + "\n\n" +
        histo_str + "\n\n" +
        f"Action demandée : {consigne}"
    )
    return prompt
