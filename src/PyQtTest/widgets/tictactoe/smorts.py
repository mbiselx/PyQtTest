'''
this is where the brains of the game live
'''

import abc
import typing
import logging
from time import time, time_ns
from random import choice

from .utils import *


class CannotComputeMove(RuntimeError):
    '''the AI cannot come up with next move'''


class AbstractAI(abc.ABC):
    def __init__(self, player: typing.Optional[Player] = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        if player is None:
            self.player = choice(tuple(Player.PLAYER_STATES))
            self.random_player = True
        else:
            self.player = player
            self.random_player = False

    @property
    def player(self) -> Player:
        return self._player

    @player.setter
    def player(self, player: Player):
        if Player.is_player(player):
            self._player = player
            self._opponent = next(player)
        else:
            raise TypeError(f"expected Player, not {type(player)}")

    @property
    def opponent(self) -> Player:
        return self._opponent

    @abc.abstractmethod
    def next_move(self, board: Board) -> Move:
        '''the next move for the player represented by this AI'''
        raise CannotComputeMove()

    def move_callback(self, move: Move):
        '''respond to moves that have been successfully made'''
        pass

    def new_game(self) -> None:
        '''reset the ai to its initial state. '''
        if self.random_player:
            self.player = choice(tuple(Player.PLAYER_STATES))


class ExplicitAI(AbstractAI):
    '''a tic-tac-toe ai using explicit logic'''

    def next_move(self, board: Board) -> Move:
        '''the next move for the player represented by this AI'''

        # edge case
        if board.is_empty():
            return self._starting_move(board)

        # check if there's a move that will immediately win the game
        winning_move = self._winning_move(board)
        if winning_move is not None:
            return winning_move

        # check if there's a move that can prevent us from immediately loosing the game
        defensive_move = self._defensive_move(board)
        if defensive_move is not None:
            return defensive_move

        # getting the center field is a good idea
        c = (board.size)//2
        if board[c, c] == N:
            return Move((c, c), self.player)

        # otherwise, any winnable place will do
        for wincon in board.all_win_conditions():
            states = list(field.state for field in wincon)

            # check if we can even make a move in this row/column/diagonal
            if any(state == self.opponent for state in states):
                continue
            try:
                return Move(wincon[states.index(N)].index, self.player)
            except ValueError:
                continue

        # at this point, and spot will do -- we've already lost / stalemated
        for wincon in board.all_win_conditions():
            states = list(field.state for field in wincon)
            try:
                return Move(wincon[states.index(N)].index, self.player)
            except ValueError:
                continue

        raise CannotComputeMove()

    def _starting_move(self, board: Board) -> Move:
        # the ideal move is in one of the corners
        idc = (0, board.size-1)
        i, j = choice(idc), choice(idc)
        return Move((i, j), self.player)

    def _winning_move(self, board: Board) -> 'Move | None':
        '''check if it's possible to win in a single move'''

        minimum_occurrences = board.size-1

        # check row/column/diagonal
        for wincon in board.all_win_conditions():
            states = list(field.state for field in wincon)

            # check if we can even make a move in this row/column/diagonal
            if any(self.opponent == state for state in states):
                continue

            # check if we only need to make a single move
            if states.count(self.player) >= minimum_occurrences:
                return Move(wincon[states.index(N)].index, self.player)

    def _defensive_move(self, board: Board) -> 'Move | None':
        '''check if a defensive move is required'''

        minimum_occurrences = board.size-1

        # check row/column/diagonal
        for wincon in board.all_win_conditions():
            states = list(field.state for field in wincon)

            # check if we can even make a move in this row/column/diagonal
            if all(state != N for state in states):
                continue

            # check if we only need to make a single move
            if states.count(self.opponent) >= minimum_occurrences:
                return Move(wincon[states.index(N)].index, self.player)


class MoveNode(Move):
    '''making a tree out of a dataclass'''

    @property
    def parent(self) -> 'MoveNode | None':
        '''this node's parent'''
        try:
            return self._parent
        except AttributeError:
            return None

    @parent.setter
    def parent(self, parent: 'MoveNode'):
        self._parent = parent
        parent.register_child(self)

    @property
    def children(self) -> 'list[MoveNode]':
        try:
            return self._children
        except AttributeError:
            return []

    def register_child(self, child: 'MoveNode'):
        '''add a child to this node'''
        child._parent = self
        try:
            self._children.append(child)
        except:
            self._children = [child]

    @property
    def winner(self) -> 'Player | None':
        try:
            return self._winner
        except AttributeError:
            return None

    @winner.setter
    def winner(self, winner: 'Player | None'):
        self._winner = winner

    @property
    def previous_moves(self) -> 'list[MoveNode]':
        '''a list of the moves leading up to and including this move'''
        try:  # cached result
            return self._previous_moves
        except AttributeError:
            self._previous_moves: list[MoveNode] = []
            cur = self
            while cur.parent is not None:  # we don't want the root node
                self._previous_moves.append(cur)
                cur = cur.parent
            return self._previous_moves

    def create_next_moves(self, fields: 'list[Field]', depth: int = 0, branch: int = 0) -> typing.Generator[float, None, float]:
        '''
        Create the child moves for this move.
        yields progress as a fraction
        '''
        if self.player is None:
            raise TypeError("Player cannot be none")
        next_player = next(self.player)

        done = 0
        total = len(fields)
        # print(f"{depth}/{branch}: {total}")
        if depth == 0:
            yield 0.
        for i, field in enumerate(fields):
            new_move = MoveNode(field.index, next_player)
            self.register_child(new_move)

            # check this move:
            g = Game()
            g.apply_moves(new_move.previous_moves)
            new_move.winner = g.winning_player()

            # only deepen the tree if it makes sense
            if new_move.winner is None:
                yield from new_move.create_next_moves(
                    list(f for f in fields if f is not field),
                    depth=depth+1,
                    branch=i)
            done += 1
            if depth == 0:
                yield done/total

        return 1.

    @staticmethod
    def RootNode() -> 'MoveNode':
        '''create the default root node'''
        return MoveNode((-1, -1), O)  # X always starts

    def grow_move_tree(self, board: Board) -> typing.Generator[float, None, float]:
        '''grow the move tree from a root node'''
        yield from self.create_next_moves(board.fields())
        return 1.

    @staticmethod
    def create_move_tree(board: Board) -> 'MoveNode':
        '''create the complete move tree'''
        root = MoveNode((-1, -1), O)  # X always starts
        root.grow_move_tree(board)
        return root


class TreeAI(AbstractAI):
    '''a tic-tac-toe ai using a tree to figure out the best move'''
    # I expect this will be really slow
    # NOTE: on my laptop, this seems to take about a minute...

    def __init__(self, player: typing.Optional[Player] = None,  board: typing.Optional[Board] = None) -> None:
        super().__init__(player)

        self.logger.debug("generating move tree")
        with ProcessTimer() as p:
            self._root_move = MoveNode.RootNode()
            for progress in self._root_move.grow_move_tree(board or Board()):
                self.logger.debug(f"generating: {int(progress*100)}%... ")
            self.logger.info(f"move tree generated in {p.seconds:.2f} seconds")

        # pointer to the current location in the move tree
        self._current_move = self._root_move

    def compute_score(self, node: MoveNode) -> int:
        '''recursively compute a score for a given move'''
        if node.winner is self.player:
            return 1100  # winning is better than losing
        elif node.winner is self.opponent:
            return -1000
        elif len(node.children):
            return min(1000, sum(map(self.compute_score, node.children))//2) - 1
        else:
            return -100

    def next_move(self, board: Board) -> Move:
        '''return the optimal move. does not actually use the board's state'''

        with ProcessTimer() as p:

            # 1. compute scores for all the moves at our disposal
            scores = list(map(self.compute_score, self._current_move.children))

            # 2. best score wins
            best_score = max(scores)
            best_move = self._current_move.children[scores.index(best_score)]

            self.logger.debug(f"move found after {p.milliseconds:.2f} ms")

        return best_move

    def move_callback(self, move: Move):
        '''every time a move is played, go down the tree'''
        # we do this so that moves take less time
        for child in self._current_move.children:
            if child.index == move.index and child.player == move.player:
                self._current_move = child
                break
        else:
            raise CannotComputeMove(move)

    def new_game(self) -> None:
        '''reset the ai's internal stuff'''
        # we don't need to re-create the tree, thankfully
        self._current_move = self._root_move
        return super().new_game()
