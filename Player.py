from Board import BoardUtility
import math
import random

ROWS = 6
COLS = 6

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

class Score:
    @staticmethod
    def count_edge(game_board, piece):
        count = 0

        for c in range(COLS):
            if game_board[0][c] == piece:
                count += 1
            if game_board[ROWS-1][c] == piece:
                count += 1

        for r in range(ROWS):
            if game_board[r][0] == piece:
                count += 1
            if game_board[r][COLS-1] == piece:
                count += 1

        return count

    @staticmethod
    def count_center(game_board, piece):
        count = 0

        for c in range(2, COLS-2):
            for r in range(2, ROWS-2):
                if game_board[r][c] == piece:
                    count += 1

        return count

    @staticmethod
    def count_corner(game_board, piece):
        count = 0

        if game_board[0][0] == piece:
            count += 1
        if game_board[0][COLS-1] == piece:
            count += 1
        if game_board[ROWS-1][0] == piece:
            count += 1
        if game_board[ROWS-1][COLS-1] == piece:
            count += 1

        return count

    @staticmethod
    def calculate_value_in_line(line, piece):
        opposite_piece = 1 if piece == 2 else 2

        empty = line.count(0)
        own = line.count(piece)
        opposite = line.count(opposite_piece)

        count_4 = 0
        for i in range(len(line)-3):
            if line[i] == line[i+1] == line[i+2] == line[i+3] == piece:
                count_4 += 1

        if count_4 > 0 and empty >= 1:
            return 10000

        if own == 4 and empty >= 1:
            return 1000

        if opposite == 4 and empty >= 1:
            return -5000

        value = 0
        count_3 = 0
        for i in range(len(line)-2):
            if line[i] == line[i+1] == line[i+2] == piece:
                count_3 += 1
        if count_3 > 0 and empty >= 2:
            value += 50

        if opposite >=3:
            value -= 30

        count_2 = 0
        for i in range(len(line)-1):
            if line[i] == line[i+1] == piece:
                count_2 += 1
        if count_2 > 0 and empty >= 3:
            value += 30

        return value

    @staticmethod
    def calculate_value(game_board, piece):
        value = 0
        for r in range(ROWS):
            row = [i for i in list(game_board[r,:])]
            for c in range(COLS-4):
                line = row[c:c+5]
                value += Score.calculate_value_in_line(line, piece)

        for c in range(COLS):
            column = [i for i in list(game_board[:,c])]
            for r in range(ROWS-4):
                line = column[r:r+5]
                value += Score.calculate_value_in_line(line, piece)

        for c in range(COLS-4):
            for r in range(ROWS-4):
                line = [game_board[r+i][c+i] for i in range(5)]
                value += Score.calculate_value_in_line(line, piece)

        for c in range(COLS-4):
            for r in range(ROWS-4):
                line = [game_board[r+3-i][c+i] for i in range(5)]
                value += Score.calculate_value_in_line(line, piece)

        value += Score.count_edge(game_board, piece) * 10 + Score.count_center(game_board, piece) * 5 + Score.count_corner(game_board, piece) * 20

        return value



    @staticmethod
    def score_position(game_board, piece):
        """
        compute the game board score for a given piece.
        you can change this function to use a better heuristic for improvement.
        """
        value = 0
        if BoardUtility.has_player_won(game_board, piece):
            return 100_000_000_000  # player has won the game give very large score
        if BoardUtility.has_player_won(game_board, 1 if piece == 2 else 2):
            return -100_000_000_000  # player has lost the game give very large negative score


        value += Score.calculate_value(game_board, piece)

        for region in BoardUtility.REGIONS:
            for rotate in ["clockwise", "anticlockwise"]:
                b = game_board.copy()
                BoardUtility.rotate_region(b, region, rotate)
                value += Score.calculate_value(b, piece)
                if BoardUtility.has_player_won(b, piece):
                    return 100_000_000_000
                if BoardUtility.has_player_won(b, 1 if piece == 2 else 2):
                    return -100_000_000_000

        return value

class MiniMaxPlayer(Player):
    def __init__(self, player_piece, depth=5):
        super().__init__(player_piece)
        self.depth = depth

    @staticmethod
    def minimax(board, depth, piece, alpha, beta, is_max):
        if BoardUtility.is_terminal_state(board) or depth == 0:
            return Score.score_position(board, piece), None

        value = -100_000_000_000 if is_max == 1 else 100_000_000_000
        locations = BoardUtility.get_valid_locations(board)
        move = [locations[0], 1, 'skip']
        next_piece = 1 if piece == 2 else 1

        for [row, col], region, rotation in zip(locations, BoardUtility.REGIONS, BoardUtility.ROTATES):
            copy_of_board = board.copy()
            BoardUtility.make_move(copy_of_board, row, col, region, rotation, piece)
            new_value = MiniMaxPlayer.minimax(copy_of_board, depth-1, next_piece, alpha, beta, is_max * -1)[0]
            if is_max == 1:
                if new_value > beta:
                    break
                if new_value > value:
                    value = new_value
                    move = [[row, col], region, rotation]
                alpha = max(alpha, value)

            else:
                if new_value < alpha:
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


    @staticmethod
    def minimax_prob(board, depth, piece, alpha, beta, is_max, prob):
        if BoardUtility.is_terminal_state(board) or depth == 0:
            return Score.score_position(board, piece), None

        value = -100_000_000_000 if is_max == 1 else 100_000_000_000
        locations = BoardUtility.get_valid_locations(board)
        move = [locations[0], 1, 'skip']
        next_piece = 1 if piece == 2 else 1

        max_choices = []

        for [row, col], region, rotation in zip(locations, BoardUtility.REGIONS, BoardUtility.ROTATES):
            copy_of_board = board.copy()
            BoardUtility.make_move(copy_of_board, row, col, region, rotation, piece)
            new_value = MiniMaxPlayer.minimax(copy_of_board, depth-1, next_piece, alpha, beta, is_max * -1)[0]
            if is_max == 1:
                if new_value > beta:
                    break
                if new_value > value:
                    value = new_value
                    move = [[row, col], region, rotation]
                alpha = max(alpha, value)
                max_choices.append([value, move])

            else:
                if new_value < alpha:
                    break
                if new_value < value:
                    value = new_value
                    move = [[row, col], region, rotation]
                beta = min(beta, value)

        if is_max == 1 and random.random() <= prob:
            return random.choice(max_choices)

        return value, move

    def play(self, board):
        return MiniMaxProbPlayer.minimax_prob(board, self.depth, self.piece, -math.inf, math.inf, 1, self.prob_stochastic)[1]

