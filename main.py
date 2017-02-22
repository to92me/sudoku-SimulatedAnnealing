from gui_sudoku import SudokuGUI, ButtonInterface
from board import SudokuBoard
from tkinter import *
from gui_plot import PlotStats
import time
import random
from numpy.random import choice as choice_numpy

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
    board = object
    gui = object
    state = -1

    plot_cost = object
    plot_temperature = object

    cost_column_1_new = 0
    cost_row_1_new = 0
    cost_column_2_new = 0
    cost_row_2_new = 0

    cost_row_1_old = 0
    cost_row_2_old = 0
    cost_column_1_old = 0
    cost_column_2_old = 0

    diff_cost = 0
    swap_elements = []

    reheat = 0
    reheat_limit = 500
    temperature_reheat = 80
    temperature = 99
    cooling_rate = 0.99


    def button_big_step(self):
        self.mainSA(3 + (3 - self.state))

    def button_small_step(self):
        self.mainSA(1)

    def button_solve(self):
        self.mainSA(3-self.state)
        self.gui.sync_board_and_canvas()
        self.gui.gui_update = False
        for x in range(10000000):
            if self.board.cost_global.value != 0:
                self.mainSA(3)
            else:
                break
        self.gui.gui_update = True
        self.gui.sync_board_and_canvas()

    def button_plot_cost(self):
        self.plot_cost.plot_value_x_time_y()

    def button_plot_temp(self):
        self.plot_temperature.plot_value_x_time_y()

    def __init__(self, _sudoku_board):
        assert isinstance(_sudoku_board, SudokuBoard)
        self.board = _sudoku_board
        self.plot_cost = PlotStats()
        self.plot_temperature = PlotStats()
        self.calculate_rows_columns_costs()
        self.board.cost_global.value = self.calculate_cost_global()
        self.plot_temperature.y_label = "temperature"
        self.plot_temperature.legend_label = "temperature"
        self.plot_temperature.plot_label = "Sudoku Simulated Annealing"
        self.plot_cost.y_label = "cost"
        self.plot_cost.legend_label = "global cost"
        self.plot_cost.plot_label = "Sudoku Simulated Annealing"
        self.plot_cost.color = 'r'


    def mainSA(self, steps):


        for x in range(steps):
            # if cost is = sudoku board is correctly filled
            if self.board.cost_global.value == 0:
                print("DONE")
                return
            else:
                pass

            if self.state == -1:
                self.init_board_random()
                self.calculate_rows_columns_costs()
                self.board.cost_global.value = self.calculate_cost_global()
                self.gui.sync_board_and_canvas()
                self.state += 1
                self.plot_cost.add_x(self.board.cost_global.value)
                self.plot_temperature.add_x(self.temperature)
                return

            # 1. pick two elements on random
            if self.state == 0:
                self.swap_elements = self.pick_random()
                self.board.set_color(self.swap_elements[0][0], self.swap_elements[0][1], "red")
                self.board.set_color(self.swap_elements[1][0], self.swap_elements[1][1], "red")
                self.gui.sync_board_and_canvas()
                self.state += 1

            # 2. swap elements
            elif self.state == 1:
                self.swap(self.swap_elements[0][0], self.swap_elements[0][1], self.swap_elements[1][0], self.swap_elements[1][1])
                self.color_altered_costs(True)
                self.gui.sync_board_and_canvas()
                self.state += 1

                self.cost_row_1_old = self.board.costs_rows[self.swap_elements[0][1]].value
                self.cost_row_2_old = self.board.costs_rows[self.swap_elements[1][1]].value
                self.cost_column_1_old = self.board.costs_columns[self.swap_elements[0][0]].value
                self.cost_column_2_old = self.board.costs_columns[self.swap_elements[1][0]].value

                # recalculate cost of altered columns and rows
                self.board.costs_rows[self.swap_elements[0][1]].value = self.calculate_cost_row(self.swap_elements[0][1])
                self.board.costs_rows[self.swap_elements[1][1]].value = self.calculate_cost_row(self.swap_elements[1][1])
                self.board.costs_columns[self.swap_elements[0][0]].value = self.calculate_cost_column(self.swap_elements[0][0])
                self.board.costs_columns[self.swap_elements[1][0]].value = self.calculate_cost_column(self.swap_elements[1][0])

                # calculate difference in old and new cost  ( new cost - old cost )
                self.diff_cost = self.board.costs_rows[self.swap_elements[0][1]].value - self.cost_row_1_old
                self.diff_cost += self.board.costs_rows[self.swap_elements[1][1]].value - self.cost_row_2_old
                self.diff_cost += self.board.costs_columns[self.swap_elements[0][0]].value - self.cost_column_1_old
                self.diff_cost += self.board.costs_columns[self.swap_elements[1][0]].value - self.cost_column_2_old

                self.gui.sync_board_and_canvas()

            # check if transaction should happen
            elif self.state == 2:
                if self.check_transaction(self.diff_cost) == False:
                    self.swap(self.swap_elements[0][0], self.swap_elements[0][1], self.swap_elements[1][0], self.swap_elements[1][1])
                    self.board.costs_rows[self.swap_elements[0][1]].value = self.cost_row_1_old
                    self.board.costs_rows[self.swap_elements[1][1]].value = self.cost_row_2_old
                    self.board.costs_columns[self.swap_elements[0][0]].value = self.cost_column_1_old
                    self.board.costs_columns[self.swap_elements[1][0]].value = self.cost_column_2_old

                else:
                    self.board.cost_global.value += self.diff_cost
                    assert self.board.cost_global.value == self.calculate_cost_global()

                self.gui.sync_board_and_canvas()

                self.state += 1

            elif self.state == 3:
                self.board.set_color(self.swap_elements[0][0], self.swap_elements[0][1], "white")
                self.board.set_color(self.swap_elements[1][0], self.swap_elements[1][1], "white")
                self.color_altered_costs(False)

                self.gui.sync_board_and_canvas()

                self.state = 0

        self.plot_cost.add_x(self.board.cost_global.value)
        self.plot_temperature.add_x(self.temperature)


    def calculate_cost_global(self):
        cost = 0
        for x in range(9):
            cost += self.board.costs_columns[x].value
            cost += self.board.costs_rows[x].value
        return cost

    def calculate_rows_columns_costs(self):
        for row in range(9):
            self.board.costs_rows[row].value = self.calculate_cost_values(self.board.get_row_values(row))

        for column in range(9):
            self.board.costs_columns[column].value = self.calculate_cost_values(self.board.get_column_values(column))

    def calculate_cost_values(self, values):
        exist_list = [False for x in range(9)]
        for value in values:
            if value == 0: continue
            exist_list[value-1] = True
        pass

        cost = 0
        for exist in exist_list:
            if exist == False:
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
                if (self.board.get_locked(element_1_column, element_1_row) == False and self.board.get_locked(element_2_column, element_2_row) == False):
                    break

        return ((element_1_column, element_1_row), (element_2_column, element_2_row))

    def check_transaction(self, cost_diff):
        if cost_diff < 0:
            self.temperature_update()
            self.reheat = 0
            return True
        else:
            probability_true = self.temperature/100
            probability_false = 1 - probability_true
            choices = [True,False]
            choices_probability = [probability_true,probability_false]
            draw = choice_numpy(choices,1,p=choices_probability)[0]
            if draw == False:
                self.reheat += 1
            else:
                self.reheat = 0
            self.temperature_update()
            return draw


    def swap(self, e1_col, e1_row, e2_col, e2_row):
        value_e1 = self.board.get_value(e1_col, e1_row)
        self.board.set(e1_col, e1_row, self.board.get_value(e2_col, e2_row))
        self.board.set(e2_col, e2_row,value_e1)

    def init_board_random(self):
        # for each of 9 squares
        for k in range(9):
            values = list(range(1,10))
            add_row = k % 3
            add_col = int(k / 3)

            for x in range(3):
                for y in range(3):
                    row = x + (add_row*3)
                    col = y + (add_col*3)
                    value_point = self.board.get_value(col,row)
                    if value_point != 0:
                        values.remove(value_point)

            random.shuffle(values)

            for x in range(3):
                for y in range(3):
                    row = x + add_row*3
                    col = y + add_col*3
                    value_point = self.board.get_value(col,row)
                    if value_point == 0:
                        self.board.set(col,row,values.pop())

            self.gui.sync_board_and_canvas()

    def color_altered_costs(self, highlight_bg = True):
        if highlight_bg == True:
            self.board.costs_rows[self.swap_elements[0][1]].color = "#7999ff"
            self.board.costs_rows[self.swap_elements[1][1]].color = "#7999ff"
            self.board.costs_columns[self.swap_elements[0][0]].color = "#7999ff"
            self.board.costs_columns[self.swap_elements[1][0]].color = "#7999ff"
        else:
            self.board.costs_rows[self.swap_elements[0][1]].color = "#b1ddff"
            self.board.costs_rows[self.swap_elements[1][1]].color = "#b1ddff"
            self.board.costs_columns[self.swap_elements[0][0]].color = "#b1ddff"
            self.board.costs_columns[self.swap_elements[1][0]].color = "#b1ddff"


    def check_for_reheat(self):
        if self.reheat > self.reheat_limit:
            self.temperature = self.temperature_reheat
            self.reheat = 0

    def temperature_update(self):
        self.temperature = self.temperature * self.cooling_rate
        self.check_for_reheat()

    def button_load(self,file):
        self.board.clear()
        f = open(file,"r")
        for x in range(9):
            line = f.readline()
            for y in range(9):
                if int(line[y]) != 0:
                    self.board.set(y,x,int(line[y]),True)
        self.calculate_rows_columns_costs()
        self.board.cost_global.value = self.calculate_cost_global()
        self.gui.sync_board_and_canvas()
        self.state = -1


random.seed(time.time())
sudoku_board = SudokuBoard()
gui = SudokuGUI(Tk(), sudoku_board, SudokuSA(sudoku_board))
gui.mainloop()
