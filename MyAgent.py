from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit, learning_rate=0.001):
        super().__init__(timeLimit)
        self.learning_rate = learning_rate

        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0
        self._depthCount = 0
        self._count = 0

    def findMove(self, state):
        self._count += 1
        actions = self.moveOrder(state)
        print(f"Available actions at root: {actions}")
        if not actions:
            print("No available actions. Ending search.")
            return

        # Defensive: choose first available move by default
        bestMove = actions[0]
        depth = 1
        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1
            print(f'Search depth {depth}')
            best = -float('inf')
            alpha = -float('inf')
            beta = float('inf')
            foundBetterMove = False  # Track if search found a better move

            for a in actions:
                result = state.move(a)
                if not self.timeRemaining():
                    print("Time ran out during move evaluations.")
                    return
                v = self.minPlayer(result, depth-1, alpha, beta)
                if v is None:
                    print("Time ran out during search.")
                    return
                print(f'\tAction {a} value: {v}')
                if v > best:
                    best = v
                    bestMove = a
                    foundBetterMove = True
                alpha = max(alpha, best)

            if not foundBetterMove:
                print("No better move found this depth, using fallback bestMove.")

            self.setMove(bestMove)
            print(f'\tBest value: {best}, Best move: {bestMove}')

            depth += 1

    def maxPlayer(self, state, depth, alpha, beta):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        actions = self.moveOrder(state)
        if not actions:
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = -float('inf')
        for a in actions:
            if not self.timeRemaining():
                return None
            result = state.move(a)
            v = self.minPlayer(result, depth-1, alpha, beta)
            if v is None:
                return None
            best = max(best, v)
            alpha = max(alpha, best)
            if best >= beta:
                break  # beta cutoff
        return best

    def minPlayer(self, state, depth, alpha, beta):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = float('inf')
        for (t, v_tile) in state.possibleTiles():
            if not self.timeRemaining():
                return None
            result = state.addTile(t, v_tile)
            v = self.maxPlayer(result, depth-1, alpha, beta)
            if v is None:
                return None
            best = min(best, v)
            beta = min(beta, best)
            if best <= alpha:
                break  # alpha cutoff
        return best

    def heuristic(self, state):
        return state.getScore()
        
    def moveOrder(self, state):
        return state.actions()

    def stats(self):
        print(f'Average depth: {self._depthCount/self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
