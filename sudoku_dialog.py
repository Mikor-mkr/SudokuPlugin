import os, random
from qgis.PyQt import QtWidgets, QtCore
from qgis.core import QgsMessageLog


def get_cell_style(row, col):
    # Determine border thickness for each side.
    top = "2px" if row % 3 == 0 else "1px"
    left = "2px" if col % 3 == 0 else "1px"
    bottom = "2px" if row == 8 else "1px"
    right = "2px" if col == 8 else "1px"
    style = (
        f"border-top: {top} solid black;"
        f"border-left: {left} solid black;"
        f"border-bottom: {bottom} solid black;"
        f"border-right: {right} solid black;"
        "font-size: 16px;"
        "min-width: 40px; min-height: 40px;"
    )
    return style
class SudokuDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sudoku Game")
        self.resize(400, 450)
        self.cells = {}  # store cells keyed by (row, col)
        self.createBoard()

    def createBoard(self):
        main_layout = QtWidgets.QVBoxLayout()

        # Create three horizontal block layouts.
        for block_row in range(3):
            block_row_layout = QtWidgets.QHBoxLayout()
            for block_col in range(3):
                # Create a grid layout for a 3x3 block.
                block_grid = QtWidgets.QGridLayout()
                block_grid.setSpacing(0)
                for i in range(3):
                    for j in range(3):
                        row = block_row * 3 + i
                        col = block_col * 3 + j
                        cell = QtWidgets.QLineEdit()
                        cell.setMaxLength(1)
                        cell.setAlignment(QtCore.Qt.AlignCenter)
                        cell.setFixedSize(40, 40)
                        cell.setStyleSheet("border: 1px solid gray; font-size: 16px; color: blue;")
                        block_grid.addWidget(cell, i, j)
                        self.cells[(row, col)] = cell

                # Wrap the block grid in a widget with a thicker border.
                block_widget = QtWidgets.QWidget()
                block_widget.setLayout(block_grid)
                block_widget.setStyleSheet("border: 2px solid black;")
                block_row_layout.addWidget(block_widget)

                if block_col < 2:
                    # Add a vertical line between blocks.
                    vline = QtWidgets.QFrame()
                    vline.setFrameShape(QtWidgets.QFrame.VLine)
                    vline.setFrameShadow(QtWidgets.QFrame.Sunken)
                    block_row_layout.addWidget(vline)

            main_layout.addLayout(block_row_layout)

            if block_row < 2:
                # Add a horizontal line between block rows.
                hline = QtWidgets.QFrame()
                hline.setFrameShape(QtWidgets.QFrame.HLine)
                hline.setFrameShadow(QtWidgets.QFrame.Sunken)
                main_layout.addWidget(hline)

        # Add the "Check Solution" button.
        self.check_btn = QtWidgets.QPushButton("Check Solution")
        self.check_btn.clicked.connect(self.checkSolution)
        main_layout.addWidget(self.check_btn)

        self.setLayout(main_layout)

    def fillBoard(self, puzzle, solution):
        self.solution = solution
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                value = puzzle[row][col]
                if value != 0:
                    cell.setText(str(value))
                    cell.setReadOnly(True)
                    cell.setStyleSheet("border: 1px solid gray; font-size: 16px; color: black;")
                else:
                    cell.setText("")
                    cell.setReadOnly(False)
                    cell.setStyleSheet("border: 1px solid gray; font-size: 16px; color: blue;")

    def checkSolution(self):
        error_found = False
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                try:
                    user_val = int(cell.text())
                except ValueError:
                    user_val = 0
                if user_val != self.solution[row][col]:
                    cell.setStyleSheet("border: 1px solid gray; font-size: 16px; background-color: #FFC0CB; color: blue;")
                    error_found = True
                else:
                    if cell.isReadOnly():
                        cell.setStyleSheet("border: 1px solid gray; font-size: 16px; color: black;")
                    else:
                        cell.setStyleSheet("border: 1px solid gray; font-size: 16px; color: blue;")
        if error_found:
            QtWidgets.QMessageBox.warning(self, "Check", "There are mistakes.")
        else:
            QtWidgets.QMessageBox.information(self, "Check", "Solution correct!")