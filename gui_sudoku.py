from tkinter import *
import random
from tkinter import filedialog
from board import SudokuBoard

def sudogen_1(board):
    """
    Algorithm:
        Add a random number between 1-9 to each subgrid in the
        board, do not add duplicate random numbers.
    """
    board.clear()
    added = [0]
    for y in range(0, 9, 3):
        for x in range(0, 9, 3):
            if len(added) == 10:
                return
            i = 0
            while i in added:
                i = random.randint(1, 9)
            try:
                board.set(random.randint(x, x+2), random.randint(y, y+2), i, lock=True)
            except ValueError:
                print("Board rule violation, this shouldn't happen!")
            added.append(i)


def rgb(red, green, blue):
    """
    Make a tkinter compatible RGB color.
    """
    return "#%02x%02x%02x" % (red, green, blue)


class ButtonInterface:
    def button_new(self):
        pass

    def button_small_step(self):
        pass

    def button_big_step(self):
        pass

    def button_solve(self):
        pass

    def button_plot_temp(self):
        pass

    def button_plot_cost(self):
        pass

    def button_load(self,file):
        pass



class SudokuGUI(Frame):
    board_generators = {"SudoGen v1 (Very Easy)": sudogen_1}
    board_generator = staticmethod(sudogen_1)
    button_interface = object
    rsize = (700 / 10)
    guidesize = rsize * 3
    rects = [[None for x in range(10)] for y in range(10)]
    handles = [[None for x in range(10)] for y in range(10)]
    gui_update = True
    canvas = object

    def make_modal_window(self, title):
        window = Toplevel()
        window.title(title)
        window.attributes('-topmost', True)
        window.grab_set()
        window.focus_force()
        return window

    def make_grid(self):
        """
        draw 9*9 boxes
        :return:
        """
        self.canvas = Canvas(self, bg=rgb(250, 250, 250), width='700', height='700')
        self.canvas.pack(side='left', fill='both', expand='1')

        # self.make_square_lines()

        for y in range(10):
            for x in range(10):
                (xr, yr) = (x*self.rsize, y*self.rsize)
                r = self.canvas.create_rectangle(xr, yr, xr+self.rsize, yr+self.rsize)
                t = self.canvas.create_text(xr+self.rsize/2, yr+self.rsize/2, text="-3", font="System 25 bold")
                self.handles[y][x] = (r, t)

        self.sync_board_and_canvas()

    def sync_board_and_canvas(self):
        """
        write on canvas and color it
        :return:
        """
        if self.gui_update == True:
            g = self.board.grid
            for y in range(9):
                for x in range(9):
                    # write value
                    if (g[y][x].value) != 0:
                        self.canvas.itemconfig(self.handles[y][x][1], text=str(g[y][x].value))
                    else:
                        self.canvas.itemconfig(self.handles[y][x][1], text='')

                    # color values

                    if g[y][x].locked:
                        self.canvas.itemconfig(self.handles[y][x][0], fill="grey")
                    else:
                        self.canvas.itemconfig(self.handles[y][x][0], fill=g[y][x].color)

            for x in range(9):
                self.canvas.itemconfig(self.handles[x][9][1], text=str(self.board.costs_rows[x].value))
                self.canvas.itemconfig(self.handles[9][x][1], text=str(self.board.costs_columns[x].value))
                self.canvas.itemconfig(self.handles[x][9][0], fill=self.board.costs_rows[x].color)
                self.canvas.itemconfig(self.handles[9][x][0], fill=self.board.costs_columns[x].color)

            self.canvas.itemconfig(self.handles[9][9][1], text=str(self.board.cost_global.value))
            self.canvas.itemconfig(self.handles[9][9][0], fill=self.board.cost_global.color)

            self.make_square_lines()

    def make_square_lines(self):
        """
        draws lines separating 3x3 squares
        :return:
        """
        for y in range(9):
            for x in range(9):
                (xr, yr) = (x*self.guidesize, y*self.guidesize)
                self.rects[y][x] = self.canvas.create_rectangle(xr, yr, xr+self.guidesize, yr+self.guidesize, width=4)


    def __init__(self, master, board, button_interface):
        Frame.__init__(self, master)

        if master:
            master.title("Sudoku Simulated Annealing")

        assert isinstance(button_interface, ButtonInterface)
        self.button_interface = button_interface

        self.board = board
        bframe = Frame(self)
        tframe = Frame(self)

        # self.ng = Button(bframe , text="New", padx=10, pady=10, command=self.on_open)
        # self.ng.pack(side='left', fill='x', expand='1')

        self.sg = Button(bframe, text="small step", padx=10, pady=10, command=self.button_interface.button_small_step)
        self.sg.pack(side='left', fill='both', expand='1')

        self.lg = Button(bframe, text="big step", padx=10, pady=10, command=self.button_interface.button_big_step)
        self.lg.pack(side='left', fill='x', expand='1')

        self.query = Button(bframe, text="solve", padx=10, pady=10, command=self.button_interface.button_solve)
        self.query.pack(side='left', fill='x', expand='1')

        self.plottmep = Button(bframe, text="Temp Plot", padx=10, pady=10, command=self.button_interface.button_plot_temp)
        self.plottmep.pack(side='left', fill='x', expand='1')

        self.plotcost = Button(bframe, text="Cost Plot", padx=10, pady=10,command=self.button_interface.button_plot_cost)
        self.plotcost.pack(side='left', fill='x', expand='1')

        bframe.pack(side='bottom', fill='x', expand='1')

        # self.tb = Entry(tframe, width=20)
        # self.tb.pack(side='top',fill='x', expand='1')
        # #
        # tframe.pack(side='right',fill='x',expand='1')

        # self.canvas.bind("<Button-1>", self.canvas_click)
        # self.canvas.bind("<Key>", self.canvas_key)

        self.make_grid()
        self.current = None
        self.pack()

        self.button_interface.gui = self

        menubar = Menu(master)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.on_open)
        filemenu.add_command(label="Solve", command=self.button_interface.button_solve)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # create more pulldown menus
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Plot Temperature", command=self.button_interface.button_plot_temp)
        editmenu.add_command(label="Plot Cost", command=self.button_interface.button_plot_cost)
        menubar.add_cascade(label="Plot", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.button_interface.button_load)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        master.config(menu=menubar)

    def query_board(self):
        pass

    def on_open(self):
        ftypes = [('Text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes=ftypes)
        fl = dlg.show()

        if fl != '':
            text = self.button_interface.button_load(fl)
