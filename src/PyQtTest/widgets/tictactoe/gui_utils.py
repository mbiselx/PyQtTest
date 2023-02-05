'''
this is where the face of the game lives
'''

from typing import Union, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQtTest.widgets.tictactoe.utils import *


class TicTacToeField(QtWidgets.QPushButton):
    def __init__(self, index: 'tuple[int, int]',
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__()
        self.index = index

        self.setFlat(True)
        self.setAutoFillBackground(True)

        self._illegal_animation = QtCore.QVariantAnimation(self)
        self._illegal_animation.setStartValue(QtGui.QColor('red'))
        self._illegal_animation.setEndValue(QtGui.QPalette().color(
            QtGui.QPalette.ColorRole.Button))
        self._illegal_animation.setDuration(500)
        self._illegal_animation.valueChanged.connect(self.setColor)

        self._win_animation = QtCore.QVariantAnimation(self)
        self._win_animation.setStartValue(QtGui.QColor('gold'))
        self._win_animation.setEndValue(QtGui.QPalette().color(
            QtGui.QPalette.ColorRole.Button))
        self._win_animation.setDuration(3000)
        self._win_animation.valueChanged.connect(self.setColor)

    def setColor(self, color: QtGui.QColor):
        '''set the button color'''
        p = self.palette()
        p.setColor(p.ColorRole.Button, color)
        self.setPalette(p)

    def illegalMove(self):
        '''an illegal move was made, and the user should receive feedback'''
        self._illegal_animation.stop()
        self.clearFocus()
        self._illegal_animation.start()

    def winningMove(self):
        '''the game has been won'''
        self.clearFocus()
        self._win_animation.start()


class TicTacToeBoard(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(Move)

    __depends__ = [
        TicTacToeField,
        Board,
        Move
    ]

    def __init__(self,
                 board: Board,
                 parent: Optional[QtWidgets.QWidget] = None,
                 flags: Union[QtCore.Qt.WindowFlags,
                              QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        # this is the board we will display
        self.board = board

        self.buttongroup = QtWidgets.QButtonGroup(self)
        self.buttongroup.setExclusive(False)
        self.buttongroup.buttonPressed.connect(self._clicked)

        # we're using a grid layout (obviously)
        self.setLayout(QtWidgets.QGridLayout(self))

        # fill in the grid with buttons
        for row, states in enumerate(self.board.rows()):
            for col, state in enumerate(states):
                w = TicTacToeField((row, col), self)
                self.layout().addWidget(w, row, col)
                self.buttongroup.addButton(w)

    def updateField(self):
        '''update the gui from the board's current state'''
        for btn in self.buttongroup.buttons():
            btn.setText(str(self.board[btn.index]))

    def illegalMove(self, move: Move):
        '''an illegal move was made, and the user should receive feedback'''
        btn: TicTacToeField = self.layout().itemAtPosition(*move.index).widget()
        btn.illegalMove()

    def hasWon(self, moves: 'list[Move]'):
        # this is very annoying, since it breaks the separation of board/game
        for move in moves:
            btn: TicTacToeField = self.layout().itemAtPosition(*move.index).widget()
            btn.winningMove()

    def _clicked(self, button: TicTacToeField):
        '''internal callback on button click'''
        self.clicked.emit(Move(button.index))


class TicTacToeGame(QtWidgets.QFrame):
    __depends__ = [
        TicTacToeBoard,
        Game
    ]

    def __init__(self,
                 parent: Optional[QtWidgets.QWidget] = None,
                 flags: Union[QtCore.Qt.WindowFlags,
                              QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.game = Game()

        # actions
        self._clearAction = QtWidgets.QAction('Clear')
        self._clearAction.triggered.connect(self._clearGame)
        self.addAction(self._clearAction)

        # widgets
        self.fieldWidget = TicTacToeBoard(self.game, self)
        self.fieldWidget.clicked.connect(self._makeGameMove)

        self.clearBtn = QtWidgets.QPushButton('Clear')
        self.clearBtn.clicked.connect(self._clearAction.trigger)

        # do layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.fieldWidget)
        self.layout().addWidget(self.clearBtn)

    def _makeGameMove(self, move: Move):
        try:
            self.game.move(move)
            self.fieldWidget.updateField()
        except Move.IllegalMove:
            self.fieldWidget.illegalMove(move)
            return

        winning_player = self.game.winning()
        if winning_player is not None:
            indices = self.game.winning_moves(winning_player)
            self.fieldWidget.hasWon(indices)

    def _clearGame(self):
        self.game.clear()
        self.fieldWidget.updateField()
