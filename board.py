

class Element:
    value = 0
    locked = False
    color = "white"


class SudokuBoard:
    """
    Data structure representing the board of a Sudoku game.
    """
    grid = [[Element() for x in range(9)] for y in range(9)]
    costs_columns = [Element() for x in range(9)]
    costs_rows = [Element() for x in range(9)]
    cost_global = Element()

    def clear(self):
        self.grid = [[Element() for x in range(9)] for y in range(9)]
        self.costs_columns = [Element() for x in range(9)]
        self.costs_rows = [Element() for x in range(9)]
        self.cost_global = Element()
        for x in range(9):
            self.costs_rows[x].color = "#b1ddff"
            self.costs_columns[x].color = "#b1ddff"
        self.cost_global.color = "#b1ddff"

    def get_row(self, row):
        return self.grid[row]

    def get_cols(self, col):
        return [y[col] for y in self.grid]

    def set(self, col, row, v, lock=False):
        self.grid[row][col].value = v
        self.grid[row][col].locked = lock

    def set_color(self, col, row, color):
        self.grid[row][col].color = color

    def get_value(self, col, row):
        return self.grid[row][col].value

    def get_colour(self, col, row):
        return self.grid[row][col].color

    def get_locked(self, col, row):
        return self.grid[row][col].locked

    def get(self, col, row):
        return self.grid[row][col]

    def get_row_values(self, row):
        row_values = []
        for x in range(9):
            row_values.append(self.grid[row][x].value)
        return row_values

    def get_column_values(self, col):
        column_values = []
        for x in range(9):
            column_values.append(self.grid[x][col].value)
        return column_values

    def print(self):
        row = []
        for x in range(9):
            for y in range(9):
                row.append(self.get_value(x, y))
            print(row)
            row.clear()

    def __init__(self):
        for x in range(9):
            self.costs_rows[x].color = "#b1ddff"
            self.costs_columns[x].color = "#b1ddff"
        self.cost_global.color = "#b1ddff"
