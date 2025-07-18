import os
if "OPENAI_WEREWOLF_KEY" in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_WEREWOLF_KEY"]
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from agents.base_agent import BaseAgent
from typing import Any

class ToolException(Exception):
    pass

class LangChainWerewolfAgent(BaseAgent):
    def __init__(self, name, role, llm=None, agent_id=None, status="alive"):
        super().__init__(name, role, llm=llm, agent_id=agent_id)
        self.status = status
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0, verbose=True)
        # Quotas d'usage par tour
        self.spy_used_turn = -1
        self.vote_to_kill_used_turn = -1
        self.current_turn = 0
        self.agent_executor = self._build_agent_executor()

    def _build_agent_executor(self):
        tools = [
            Tool(
                name="talk",
                func=self._guarded_talk,
                description="Exprime-toi publiquement pendant la phase de jour."
            ),
            Tool(
                name="vote",
                func=self._guarded_vote,
                description="Vote pour éliminer un joueur vivant (ID)."
            ),
        ]
        if self.role == "Werewolf":
            tools.append(Tool(
                name="vote_to_kill",
                func=self._guarded_vote_to_kill,
                description="(Loup) Vote pour éliminer un joueur la nuit (ID)."
            ))
        if self.role == "Seer":
            tools.append(Tool(
                name="spy",
                func=self._guarded_spy,
                description="(Voyante) Choisis un joueur à espionner la nuit (ID)."
            ))
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._system_prompt()),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, memory=self.memory, verbose=True, max_iterations=2)

    def _system_prompt(self):
        objectifs = {
            "Werewolf": "Tu es loup-garou. Ton but : qu'à la fin il ne reste que des loups. Collabore avec tes alliés loups, élimine les autres.",
            "Villager": "Tu es villageois. Ton but : survivre et éliminer tous les loups-garous.",
            "Seer": "Tu es la voyante. Ton but : aider le village en découvrant le rôle d'un joueur chaque nuit."
        }
        return (
            f"Tu es un agent autonome du jeu 'Le Loup-Garou'.\n"
            f"Nom : {self.name}\nRôle : {self.role}\nObjectif : {objectifs.get(self.role, '')}\n"
            "Agis pour gagner la partie selon ton camp.\n"
            "Utilise les outils disponibles pour parler, voter, espionner, etc.\n"
            "Sois stratégique, concis, et adapte-toi à la situation."
        )

    def _reflect_and_store(self, last_output: str) -> None:
        reflection_prompt = (
            "En une phrase, explique ta stratégie secrète derrière cette action : "
            f"« {last_output} »"
        )
        reflection = self.llm.invoke(reflection_prompt).content
        self.memory.save_context({"input": "[REFLEXION_PRIVEE]"}, {"output": reflection})

    # Guards pour chaque outil
    def _guarded_talk(self, input):
        if self._phase != "jour":
            self.memory.save_context({"input": "[ERREUR] Parler n'est autorisé que le jour."}, {"output": "[ERREUR] Parler n'est autorisé que le jour."})
            raise ToolException("Parler n'est autorisé que le jour.")
        return input

    def _guarded_vote(self, input):
        if self._phase != "jour":
            self.memory.save_context({"input": "[ERREUR] Voter n'est autorisé que le jour."}, {"output": "[ERREUR] Voter n'est autorisé que le jour."})
            raise ToolException("Voter n'est autorisé que le jour.")
        return input

    def _guarded_vote_to_kill(self, input):
        if self.role != "Werewolf":
            self.memory.save_context({"input": "[ERREUR] Seuls les loups peuvent utiliser vote_to_kill."}, {"output": "[ERREUR] Seuls les loups peuvent utiliser vote_to_kill."})
            return "[ERREUR] Seuls les loups peuvent utiliser vote_to_kill."
        if self._phase != "nuit":
            self.memory.save_context({"input": "[ERREUR] vote_to_kill n'est autorisé que la nuit."}, {"output": "[ERREUR] vote_to_kill n'est autorisé que la nuit."})
            return "[ERREUR] vote_to_kill n'est autorisé que la nuit."
        if self.vote_to_kill_used_turn == self.current_turn:
            self.memory.save_context({"input": "[ERREUR] vote_to_kill déjà utilisé ce tour."}, {"output": "[ERREUR] vote_to_kill déjà utilisé ce tour."})
            return "[ERREUR] Pouvoir déjà utilisé ce tour."
        self.vote_to_kill_used_turn = self.current_turn
        return input

    def _guarded_spy(self, input):
        if self.role != "Seer":
            self.memory.save_context({"input": "[ERREUR] Seule la voyante peut utiliser spy."}, {"output": "[ERREUR] Seule la voyante peut utiliser spy."})
            raise ToolException("Seule la voyante peut utiliser spy.")
        if self._phase != "nuit":
            self.memory.save_context({"input": "[ERREUR] spy n'est autorisé que la nuit."}, {"output": "[ERREUR] spy n'est autorisé que la nuit."})
            raise ToolException("spy n'est autorisé que la nuit.")
        if self.spy_used_turn == self.current_turn:
            self.memory.save_context({"input": "[ERREUR] spy déjà utilisé ce tour."}, {"output": "[ERREUR] spy déjà utilisé ce tour."})
            return "[ERREUR] Pouvoir déjà utilisé ce tour."
        self.spy_used_turn = self.current_turn
        return input

    # Méthodes attendues par le moteur
    def talk(self, game_state):
        self._phase = "jour"
        self.current_turn = getattr(game_state, "turn", 0)
        result = self.agent_executor.invoke({"input": self._build_context(game_state, phase="jour")})
        self._reflect_and_store(result["output"])
        return result["output"]

    def vote(self, game_state):
        self._phase = "jour"
        self.current_turn = getattr(game_state, "turn", 0)
        result = self.agent_executor.invoke({"input": self._build_context(game_state, phase="jour")})
        self._reflect_and_store(result["output"])
        return result["output"]

    def vote_to_kill(self, game_state):
        self._phase = "nuit"
        self.current_turn = getattr(game_state, "turn", 0)
        if self.role != "Werewolf":
            return None
        if self.vote_to_kill_used_turn == self.current_turn:
            return "[ERREUR] Pouvoir déjà utilisé ce tour."
        result = self.agent_executor.invoke({"input": self._build_context(game_state, phase="nuit")})
        self._reflect_and_store(result["output"])
        return result["output"]

    def spy(self, game_state):
        self._phase = "nuit"
        self.current_turn = getattr(game_state, "turn", 0)
        if self.role != "Seer":
            return None
        if self.spy_used_turn == self.current_turn:
            return "[ERREUR] Pouvoir déjà utilisé ce tour."
        result = self.agent_executor.invoke({"input": self._build_context(game_state, phase="nuit")})
        self._reflect_and_store(result["output"])
        return result["output"]

    def _build_context(self, game_state, phase):
        vivants = [a for a in game_state.agents if a.status == "alive"]
        joueurs = ", ".join(f"{a.name} (ID: {a.agent_id})" for a in vivants)
        events = self.memory.buffer[-10:] if hasattr(self.memory, "buffer") else []
        events_str = "\n".join(m.content for m in events) if events else "(aucun événement récent)"
        # Consigne explicite selon la phase et le rôle
        if phase == "nuit":
            if self.role == "Seer":
                consigne = "Consigne : Choisis un joueur à espionner cette nuit (ID ou nom). Tu ne peux le faire qu'une fois par nuit."
            elif self.role == "Werewolf":
                consigne = "Consigne : Vote pour éliminer un joueur cette nuit (ID ou nom, jamais un loup). Tu ne peux voter qu'une fois par tour."
            else:
                consigne = "Consigne : Attends la fin de la nuit, tu n'as pas d'action nocturne."
        else:  # jour
            consigne = "Consigne : Prends la parole publiquement (parle), puis vote pour éliminer un joueur vivant."
        return (
            f"Phase : {phase}\n"
            f"Rôle : {self.role}\n"
            f"Objectif : {self.role}\n"
            f"Joueurs vivants : {joueurs}\n"
            f"Événements récents :\n{events_str}\n"
            f"Actions possibles : parler, voter" +
            (", espionner (si voyante)" if self.role == "Seer" else "") +
            (", vote_to_kill (si loup)" if self.role == "Werewolf" else "") + ".\n"
            f"{consigne}"
        ) 