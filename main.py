from gui_sudoku import SudokuGUI, ButtonInterface
from board import SudokuBoard
from tkinter import *
from gui_plot import PlotStats
import time
import random


# board = SudokuBoard()
# tk = Tk()
# gui = SudokuGUI(tk,board)
# plot = PlotStats()
#
# board.set(0,0,8,True)
# board.set(6,6,8,False)
# gui.sync_board_and_canvas()
#
#
# list_x = list(range(0,50))
# list_y = list(range(0,50))
#
# list_x_name = "name x"
# list_y_name = "name y"
#
# label = "label"
#
# plot.plot_lists(list_x, list_y, list_x_name, list_y_name, "tome")

def rgb(red, green, blue):
    """
    Make a tkinter compatible RGB color.
    """
    return "#%02x%02x%02x" % (red, green, blue)


class SudokuSA(ButtonInterface):
    plot = PlotStats()
    board = object
    cost_global = -1
    costs_row = [-1 for x in range(9)]
    costs_column = [-1 for x in range(9)]
    gui = object
    state = 0
    cost_column_1_new = 0
    cost_row_1_new = 0
    cost_column_2_new = 0
    cost_row_2_new = 0
    diff_cost = 0
    swap_elements = []

    def button_new(self):
        print("button_new")

    def button_big_step(self):
        print("button_big_step")
        self.mainSA(4 + self.state)

    def button_small_step(self):
        print("button_small_step")
        self.mainSA(1)

    def button_solve(self):
        print("button_solve")
        self.gui.coloring = False
        self.mainSA(1000)
        self.gui.coloring = True

    def __init__(self, _sudoku_board):
        assert isinstance(_sudoku_board, SudokuBoard)
        self.board = _sudoku_board
        self.board.set(0, 0, 9, True)
        self.board.set(2, 2, 9)
        self.board.set(3, 3, 8, False)
        self.board.print()
        self.calculate_rows_columns_costs()
        print(self.calculate_cost_values(self.board.get_row_values(0)))
        print(self.calculate_cost_values(self.board.get_column_values(0)))
        print(self.calculate_cost_global())

        points = self.pick_random()
        self.board.set(points[0][0], points[0][1], -1)
        self.board.set(points[1][0], points[1][1], -2)
        pass

    def mainSA(self, steps):


        for x in range(steps):
            # if cost is = sudoku board is correctly filled
            if self.cost_global == 0:
                break

            # 1. pick two elements on random
            if self.state == 0:
                print("state 0")
                self.swap_elements = self.pick_random()
                self.board.set_color(self.swap_elements[0][0], self.swap_elements[0][1], "red")
                self.board.set_color(self.swap_elements[1][0], self.swap_elements[1][1], "red")
                self.gui.sync_board_and_canvas()
                self.state += 1

            # 2. swap elements
            elif self.state == 1:
                print("state 1")
                self.swap(self.swap_elements[0][0], self.swap_elements[0][1], self.swap_elements[1][0], self.swap_elements[1][1])
                self.state += 1
                self.gui.sync_board_and_canvas()

            # 3. calculate cost with new elements
            elif self.state == 2:
                print("state 2")

                # recalculate cost of altered columns and rows
                self.cost_row_1_new = self.calculate_cost_row(self.swap_elements[0][0])
                self.cost_row_2_new = self.calculate_cost_row(self.swap_elements[1][0])
                self.cost_column_1_new = self.calculate_cost_column(self.swap_elements[0][1])
                self.cost_column_2_new = self.calculate_cost_column(self.swap_elements[1][1])

                # calculate difference in old and new cost  ( new cost - old cost )
                self.diff_cost = self.cost_row_1_new - self.costs_row[self.swap_elements[0][0]]
                self.diff_cost += self.cost_row_2_new - self.costs_row[self.swap_elements[1][0]]
                self.diff_cost += self.cost_column_1_new - self.costs_column[self.swap_elements[0][1]]
                self.diff_cost += self.cost_column_2_new - self.costs_column[self.swap_elements[1][1]]

                self.state += 1

            # check if transaction should happen
            elif self.state == 3:
                print("state 3")
                if self.check_transaction(self.diff_cost) is False:
                    self.swap(self.swap_elements[0][0], self.swap_elements[0][1], self.swap_elements[1][0], self.swap_elements[1][1])
                else:
                    self.costs_row[self.swap_elements[0][0]] = self.cost_row_1_new
                    self.costs_row[self.swap_elements[1][0]] = self.cost_row_2_new
                    self.costs_column[self.swap_elements[0][1]] = self.cost_column_1_new
                    self.costs_column[self.swap_elements[1][1]] = self.cost_column_2_new
                    self.cost_global += self.diff_cost

                self.board.set_color(self.swap_elements[0][0], self.swap_elements[0][1], "white")
                self.board.set_color(self.swap_elements[1][0], self.swap_elements[1][1], "white")

                self.state = 0

    def calculate_cost_global(self):
        cost = 0
        for x in range(9):
            cost += self.costs_column[x]
            cost += self.costs_row[x]
        return cost

    def calculate_rows_columns_costs(self):
        for row in range(9):
            self.costs_row[row] = self.calculate_cost_values(self.board.get_row_values(row))

        for column in range(9):
            self.costs_column[column] = self.calculate_cost_values(self.board.get_column_values(column))

    def calculate_cost_values(self, values):
        exist_list = [False for x in range(9)]
        for value in values:
            if value == 0: continue
            exist_list[value-1] = True
        pass

        cost = 0
        for exist in exist_list:
            if exist is False:
                cost += 1

        return cost

    def calculate_cost_row(self, row):
        return self.calculate_cost_values(self.board.get_row_values(row))

    def calculate_cost_column(self, col):
        return self.calculate_cost_values(self.board.get_column_values(col))

    def pick_random(self):
        while True:
            element_1_row = random.randrange(0, 3)
            element_1_column = random.randrange(0, 3)
            element_2_row = random.randrange(0, 3)
            element_2_column = random.randrange(0, 3)
            square_x = random.randrange(0, 3)
            square_y = random.randrange(0, 3)
            element_1_column += square_x * 3
            element_1_row += square_y * 3
            element_2_column += square_x * 3
            element_2_row += square_y * 3

            if element_1_row != element_2_row or element_1_column != element_2_column:
                if self.board.get_locked(element_1_column, element_2_column) is False and \
                                self.board.get_locked(element_2_column, element_2_row) is False:
                    break

        return ((element_1_column, element_1_row), (element_2_column, element_2_row))

    def check_transaction(self, cost_diff):
        return True

    def swap(self, e1_col, e1_row, e2_col, e2_row):
        value_e1 = self.board.get_value(e1_col, e1_row)
        self.board.set(e1_col, e1_row, self.board.get_value(e2_col, e2_row))
        self.board.set(e2_col, e2_row,value_e1)

    def init_board_random(self):
        for x in range(9):
            row = x % 3
            for x in range(3):
                for y in range(3);

        pass


random.seed(time.time())
sudoku_board = SudokuBoard()
gui = SudokuGUI(Tk(), sudoku_board, SudokuSA(sudoku_board))
gui.mainloop()
