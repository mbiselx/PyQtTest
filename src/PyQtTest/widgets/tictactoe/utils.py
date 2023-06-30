'''
this is where the game lives
'''

from time import time_ns
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Generator, List, Callable, overload, Iterable

__all__ = [
    'X', 'O', 'N',
    'State',
    'Player',
    'Field',
    'Board',
    'Move',
    'Game',
    'ProcessTimer',
]


class State:
    '''the only values allowed for a state are `X`, `O` or (space)'''
    ALLOWED_STATES: 'set[State]'
    PLAYER_STATES: 'set[Player]'

    def __init__(self, representation: str) -> None:
        self.__representation = str(representation)

    def __repr__(self) -> str:
        return self.__representation

    @overload
    @staticmethod
    def is_valid(__state: 'State | Any') -> bool: ...

    @overload
    def is_valid(self) -> bool: ...

    def is_valid(self: 'State | Any') -> bool:
        '''check if the given state is a valid state'''
        return self in __class__.ALLOWED_STATES

    @overload
    @staticmethod
    def is_player(__player: 'Player | Any') -> bool: ...

    @overload
    def is_player(self) -> bool: ...

    def is_player(self: 'Player | Any') -> bool:
        '''check if the given player is a valid player'''
        return self in __class__.PLAYER_STATES


class Player(State):
    '''decorator, so that we can differentiate between players and field states'''

    @abstractmethod
    def __next__(self) -> 'Player': ...


# create the allowed Players / States
X = Player('X')
O = Player('O')
N = State(' ')  # None

# now add these to the Player/State classes
State.ALLOWED_STATES = {X, O, N}  # this also sets Player.ALLOWED_STATES
State.PLAYER_STATES = {X, O}  # this also sets Player.PLAYER_STATES
Player.__next__ = lambda self: O if self is X else X


class Field:
    '''represent a single field on the TicTacToe board'''

    def __init__(self, index: 'tuple[int, int]', state: Optional[State] = None) -> None:
        if not isinstance(index, tuple):
            raise TypeError(f"Expected tuple[int, int], not {type(index)!s}")
        if not len(index) == 2:
            raise ValueError(f"Expected tuple of length 2, not {len(index)}")
        if not (isinstance(index[0], int) and isinstance(index[1], int)):
            raise TypeError(
                f"Expected tuple[int, int], not tuple[{type(index[0])!s}, {type(index[1])!s}]")

        self._view_refresh: 'Callable[[], None] | None' = None
        '''callback to refresh gui'''

        self._index = index
        self.state = state or N

    def register_view_refresh(self, view_refresh: 'Callable[[], None] | None'):
        '''register a new function as a view-refresher. register ``None` to remove'''
        self._view_refresh = view_refresh

    def view_refresh(self):
        '''refresh GUI if applicable'''
        if self._view_refresh is not None:
            self._view_refresh()

    @property
    def state(self) -> State:
        '''the current state of the field'''
        return self.__state  # using __ so nobody can 'accidentally' change this

    @state.setter
    def state(self, value: State):
        if not State.is_valid(value):
            raise TypeError(f"State can only be one of {State.ALLOWED_STATES}")
        self.__state = value
        self.view_refresh()

    def clear(self):
        '''clear the field's state'''
        self.__state = N
        self.view_refresh()

    def set(self, state: State):
        '''set the field's state'''
        self.state = state

    def is_empty(self) -> bool:
        return self.state is N

    def __str__(self) -> str:
        return f' {self.state} '  # padded

    def __contains__(self, other: Any) -> bool:
        return self.state == other

    @property
    def index(self) -> 'tuple[int, int]':
        return self._index

    @property
    def row(self) -> int:
        return self._index[0]

    @property
    def column(self) -> int:
        return self._index[1]


class Board:
    '''represent a TicTacToe board'''

    def __init__(self, size: int = 3) -> None:
        self._size = size
        self._fields = [[Field((i, j)) for j in range(size)]
                        for i in range(size)]

    @property
    def size(self) -> int:
        '''size of the board'''
        return self._size

    def fields(self) -> List[Field]:
        '''flattened list of all fields of the board'''
        return sum(self._fields, [])

    def __str__(self) -> str:
        '''print the board to stdout'''
        hsep = '+'.join(self.size*['---']) + '\n'
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

    def rows(self) -> Generator[List[Field], None, None]:
        '''return a row-wise generator containing the fields of the board'''
        return (row for row in self._fields)

    def columns(self) -> Generator[List[Field], None, None]:
        '''return a column-wise generator containing the fields of the board'''
        return (list(f for f in (row[i] for row in self._fields)) for i in range(self._size))

    def diagonals(self) -> Generator[List[Field], None, None]:
        '''return a generator containing the two diagonals of the board'''
        # this is a bit clunky, but i'm doing it this way for symmetry, okay ?
        return (list(self._fields[l(i)][i] for i in range(self._size)) for l in (lambda i: i, lambda i: self.size-i-1))

    def all_win_conditions(self) -> List[List[Field]]:
        '''return a list containing the lists of fields for all win-conditions of the board'''
        return [*self.rows(), *self.columns(), *self.diagonals()]

    def is_empty(self) -> bool:
        '''return whether or not the board is empty'''
        return all(all(f.state == N for f in row) for row in self._fields)

    def is_full(self) -> bool:
        '''return whether or not the board is full'''
        return all(all(f.state != N for f in row) for row in self._fields)

    def free_fields(self) -> List[Field]:
        '''return a list of all free fields'''
        return [f for row in self._fields for f in row if f.state == N]

    def clear(self):
        '''clear the board'''
        for row in self.rows():
            for field in row:
                field.clear()

    def has_won(self, player: Player) -> bool:
        '''check if a given player has won'''
        return any(all(field.state == player for field in wincon) for wincon in self.all_win_conditions())

    def winning_player(self) -> 'Player | None':
        '''get the player currently winning'''
        for player in Player.PLAYER_STATES:
            if self.has_won(player):
                return player
        return None

    def stalemate(self) -> bool:
        '''has a stalemate occurred ?'''
        return self.is_full() and self.winning_player() is None

    def game_over(self) -> bool:
        '''is the game over ?'''
        return self.is_full() or self.winning_player() is not None


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

        # this is placed in a field for gui updating
        self._current_player = Field((-1, -1), initial_player)
        '''the player whose move it is now'''

        self._history: 'list[Move]' = []
        '''the history of the moves played so far'''

    @property
    def current_player(self) -> Player:
        '''the player whose move it is now'''
        if isinstance(self._current_player.state, Player):
            return self._current_player.state
        else:  # this is just here so typehinting stops whining
            return self._initial_player

    @current_player.setter
    def current_player(self, player: Player):
        self._current_player.state = player

    @property
    def next_player(self) -> Player:
        '''the player whose move it will be next turn'''
        return next(self.current_player)

    def find_move(self, __row: int, __column: int) -> Move:
        '''find the move for `index` in history'''
        return next(move for move in self._history if move.index == (__row, __column))

    def apply_move(self, move: Move):
        '''
        Raises Move.IllegalMove on an illegal move.
        '''
        # check if the move is from a valid player
        if not (isinstance(move.player, Player) and move.player.is_player()):
            raise Move.IllegalMove(
                move, f'{move.player} is not a valid player')

        # check if the move is in a valid field
        if self[move.index] is not N:
            raise Move.IllegalMove(
                move, f"Field already set to '{self[move.index]}'")

        # make the move
        self.current_player = move.player
        self[move.index] = move.player

        # append the move to the game 'history'
        self._history.append(move)

    def apply_moves(self, moves: Iterable[Move]):
        for move in moves:
            self.apply_move(move)

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
            if not isinstance(__column, int):
                raise TypeError("require row, column to be of type "
                                f"'int', not {type(__column)}")
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
            player = self.winning_player()
            if player is None:  # still `None` means nobody is winning
                return outlist  # empty list

        for wincon in self.all_win_conditions():
            if all(f.state == player for f in wincon):
                outlist.extend(self.find_move(*f.index) for f in wincon)

        return outlist


class ProcessTimer:
    def __init__(self, callback: Optional[Callable[[int], None]] = None) -> None:
        self.start_time: int = time_ns()
        self.end_time: int = 0
        self.callback: Callable[[int], None] = callback or (lambda i: None)

    @property
    def nanoseconds(self) -> int:
        return time_ns() - self.start_time

    @property
    def microseconds(self) -> float:
        return self.nanoseconds/1e3

    @property
    def milliseconds(self) -> float:
        return self.nanoseconds/1e6

    @property
    def seconds(self) -> float:
        return self.nanoseconds/1e9

    def __enter__(self) -> 'ProcessTimer':
        self.start_time = time_ns()
        return self

    def __exit__(self, *args):
        self.end_time = time_ns()
        self.callback(self.end_time - self.start_time)
