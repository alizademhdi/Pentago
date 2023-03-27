from Board import BoardUtility
import math
import random


class Player:
    def __init__(self, player_piece):
        self.piece = player_piece

    def play(self, board):
        return 0


class RandomPlayer(Player):
    def play(self, board):
        return [random.choice(BoardUtility.get_valid_locations(board)), random.choice(BoardUtility.REGIONS), random.choice(BoardUtility.ROTATES)]


class HumanPlayer(Player):
    def play(self, board):
        move = input("row, col, region, rotation\n")
        move = move.split()
        return [[int(move[0]), int(move[1])], int(move[2]), move[3]]


class MiniMaxPlayer(Player):
    def __init__(self, player_piece, depth=5):
        super().__init__(player_piece)
        self.depth = depth

    @staticmethod
    def minimax(board, depth, piece, alpha, beta, is_max):
        if BoardUtility.is_terminal_state(board) or depth == 0:
            return BoardUtility.score_position(board, piece), None

        value = -100_000_000_000 if is_max == 1 else 100_000_000_000
        locations = BoardUtility.get_valid_locations(board)
        move = [locations[0], 1, 'skip']
        next_piece = 1 if piece == 2 else 1

        for [row, col], region, rotation in zip(locations, BoardUtility.REGIONS, BoardUtility.ROTATES):
            copy_of_board = board.copy()
            BoardUtility.make_move(copy_of_board, row, col, region, rotation, piece)
            new_value = MiniMaxPlayer.minimax(copy_of_board, depth-1, next_piece, alpha, beta, is_max * -1)[0]
            if is_max == 1:
                if new_value >= beta:
                    break
                if new_value > value:
                    value = new_value
                    move = [[row, col], region, rotation]
                alpha = max(alpha, value)

            else:
                if new_value <= alpha:
                    break
                if new_value < value:
                    value = new_value
                    move = [[row, col], region, rotation]
                beta = min(beta, value)
        return value, move


    def play(self, board):
        return MiniMaxPlayer.minimax(board, self.depth, self.piece, -math.inf, math.inf, 1)[1]


class MiniMaxProbPlayer(Player):
    def __init__(self, player_piece, depth=5, prob_stochastic=0.1):
        super().__init__(player_piece)
        self.depth = depth
        self.prob_stochastic = prob_stochastic

    def play(self, board):
        if random.random() <= self.prob_stochastic:
            return [random.choice(BoardUtility.get_valid_locations(board)), random.choice(BoardUtility.REGIONS), random.choice(BoardUtility.ROTATES)]

        return MiniMaxPlayer.minimax(board, self.depth, self.piece, -math.inf, math.inf, 1)[1]

