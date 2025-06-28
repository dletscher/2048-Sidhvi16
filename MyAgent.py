from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit, learning_rate=0.001):
        super().__init__(timeLimit)
        self.learning_rate = learning_rate  
        self.node_count = 0
        self.parent_count = 0
        self.child_count = 0
        self.depth_count = 0
        self.move_count = 0

    def findMove(self, state):
        self.move_count += 1
        actions = self.moveOrder(state)
        if not actions:
            return
        
        depth = 1
        best_move = actions[0]

        while self.timeRemaining():
            self.depth_count += 1
            self.parent_count += 1
            self.node_count += 1

            best_value = -float('inf')
            current_best_move = best_move

            for action in actions:
                result_state = state.move(action)
                if not self.timeRemaining():
                    return

                value = self.expectiPlayer(result_state, depth - 1)
                if value is None:
                    return
                if value > best_value:
                    best_value = value
                    current_best_move = action

            self.setMove(current_best_move)
            best_move = current_best_move
            depth += 1

    def maxPlayer(self, state, depth):
        self.node_count += 1
        self.child_count += 1

        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)

        actions = self.moveOrder(state)
        if not actions:
            return self.heuristic(state)

        self.parent_count += 1
        best_value = -float('inf')
        for action in actions:
            if not self.timeRemaining():
                return None
            result_state = state.move(action)
            value = self.expectiPlayer(result_state, depth - 1)
            if value is None:
                return None
            best_value = max(best_value, value)

        return best_value

    def expectiPlayer(self, state, depth):
        self.node_count += 1
        self.child_count += 1

        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)

        self.parent_count += 1
        possibilities = state.possibleTiles()
        if not possibilities:
            return self.heuristic(state)

        total_value = 0
        for tile_pos, tile_val in possibilities:
            if not self.timeRemaining():
                return None
            next_state = state.addTile(tile_pos, tile_val)
            result = self.maxPlayer(next_state, depth - 1)
            if result is None:
                return None
            total_value += result

        return total_value / len(possibilities)

    def heuristic(self, state):
        board = [[state.getTile(r, c) for c in range(4)] for r in range(4)]
        flat_tiles = [tile for row in board for tile in row]
        empty_count = flat_tiles.count(0)
        max_tile = max(flat_tiles)

        weights = [
            [32768,16384,8192,4096],
            [256,128,64,32],
            [16,8,4,2],
            [1,1,1,1]
        ]

        # Corner weighting: prefer largest tiles in top-left.
        corner_score = sum(board[r][c] * weights[r][c] for r in range(4) for c in range(4))

        # Empty tiles: more empty spaces are better.
        empty_score = empty_count * 3000

        # Monotonicity: favor boards with rows/columns increasing or decreasing.
        monotonicity_score = 0
        for row in board:
            monotonicity_score += self.isMonotonic(row)
        for col in zip(*board):
            monotonicity_score += self.isMonotonic(col)
        monotonicity_score *= 15000

        # Smoothness: penalize big differences between adjacent tiles.
        smoothness_score = 0
        for r in range(4):
            for c in range(3):
                smoothness_score -= abs(board[r][c] - board[r][c+1])
        for c in range(4):
            for r in range(3):
                smoothness_score -= abs(board[r][c] - board[r+1][c])
        smoothness_score *= 30
        merge_score = 0
        for r in range(4):
            for c in range(3):
                if board[r][c] and board[r][c] == board[r][c+1]:
                    merge_score += 1
        for c in range(4):
            for r in range(3):
                if board[r][c] and board[r][c] == board[r+1][c]:
                    merge_score += 1
        merge_score *= 25000

        return corner_score + empty_score + monotonicity_score + smoothness_score + merge_score

    def isMonotonic(self, line):
        return all(i >= j for i, j in zip(line, line[1:])) or all(i <= j for i, j in zip(line, line[1:]))

    def moveOrder(self, state):
        preferred_order = ['U', 'L', 'R', 'D']
        legal_moves = state.actions()
        return [move for move in preferred_order if move in legal_moves]

    def stats(self):
        avg_depth = self.depth_count / self.move_count if self.move_count else 0
        avg_branching = self.child_count / self.parent_count if self.parent_count else 0
        print(f'Average depth: {avg_depth:.2f}')
        print(f'Branching factor: {avg_branching:.2f}')
