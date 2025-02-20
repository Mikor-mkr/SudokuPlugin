import os, random
from qgis.PyQt import QtWidgets, QtCore
from qgis.core import QgsMessageLog


class SudokuCell(QtWidgets.QLineEdit):
    clicked = QtCore.pyqtSignal()
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)



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
        self.cells = {}      # Store cells keyed by (row, col)
        self.cellStyles = {} # Base style for each cell
        self.currentHighlight = None
        self.createBoard()

    def createBoard(self):
        main_layout = QtWidgets.QVBoxLayout()
        # Create three horizontal block layouts.
        for block_row in range(3):
            block_row_layout = QtWidgets.QHBoxLayout()
            for block_col in range(3):
                block_grid = QtWidgets.QGridLayout()
                block_grid.setSpacing(0)
                for i in range(3):
                    for j in range(3):
                        row = block_row * 3 + i
                        col = block_col * 3 + j
                        cell = SudokuCell()
                        cell.setMaxLength(1)
                        cell.setAlignment(QtCore.Qt.AlignCenter)
                        cell.setFixedSize(40, 40)
                        base_style = "border: 1px solid gray; font-size: 16px; color: blue;"
                        cell.setStyleSheet(base_style)
                        # Save the base style for later use.
                        self.cellStyles[(row, col)] = base_style
                        # Connect the click signal to handle highlighting.
                        cell.clicked.connect(lambda r=row, c=col: self.onCellClicked(r, c))
                        block_grid.addWidget(cell, i, j)
                        self.cells[(row, col)] = cell

                block_widget = QtWidgets.QWidget()
                block_widget.setLayout(block_grid)
                block_widget.setStyleSheet("border: 2px solid black;")
                block_row_layout.addWidget(block_widget)
                if block_col < 2:
                    vline = QtWidgets.QFrame()
                    vline.setFrameShape(QtWidgets.QFrame.VLine)
                    vline.setFrameShadow(QtWidgets.QFrame.Sunken)
                    block_row_layout.addWidget(vline)
            main_layout.addLayout(block_row_layout)
            if block_row < 2:
                hline = QtWidgets.QFrame()
                hline.setFrameShape(QtWidgets.QFrame.HLine)
                hline.setFrameShadow(QtWidgets.QFrame.Sunken)
                main_layout.addWidget(hline)
        self.check_btn = QtWidgets.QPushButton("Check Solution")
        self.check_btn.clicked.connect(self.checkSolution)
        self.hint_btn = QtWidgets.QPushButton("Get Hint")
        self.hint_btn.clicked.connect(self.getHint)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.check_btn)
        button_layout.addWidget(self.hint_btn)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def fillBoard(self, puzzle, solution):
        self.solution = solution
        # Clear any previous highlight.
        self.currentHighlight = None
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                value = puzzle[row][col]
                base_style = self.cellStyles[(row, col)]
                if value != 0:
                    cell.setText(str(value))
                    cell.setReadOnly(True)
                    cell.setStyleSheet(base_style + " color: black;")
                else:
                    cell.setText("")
                    cell.setReadOnly(False)
                    cell.setStyleSheet(base_style + " color: blue;")

    def onCellClicked(self, row, col):
        cell = self.cells[(row, col)]
        try:
            clicked_value = int(cell.text())
        except ValueError:
            clicked_value = 0

        # Clear previous highlight if any.
        self.clearHighlights()

        if clicked_value != 0:
            self.highlightCells(clicked_value)
            self.currentHighlight = clicked_value

    def highlightCells(self, number):
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                try:
                    cell_value = int(cell.text())
                except ValueError:
                    cell_value = 0
                base_style = self.cellStyles[(row, col)]
                # If the cell matches the clicked number, add a yellow background.
                if cell_value == number and number != 0:
                    # Preserve existing read-only color if needed.
                    if cell.isReadOnly():
                        cell.setStyleSheet(base_style + " color: black; background-color: yellow;")
                    else:
                        cell.setStyleSheet(base_style + " color: blue; background-color: yellow;")

    def clearHighlights(self):
        # Reset style for every cell according to its current state.
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                base_style = self.cellStyles[(row, col)]
                if cell.isReadOnly():
                    cell.setStyleSheet(base_style + " color: black;")
                else:
                    cell.setStyleSheet(base_style + " color: blue;")

    def checkSolution(self):
        error_found = False
        self.clearHighlights()  # Remove number highlights before checking.
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                try:
                    user_val = int(cell.text())
                except ValueError:
                    user_val = 0
                base_style = self.cellStyles[(row, col)]
                if user_val != self.solution[row][col]:
                    cell.setStyleSheet(base_style + " font-size: 16px; background-color: #FFC0CB; color: blue;")
                    error_found = True
                else:
                    if cell.isReadOnly():
                        cell.setStyleSheet(base_style + " font-size: 16px; color: black;")
                    else:
                        cell.setStyleSheet(base_style + " font-size: 16px; color: blue;")
        if error_found:
            QtWidgets.QMessageBox.warning(self, "Check", "There are mistakes.")
        else:
            QtWidgets.QMessageBox.information(self, "Check", "Solution correct!")

    def getHint(self):
        # Find empty or incorrect cells
        hint_candidates = []
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                try:
                    user_val = int(cell.text())
                except ValueError:
                    user_val = 0
                if user_val != self.solution[row][col]:
                    hint_candidates.append((row, col))
        
        if hint_candidates:
            # Choose a random cell to give hint for
            row, col = random.choice(hint_candidates)
            cell = self.cells[(row, col)]
            correct_value = self.solution[row][col]
            cell.setText(str(correct_value))
            cell.setReadOnly(True)
            base_style = self.cellStyles[(row, col)]
            cell.setStyleSheet(base_style + " color: green;")
        else:
            QtWidgets.QMessageBox.information(self, "Hint", "No hints needed - puzzle is complete!")            