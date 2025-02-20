def classFactory(iface):
    from .sudoku_plugin import SudokuPlugin
    return SudokuPlugin(iface)

