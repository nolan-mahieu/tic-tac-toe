import random

class TicTacToeAI:
    def __init__(self, opponent, level="easy"):
        self.opponent = opponent
        self.level = level

    def make_move(self, board):
        if self.level == "easy":
            return self.easy_move(board)
        elif self.level == "medium":
            return self.medium_move(board)
        elif self.level == "hard":
            return self.hard_move(board)

    def easy_move(self, board):
        available_moves = [i for i, cell in enumerate(board) if cell == " "]
        if available_moves:
            move = random.choice(available_moves)
            return move

    def medium_move(self, board):
        move = self.find_winning_move(board, self.opponent)
        if move is not None:
            return move
        return self.easy_move(board)

    def hard_move(self, board):
        _, move = self.minimax(board, self.opponent, True)
        return move

    def find_winning_move(self, board, player):
        for i in range(len(board)):
            if board[i] == " ":
                new_board = board.copy()
                new_board[i] = player
                if self.check_winner(new_board, player):
                    return i
        return None

    def check_winner(self, board, player):
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in winning_combinations:
            if board[a] == board[b] == board[c] == player:
                return True
        return False

    def minimax(self, board, player, is_maximizing):
        if self.check_winner(board, self.opponent):
            return -1, None
        if self.check_winner(board, self.opponent if player == "X" else "X"):
            return 1, None
        if " " not in board:
            return 0, None

        best_score = float("-inf") if is_maximizing else float("inf")
        best_move = None

        for i in range(len(board)):
            if board[i] == " ":
                new_board = board.copy()
                new_board[i] = player
                score, _ = self.minimax(new_board, "O" if player == "X" else "X", not is_maximizing)
                if is_maximizing:
                    if score > best_score:
                        best_score = score
                        best_move = i
                else:
                    if score < best_score:
                        best_score = score
                        best_move = i

        return best_score, best_move
