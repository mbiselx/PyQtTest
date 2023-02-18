'''
this is where the brains of the game live
'''

import abc
import typing
from random import choice

from .utils import *




class CannotComputeMove(RuntimeError):
    '''the AI cannot come up with next move'''

class AbstractAI(abc.ABC):
    def __init__(self, player: Player = None) -> None:
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
    def player(self, player:Player):
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
        if winning_move is not None : 
            return winning_move

        # check if there's a move that can prevent us from immediately loosing the game
        defensive_move = self._defensive_move(board)
        if defensive_move is not None : 
            return defensive_move

        # getting the center field is a good idea
        c=(board.size)//2
        if board[c,c] == N:
            return Move((c,c), self.player)

        # otherwise, any winnable place will do
        for wincon in board.all_win_conditions(): 
            states=list(field.state for field in wincon)

            # check if we can even make a move in this row/column/diagonal
            if any(state == self.opponent for state in states):
                continue
            try: 
                return Move(wincon[states.index(N)].index, self.player)
            except ValueError :
                continue
            
        # at this point, and spot will do -- we've already lost / stalemated
        for wincon in board.all_win_conditions(): 
            states=list(field.state for field in wincon)
            try: 
                return Move(wincon[states.index(N)].index, self.player)
            except ValueError :
                continue          

        raise CannotComputeMove()

    def _starting_move(self, board:Board) -> Move:
        # the ideal move is in one of the corners
        idc = (0, board.size-1)
        i, j = choice(idc), choice(idc)
        return Move((i, j), self.player)

    def _winning_move(self, board:Board) -> 'Move | None': 
        '''check if it's possible to win in a single move'''

        minimum_occurrences = board.size-1

        # check row/column/diagonal 
        for wincon in board.all_win_conditions(): 
            states=list(field.state for field in wincon)

            # check if we can even make a move in this row/column/diagonal
            if any(self.opponent == state for state in states) :
                continue

            # check if we only need to make a single move  
            if states.count(self.player) >= minimum_occurrences : 
                return Move(wincon[states.index(N)].index, self.player)


    def _defensive_move(self, board:Board) -> 'Move | None': 
        '''check if a defensive move is required'''

        minimum_occurrences = board.size-1

        # check row/column/diagonal 
        for wincon in board.all_win_conditions(): 
            states=list(field.state for field in wincon)

            # check if we can even make a move in this row/column/diagonal
            if all(state != N for state in states) :
                continue

            # check if we only need to make a single move  
            if states.count(self.opponent) >= minimum_occurrences : 
                return Move(wincon[states.index(N)].index, self.player)

