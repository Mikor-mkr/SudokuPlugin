import os, random
from qgis.PyQt import QtWidgets, QtCore
from qgis.core import QgsMessageLog
from .sudoku_dialog import SudokuDialog

# Sudoku puzzle logic functions
def is_valid(board, row, col, num):
    # Check row and column
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    # Check 3x3 sub-grid
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_board(board):
    # Backtracking solver: find the next empty cell and try possible numbers
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                numbers = list(range(1, 10))
                random.shuffle(numbers)
                for num in numbers:
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_board(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def generate_full_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve_board(board)
    return board

def remove_numbers(board, removals=40):
    # Create a copy of the full board and remove numbers to form a puzzle
    puzzle = [row[:] for row in board]
    removed = 0
    while removed < removals:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            removed += 1
    return puzzle

class SudokuPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dialog = None

    def initGui(self):
        self.action = QtWidgets.QAction("Sudoku Game", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Sudoku Plugin", self.action)

    def unload(self):
        self.iface.removePluginMenu("Sudoku Plugin", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.dialog:
            self.dialog = SudokuDialog()
        full_board = generate_full_board()
        puzzle = remove_numbers(full_board, removals=40)
        # Provide both puzzle and solution to the dialog
        self.dialog.fillBoard(puzzle, full_board)
        self.dialog.show()