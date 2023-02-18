
import logging
from typing import Union, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from .utils import *
from .gui_utils import *
from .smorts import *

class AutoTicTacToeGame(TicTacToeGame):
    __depends__ = [
        TicTacToeGame,
        AbstractAI,
    ]

    def __init__(self,
                 parent: Optional[QtWidgets.QWidget] = None,
                 game: Optional[Game] = None, 
                 ai: Optional[AbstractAI] = None,
                 flags: Union[QtCore.Qt.WindowFlags,
                              QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, game, flags)
        self.ai=ai or ExplicitAI()

    # re-implement nextMove
    def nextMove(self) -> 'Move | None':
        '''make the next move'''
        if self.game.current_player == self.ai.player :
            try:
                return self.ai.next_move(self.game)
            except CannotComputeMove:
                self.logger.info("Failed to compute move")
                return None
        else : #real player's turn
            return None
        
    def clearGame(self):
        self.ai.new_game()
        return super().clearGame()