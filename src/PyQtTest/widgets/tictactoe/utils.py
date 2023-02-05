'''
this is where the game lives
'''

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Generator, List, overload

__all__ = [
    'X', 'O',
    'Field',
    'Board',
    'Move',
    'Game'
]


class State:
    '''the only values allowed for a state are `X`, `O` or (space)'''
    ALLOWED_STATES: 'set[State]'
    PLAYER_STATES: 'set[State]'

    def __init__(self, representation: str) -> None:
        self.__representation = str(representation)

    def __repr__(self) -> str:
        return self.__representation

    def is_valid(state: 'State | Any') -> bool:
        '''check if the given state is a valid state'''
        return state in __class__.ALLOWED_STATES

    def is_player(state: 'State | Any') -> bool:
        '''check if the given state is a valid player'''
        return state in __class__.PLAYER_STATES

    @abstractmethod
    def __next__(self) -> 'State':
        '''get alternating states'''  # implemented later
        pass


class Player(State):
    '''decorator, so that we can differentiate between players and field states'''
    pass


# create the allowed Players / States
X = Player('X')
O = Player('O')
N = State(' ')  # None

# now add these to the Player/State classes
State.ALLOWED_STATES = {X, O, N}  # this also sets Player.ALLOWED_STATES
State.PLAYER_STATES = {X, O}  # this also sets Player.PLAYER_STATES
State.__next__ = lambda s: O if s is X else X


class Field:
    '''represent a single field on the TicTacToe board'''

    def __init__(self, state: Optional[State] = None) -> None:
        self.state = state or N

    @property
    def state(self) -> State:
        '''the current state of the field'''
        return self.__state  # using __ so nobody can 'accidentally' change this

    @state.setter
    def state(self, value: State):
        if not State.is_valid(value):
            raise TypeError(f"State can only be one of {State.ALLOWED_STATES}")
        self.__state = value

    def clear(self):
        self.__state = N

    def __str__(self) -> str:
        return f' {self.state} '  # padded


class Board:
    '''represent a TicTacToe board'''

    def __init__(self, size: int = 3) -> None:
        self._size = size
        self._fields = [[Field() for i in range(size)] for i in range(size)]

    @property
    def size(self) -> int:
        return self._size

    def __str__(self) -> str:
        '''print the board to stdout'''
        hsep = '+'.join(self.size*[len(str(Field()))*'-']) + '\n'
        rows = ('|'.join(map(str, row)) + '\n' for row in self._fields)
        return hsep.join(rows)

    def __getitem__(self, __index: 'tuple[int, int]') -> State:
        if not isinstance(__index, (tuple, list)):
            raise TypeError('indices must be a tuple or list')
        if not len(__index) == 2:
            raise ValueError(f'expeced 2 indices -- got {len(__index)}')
        return self._fields[__index[0]][__index[1]].state

    def __setitem__(self, __index: 'tuple[int, int]', __state: State):
        '''this will raise a TypeError if state is not a valid `State`'''
        if not isinstance(__index, (tuple, list)):
            raise TypeError('indices must be a tuple or list')
        if not len(__index) == 2:
            raise ValueError(f'expeced 2 indices -- got {len(__index)}')
        self._fields[__index[0]][__index[1]].state = __state

    def rows(self) -> Generator[List[State], None, None]:
        '''return a row-wise generator containing the states of the fields'''
        return (list(f.state for f in row) for row in self._fields)

    def columns(self) -> Generator[List[State], None, None]:
        '''return a column-wise generator containing the states of the fields'''
        return (list(f.state for f in (row[i] for row in self._fields)) for i in range(self._size))

    def diagonals(self) -> Generator[List[State], None, None]:
        '''return a generator containing the two diagonals of the board'''
        # this is a bit clunky, but i'm doing it this way for symmetry, okay ?
        return (list(self[f(i), i] for i in range(self._size)) for f in (lambda i: i, lambda i: self.size-i-1))

    def clear(self):
        '''clear the board'''
        for row in self._fields:
            for field in row:
                field.clear()

    def has_won(self, player: Player) -> bool:
        '''check if a given player has won'''
        # check rows :
        if any(all(state == player for state in row) for row in self.rows()):
            return True
        # check columns :
        if any(all(state == player for state in col) for col in self.columns()):
            return True
        # check diagonals :
        if any(all(state == player for state in diag) for diag in self.diagonals()):
            return True
        return False

    def winning(self) -> 'Player | None':
        '''get the player currently winning'''
        for player in Player.PLAYER_STATES:
            if self.has_won(player):
                return player
        return None


@dataclass
class Move:
    '''represent a single move of a TicTacToe game'''
    index: 'tuple[int, int]'
    '''the index of the field the move was played in'''
    player: Optional[Player] = None
    '''the player who played the move'''

    class IllegalMove(RuntimeError):
        '''Illegal game move was made'''
        pass


class Game(Board):
    '''a game, consisting of a board, and the current player'''

    def __init__(self, initial_player: Player = X, size: int = 3) -> None:
        super().__init__(size=size)
        self._initial_player = initial_player  # keep this reference for when we reset

        self.current_player = initial_player
        '''the player whose move it is now'''

        self._history: 'list[Move]' = []
        '''the history of the moves played so far'''

    @property
    def next_player(self) -> Player:
        '''the player whose move it will be next turn'''
        return next(self.current_player)

    def find_move(self, *index: 'tuple[int, int]') -> Move:
        '''find the move for `index` in history'''
        return next(move for move in self._history if move.index == index)

    def apply_move(self, move: Move):
        '''
        Raises Move.IllegalMove on an illegal move.
        '''
        # check if the move is from a valid player
        if not Player.is_player(move.player):
            raise Move.IllegalMove(move, f'{move.player} is not a player')

        # check if the move is in a valid field
        if self[move.index] is not N:
            raise Move.IllegalMove(
                move, f"Field already set to '{self[move.index]}'")

        # make the move
        self.current_player = move.player
        self[move.index] = move.player

        # append the move to the game 'history'
        self._history.append(move)

    @overload
    def move(self, __move: Move) -> None: ...

    @overload
    def move(self, __row: int, __column: int,
             player: Optional[Player] = None) -> None: ...

    def move(self,
             __row_or_move: 'int | Move',
             __column: 'int | None' = None,
             player: 'Player | None' = None):
        '''
        Play a move of the game as the current player, alternating after every move.
        If a player is specified, play the move as that player instead.

        Raises Move.IllegalMove on an illegal move.
        '''

        # deal with function overload
        if isinstance(__row_or_move, Move):
            move = __row_or_move
            if move.player is None:
                move.player = self.current_player
        else:
            move = Move((__row_or_move, __column),
                        player or self.current_player)

        # apply the move
        self.apply_move(move)

        # go to next player
        self.current_player = self.next_player

    def undo_move(self, move: Move):
        '''
        Undo a given move.

        Raises Move.IllegalMove if the move is not in the game's history.
        '''

        # assume there are only legal moves in the game history
        if not move in self._history:
            raise Move.IllegalMove(move, 'not in game history')

        # undo the move
        self[move.index] = N

        # remove the move from game 'history'
        self._history.remove(move)

    def undo(self):
        '''Undo the last move. Raise an exception if history is empty'''
        self.undo_move(self._history[-1])

    def clear(self):
        self._history = []
        self.current_player = self._initial_player
        return super().clear()

    def winning_moves(self, player: Optional[Player] = None) -> 'list[Move]':
        '''
        Return the field indices which have led to a player winning.
        Assumption : a player has won.
        '''
        outlist = []

        if player is None:
            player = self.winning()
            if player is None:  # still `None` means nobody is winning
                return outlist  # empty list

        for r, row in enumerate(self.rows()):
            if all(f == player for f in row):
                outlist.extend(self.find_move(r, c) for c in range(self.size))

        for c, col in enumerate(self.columns()):
            if all(f == player for f in col):
                outlist.extend(self.find_move(r, c) for r in range(self.size))

        # ughhh the diagonals are so annoying
        descending, ascending = self.diagonals()
        if all(f == player for f in descending):
            outlist.extend(self.find_move(i, i) for i in range(self.size))
        if all(f == player for f in ascending):
            outlist.extend(self.find_move(self.size-1-i, i)
                           for i in range(self.size))

        return outlist
