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

    # number of reheats
    reheat = 0
    # if reheat counter reaches this value, system will be reheated
    reheat_limit = 500
    # reheat counter
    reheat_counter = 0
    # temperature of system after repeat
    temperature_reheat = 80
    #  initial temperature of system
    temperature = 99
    # colling rate of system
    cooling_rate = 0.99

    def button_big_step(self):
        """
        runs heuristic to end of 3 part step and new 3 steps.
        3 steps are 1. randomly pick two values from same square that are not locked
                    2. swap them and calculate cost
                    3. if swapping update costs, otherwise return swapped values
        :return:
        """
        self.mainSA(3 + (3 - self.state))

    def button_small_step(self):
        """
        runs heuristic for 1 step
        heuristic has 3 steps:  1. randomly pick two values from same square that are not locked
                                2. swap them and calculate cost
                                3. if swapping update costs, otherwise return swapped values
        :return:
        """
        self.mainSA(1)

    def button_solve(self):
        """
        runs heuristic to end of "big step" ( to end of 3 steps )
        then runs heuristic for 100 000 cycles. If sudoku is solved method will stop running heuristic
        :return:
        """
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
        """
        plots cost in function of time
        :return:
        """
        self.plot_cost.plot_value_x_time_y()

    def button_plot_temp(self):
        """
        plots temperature in funciton of time
        :return:
        """
        self.plot_temperature.plot_value_x_time_y()

    def __init__(self, _sudoku_board):
        assert isinstance(_sudoku_board, SudokuBoard)
        self.board = _sudoku_board
        self.plot_cost = PlotStats()
        self.plot_temperature = PlotStats()
        self.calculate_rows_columns_costs()
        self.board.cost_global.value = self.calculate_cost_global()
        self.plot_temperature.y_label = "temperature"
        self.plot_temperature.legend_label = "cost & temp"
        self.plot_temperature.plot_label = "Sudoku Simulated Annealing"
        self.plot_cost.y_label = "cost & temp"
        self.plot_cost.legend_label = "global cost"
        self.plot_cost.plot_label = "Sudoku Simulated Annealing"
        self.plot_cost.color = 'r'

    def mainSA(self, steps):
        """
        App main method. It runs heuristic for given number of steps
        :param steps: number of steps to run heuristic
        :return:
        """
        for x in range(steps):
            # if cost is = sudoku board is correctly filled
            if self.board.cost_global.value == 0:
                self.plot_cost.add_x(self.board.cost_global.value)
                self.plot_temperature.add_x(self.temperature)
                print("DONE")
                print(self.reheat_counter)
                return
            else:
                pass

            # INIT BOARD
            # for each empty place in board picks random number from 1 to 9 so that rule of
            # numbers of 1 to 9 in every square is satisfied
            if self.state == -1:
                # fill squares in board
                self.init_board_random()
                # calculate cost of every row and column
                self.calculate_rows_columns_costs()
                # calculate global cost and set it to class variable
                self.board.cost_global.value = self.calculate_cost_global()
                # update gui
                self.gui.sync_board_and_canvas()
                # add initial global cost to plotting object
                self.plot_cost.add_x(self.board.cost_global.value)
                # add initial temperature of system to plotting object
                self.plot_temperature.add_x(self.temperature)

                # set state to next one
                self.state += 1
                return

            #  PICKS RANDOM ELEMENTS
            if self.state == 0:
                # get two random elements from board ( from same square )
                self.swap_elements = self.pick_random()
                # change color of chosen elements
                self.board.set_color(self.swap_elements[0][0], self.swap_elements[0][1], "red")
                self.board.set_color(self.swap_elements[1][0], self.swap_elements[1][1], "red")
                # sync gui
                self.gui.sync_board_and_canvas()

                # set state to next one
                self.state += 1

            # SWAP ELEMENTS
            elif self.state == 1:
                # swap elements
                self.swap(self.swap_elements[0][0], self.swap_elements[0][1], self.swap_elements[1][0], self.swap_elements[1][1])
                # change color of costs that will be updated
                self.color_altered_costs(True)

                # store old costs from rows and columns that are affected by swap
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

                # sync gui
                self.gui.sync_board_and_canvas()

                # set state to next one
                self.state += 1

            # CHECK IF SWAP WILL BE KEPT
            elif self.state == 2:
                # check if swap should be kept of not
                if self.check_transaction(self.diff_cost) == False:
                    # if swap should not be kept swap again elements so board is as before random swap
                    self.swap(self.swap_elements[0][0], self.swap_elements[0][1], self.swap_elements[1][0], self.swap_elements[1][1])

                    # return cost of rows and columns to old values ( that were before random swap )
                    self.board.costs_rows[self.swap_elements[0][1]].value = self.cost_row_1_old
                    self.board.costs_rows[self.swap_elements[1][1]].value = self.cost_row_2_old
                    self.board.costs_columns[self.swap_elements[0][0]].value = self.cost_column_1_old
                    self.board.costs_columns[self.swap_elements[1][0]].value = self.cost_column_2_old

                else:
                    # if swap will be kept update global cost
                    self.board.cost_global.value += self.diff_cost
                    # check if global cost + diff in cost is same as calculated global from sum of costs of columns and rows
                    assert self.board.cost_global.value == self.calculate_cost_global()

                # update gui
                self.gui.sync_board_and_canvas()

                # set state to next one
                self.state += 1

            # RESTORE COLORS
            elif self.state == 3:
                # restore colors of swap candidates
                self.board.set_color(self.swap_elements[0][0], self.swap_elements[0][1], "white")
                self.board.set_color(self.swap_elements[1][0], self.swap_elements[1][1], "white")
                # restore color of swap affected costs
                self.color_altered_costs(False)

                # update gui
                self.gui.sync_board_and_canvas()

                # set next state to 0
                self.state = 0

        # add current global cost to plotting object
        self.plot_cost.add_x(self.board.cost_global.value)
        # add current temperature of system to plotting object
        self.plot_temperature.add_x(self.temperature)

        # if global cost of system is 0 sudoku is solved stop executing heuristic
        if self.board.cost_global == 0:
            self.plot_cost.add_x(self.board.cost_global.value)
            self.plot_temperature.add_x(self.temperature)
            print("DONE EE")
            print(self.reheat_counter)
            return

    def calculate_cost_global(self):
        """
        calculates global cost by summing all costs of rows and columns
        cost of one row or column is number of values that break rule of sudoku that one row/column can have just once numbers 1,2,...,9
        sum of costs from all rows and columns is global cost
        :return: global cost
        """
        cost = 0
        # for each row and column
        for x in range(9):
            cost += self.board.costs_columns[x].value
            cost += self.board.costs_rows[x].value
        return cost

    def calculate_rows_columns_costs(self):
        """
        calculate cost of each row and column and set it to object variables
        cost of one row or column is number of values that break rule of sudoku that one row/column can have just once numbers 1,2,...,9
        :return:
        """
        for row in range(9):
            self.board.costs_rows[row].value = self.calculate_cost_values(self.board.get_row_values(row))

        for column in range(9):
            self.board.costs_columns[column].value = self.calculate_cost_values(self.board.get_column_values(column))

    def calculate_cost_values(self, values):
        """
        calculate cost of one row/column
        cost of one row or column is number of values that break rule of sudoku that one row/column can have just once numbers 1,2,...,9
        :param values: row/column values in array
        :return: cost of given row/column
        """

        # lift of 9 boolean False values
        exist_list = [False for x in range(9)]

        for value in values:
            if value == 0: continue
            # for each value in column/row array set corresponding index in boolean array to True
            exist_list[value-1] = True
        pass

        cost = 0
        for exist in exist_list:
            # for each False in boolean array increment cost because index of False in array is value that is missing in row/column
            if exist == False:
                cost += 1

        return cost

    def calculate_cost_row(self, row):
        """
        calculates cost of row
        :param row: row index
        :return: cost of row
        """
        return self.calculate_cost_values(self.board.get_row_values(row))

    def calculate_cost_column(self, col):
        """
        calculates cost of column
        :param col: column index
        :return: cost of column
        """
        return self.calculate_cost_values(self.board.get_column_values(col))

    def pick_random(self):
        """
        picks 2 random elements from same square. Square is also randomly picked
        :return: (( random element 1 column index, random element 1 row index ) , ( random element 2 column index, random element 2 row index )
        """
        while True:
            # chose randomly elements from one square ( not specific square )
            element_1_row = random.randrange(0, 3)
            element_1_column = random.randrange(0, 3)
            element_2_row = random.randrange(0, 3)
            element_2_column = random.randrange(0, 3)

            # chose randomly square
            square_x = random.randrange(0, 3)
            square_y = random.randrange(0, 3)

            # place random elements in that square.
            # ( translate column and row indexes in chosen square
            element_1_column += square_x * 3
            element_1_row += square_y * 3
            element_2_column += square_x * 3
            element_2_row += square_y * 3

            # check if elements are not same. If not check if random elements are not locked. If not, random elements are OK and return them
            # if some of checks fails try again random
            if element_1_row != element_2_row or element_1_column != element_2_column:
                if self.board.get_locked(element_1_column, element_1_row) == False and self.board.get_locked(element_2_column, element_2_row) == False:
                    break

        return ((element_1_column, element_1_row), (element_2_column, element_2_row))

    def check_transaction(self, cost_diff):
        """
        calculates if swapping of elements should be kept.
        If swap is not valid increase reheat. Otherwise reset reheat to 0
        :param cost_diff: difference between cost before swapping elements and after swapping elements
                        ( cost_diff > 0 if there is improvement of cost )
        :return: False if swap should NOT be kept. Otherwise True
        """

        #if cost is not positive, return True, update temperature and reset reheat
        if cost_diff < 0:
            print("Cycle: " + str(len(self.plot_temperature.list_x)) + " improvement of cost by" + str(cost_diff) + " Current cost: " + str(self.board.cost_global.value))
            self.temperature_update()
            self.reheat = 0
            return True
        else:
            # if cost difference is positive then chose if swap should be kept
            # chose randomly with probability of exp(-cooling_rate/temperature)
            probability_true = self.temperature/100
            probability_false = 1 - probability_true
            choices = [True, False]
            choices_probability = [probability_true, probability_false]
            draw = choice_numpy(choices,1,p=choices_probability)[0]

            # if draw is False increment reheat
            # otherwise reset reheat
            if draw == False:
                self.reheat += 1
            else:
                self.reheat = 0
            # update temperature at end
            self.temperature_update()
            return draw

    def swap(self, e1_col, e1_row, e2_col, e2_row):
        """
        swap elements on sudoku board
        :param e1_col: element 1 column
        :param e1_row: element 1 row
        :param e2_col: element 2 column
        :param e2_row: element 1 row
        """
        value_e1 = self.board.get_value(e1_col, e1_row)
        self.board.set(e1_col, e1_row, self.board.get_value(e2_col, e2_row))
        self.board.set(e2_col, e2_row, value_e1)

    def init_board_random(self):
        """
        for each empty place in board picks random number from 1 to 9 so that rule of
        numbers of 1 to 9 in every square is satisfied
        """

        # for each of 9 squares
        for k in range(9):
            # create list of all values ( 1, 2 ... 9)
            values = list(range(1,10))

            # calculate multiplier of row and column for each square in board
            add_row = k % 3
            add_col = int(k / 3)

            # go through all elements in one square
            for x in range(3):
                for y in range(3):
                    row = x + (add_row*3)
                    col = y + (add_col*3)
                    # remove all existing values in square from list of all values
                    value_point = self.board.get_value(col,row)
                    if value_point != 0:
                        values.remove(value_point)

            # shuffle list of all missing values in one square
            random.shuffle(values)

            # go through all elements in one square
            for x in range(3):
                for y in range(3):
                    row = x + add_row*3
                    col = y + add_col*3
                    # if element is empty (it has value 0) place value from list of all missing values
                    value_point = self.board.get_value(col,row)
                    if value_point == 0:
                        self.board.set(col,row,values.pop())

            # syc gui
            self.gui.sync_board_and_canvas()

    def color_altered_costs(self, highlight_bg = True):
        """
        change color of column and row costs altered by swapping
        :param highlight_bg: True: color it to darker blue color, False return color to normal
        :return:
        """
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
        """
        if reheat is bigger than reheat limit do the reheat process. Update temperature to reheat temperature
        :return:
        """
        if self.reheat > self.reheat_limit:
            print("\nCycle: " + str(len(self.plot_temperature.list_x)) + "Stuck at local minimum. Reheating system. Reheat counter" + str(self.reheat_counter)+ "\n")
            #set temperature of system to reheat temperature
            self.temperature = self.temperature_reheat
            # reset reheat
            self.reheat = 0
            # increment system reheat processes counter
            self.reheat_counter += 1

    def temperature_update(self):
        """
        updates temperature by formula:
        T(i+1) = T(i) * cooling rate
        :return:
        """
        self.temperature = self.temperature * self.cooling_rate
        self.check_for_reheat()

    def button_load(self,file):
        """
        button load, loads sudoku task in application
        :param file:
        :return:
        """
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
