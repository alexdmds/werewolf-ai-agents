from game.game_engine import WerewolfGame
from game.roles import assign_roles

if __name__ == "__main__":
    agents = assign_roles(nb_players=5)
    game = WerewolfGame(agents)
    game.play()
