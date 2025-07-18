from game.game_engine import WerewolfGame
from game.roles import assign_roles_langchain

if __name__ == "__main__":
    agents = assign_roles_langchain(nb_players=7)
    game = WerewolfGame(agents)
    game.play()
