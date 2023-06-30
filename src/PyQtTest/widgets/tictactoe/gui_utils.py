'''
this is where the face of the game lives
'''

import logging
from typing import Union, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQtTest.widgets.tictactoe.utils import *


class TicTacToeField(QtWidgets.QAbstractButton):
    __depends__ = [State, Player]

    FREE_COLOR = QtGui.QColor('white')
    OCCUPIED_COLOR = QtGui.QColor('lightGray')
    FORBID_COLOR = QtGui.QColor('red')
    STALEMATE_COLOR = QtGui.QColor('tomato')
    SUCCESS_COLOR = QtGui.QColor('gold')
    WIN_COLOR = QtGui.QColor('beige')

    def __init__(self, field: Field,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self._field = field
        self._field.register_view_refresh(self._update)
        self._readonly = False

        self._illegal_animation = QtCore.QVariantAnimation(self)
        self._illegal_animation.setStartValue(self.FORBID_COLOR)
        self._illegal_animation.setEndValue(self.OCCUPIED_COLOR)
        self._illegal_animation.setDuration(250)
        self._illegal_animation.valueChanged.connect(self.setColor)

        self._stalemate_animation = QtCore.QVariantAnimation(self)
        self._stalemate_animation.setStartValue(self.FORBID_COLOR)
        self._stalemate_animation.setEndValue(self.STALEMATE_COLOR)
        self._stalemate_animation.setDuration(1500)
        self._stalemate_animation.valueChanged.connect(self.setColor)

        self._win_animation = QtCore.QVariantAnimation(self)
        self._win_animation.setStartValue(self.SUCCESS_COLOR)
        self._win_animation.setEndValue(self.WIN_COLOR)
        self._win_animation.setDuration(3000)
        self._win_animation.valueChanged.connect(self.setColor)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )

    def index(self) -> 'tuple[int, int]':
        return self._field.index

    def state(self) -> 'State':
        return self._field.state

    def readOnly(self) -> bool:
        return self._readonly

    def setReadOnly(self, readonly):
        self._readonly = readonly

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(50, 50)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, a0: int) -> int:
        return a0

    def setColor(self, color: QtGui.QColor):
        '''set the button color'''
        p = self.palette()
        p.setColor(p.ColorRole.Base, color)
        self.setPalette(p)
        self.update()

    def _stopAnimations(self):
        self._illegal_animation.stop()
        self._win_animation.stop()
        self._stalemate_animation.stop()

    def illegalMove(self):
        '''an illegal move was made, and the user should receive feedback'''
        self._stopAnimations()
        self.clearFocus()
        self._illegal_animation.start()

    def winningMove(self):
        '''the game has been won'''
        self._stopAnimations()
        self.clearFocus()
        self._win_animation.start()

    def setStalemate(self):
        self._stopAnimations()
        self._stalemate_animation.start()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._readonly:
            event.ignore()
        else:
            return super().mousePressEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        # adapt the font to current size
        f = self.font()
        f.setPixelSize(int(0.8*self.contentsRect().height()))
        self.setFont(f)
        return super().resizeEvent(event)

    def _update(self) -> None:
        self._stopAnimations()
        if self._field.is_empty():
            self.setColor(self.FREE_COLOR)
        else:
            self.setColor(self.OCCUPIED_COLOR)
        return self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        '''draw the field'''

        rect = self.rect()
        text = str(self._field.state)
        trect = self.fontMetrics().tightBoundingRect(text)
        trect.moveCenter(rect.center())

        with QtGui.QPainter(self) as p:
            p: QtGui.QPainter

            # draw background :
            p.setBrush(self.palette().base())
            p.drawRect(rect)

            # draw the current text :
            p.drawText(trect.bottomLeft(), text)


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
        self.board: Board = board
        self._game_over: bool = False

        self.buttongroup = QtWidgets.QButtonGroup(self)
        self.buttongroup.setExclusive(False)
        self.buttongroup.buttonPressed.connect(self._clicked)

        # we're using a grid layout (obviously)
        self._layout = QtWidgets.QGridLayout(self)
        self.setLayout(self._layout)

        # fill in the grid with buttons
        for row in self.board.rows():
            for field in row:
                w = TicTacToeField(field, parent=self)
                self._layout.addWidget(w, field.row, field.column)
                self.buttongroup.addButton(w)

    def hasHeightForWidth(self) -> bool:
        '''make sure the fields stay square'''
        return True

    def heightForWidth(self, a0: int) -> int:
        '''make sure the fields stay square'''
        return a0

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        '''make sure the fields stay square'''
        self.setGeometry(self.x(), self.y(),
                         min(self.height(), self.width()),
                         min(self.height(), self.width()))

    def illegalMove(self, move: Move):
        '''an illegal move was made, and the user should receive feedback'''
        btn: TicTacToeField = self._layout.itemAtPosition(*move.index).widget()
        btn.illegalMove()

    def hasWon(self, moves: 'list[Move]'):
        '''highlight the moves which have won the game'''
        # this is very annoying, since it breaks the separation of board/game
        self._game_over = True
        for move in moves:
            btn: TicTacToeField = self._layout.itemAtPosition(
                *move.index).widget()
            btn.winningMove()

    def hasStalemated(self):
        self._game_over = True
        for btn in self.buttongroup.buttons():
            btn.setStalemate()

    def _clicked(self, button: TicTacToeField):
        '''internal callback on button click'''
        if not self._game_over:
            self.clicked.emit(Move(button.index()))

    def clearBoard(self):
        '''restart the game'''
        self._game_over = False
        self.board.clear()


class TicTacToeGame(QtWidgets.QFrame):
    '''basic structure of the games'''
    moveFinished = QtCore.pyqtSignal()
    winningPlayer = QtCore.pyqtSignal(Player)
    stalemate = QtCore.pyqtSignal()

    __depends__ = [
        TicTacToeField,
        TicTacToeBoard,
        Game
    ]

    def __init__(self,
                 parent: Optional[QtWidgets.QWidget] = None,
                 game: Optional[Game] = None,
                 flags: Union[QtCore.Qt.WindowFlags,
                              QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.game = game or Game()

        # actions
        self._clearAction = QtWidgets.QAction('&Clear')
        self._clearAction.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_LineEditClearButton))
        self._clearAction.triggered.connect(self.clearGame)
        self.addAction(self._clearAction)

        # widgets
        self.currentPlayer = TicTacToeField(
            self.game._current_player, parent=self)
        self.currentPlayer.setReadOnly(True)
        self.currentPlayer.setMaximumSize(QtCore.QSize(50, 50))
        self.stalemate.connect(self.game._current_player.clear)
        self.winningPlayer.connect(self.game._current_player.set)

        self.fieldWidget = TicTacToeBoard(self.game, self)
        self.fieldWidget.clicked.connect(self._applyMove)
        self.stalemate.connect(self.fieldWidget.hasStalemated)
        self.winningPlayer.connect(
            lambda p: self.fieldWidget.hasWon(self.game.winning_moves(p)))

        self.clearBtn = QtWidgets.QPushButton(self._clearAction.text())
        self.clearBtn.setIcon(self._clearAction.icon())
        self.clearBtn.clicked.connect(self._clearAction.trigger)

        self.moveFinished.connect(self._autoNextMove)
        # immediately do auto-move
        QtCore.QTimer.singleShot(1, self._autoNextMove)

        # do layout
        topBar = QtWidgets.QHBoxLayout()
        topBar.addWidget(QtWidgets.QLabel("Current Player : "))
        topBar.addWidget(self.currentPlayer)
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(topBar)
        layout.addWidget(self.fieldWidget)
        layout.addWidget(self.clearBtn)
        self.setLayout(layout)

    def clearGame(self):
        self.fieldWidget.clearBoard()
        self.moveFinished.emit()

    def nextMove(self) -> 'Move | None':
        '''make the next move'''
        return None

    def moveApplied(self, move: Move):
        '''a move has been successfully applied'''
        pass

    def _autoNextMove(self):
        next_move = self.nextMove()
        if next_move is not None:
            self._applyMove(next_move)

    def _applyMove(self, move: Move):
        if self.applyMove(move) and not self.evaluateGame():
            self.moveFinished.emit()

    def applyMove(self, move: Move) -> bool:
        '''attempt to apply a move. return success'''
        try:
            self.game.move(move)
            self.moveApplied(move)
            return True
        except Move.IllegalMove:
            self.fieldWidget.illegalMove(move)
            return False

    def evaluateGame(self) -> bool:
        '''return 'game over' status'''
        winning_player = self.game.winning_player()
        if winning_player is not None:
            self.logger.debug(f"{winning_player} has won")
            self.winningPlayer.emit(winning_player)
            return True
        elif self.game.is_full():
            self.logger.debug("stalemate detected")
            self.stalemate.emit()
            return True
        else:
            return False  # normal game round
