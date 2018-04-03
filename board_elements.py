import tkinter as tk
from PIL import Image, ImageTk
import boardgen
import threading


# Processes jpg images into a format accepted by Tkinter
def gen_image(path):
    img = Image.open(path)
    processed_img = ImageTk.PhotoImage(img)
    return processed_img


# When given the location of a core tile, returns list of all nearby tiles. Nearby refers to
# tiles adjacent or diagonal from the passed tile location
def find_nearby(tile_loc):
    nearby_tile_list = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            col = tile_loc[0] + x
            row = tile_loc[1] + y
            nearby_tile_list.append((col, row))
    return nearby_tile_list


# Stores a dictionary of processed images when passed a list of image names. The images must be in the
# sprites folder.
class Images(object):

    def __init__(self, img_paths):
        self.img_paths = img_paths
        self.img_dict = dict()

        for path in img_paths:
            self.img_dict[path] = gen_image('./sprites/%s.jpg' % path)


# The class that all GUI widgets are made from. Gives widgets basic mouse functionality to allow better
# mouse tracking and also causes the widget to be stored in the Info class
class Widget(tk.Label):

    def __init__(self, master, info):
        super().__init__(master, borderwidth=0)
        self.master = master
        self.info = info

        self.id = self.winfo_id()
        self.info.widget_dict[self.id] = self

        self.bind('<ButtonPress-1>', self.press_click)
        self.bind('<ButtonRelease-1>', self.release_click)

    def press_click(self, event):
        self.info.pressed = True

    def release_click(self, event):
        self.info.pressed = False


# Class for game board tiles.
class CoreTile(Widget):

    def __init__(self, gui, timer, mine_counter, column, row):
        super().__init__(gui.master, gui.info)
        self.gui = gui
        self.timer = timer
        self.mine_counter = mine_counter
        self.loc = (column, row)
        self.mine = False
        self.flag = False
        self.explored = False
        self.nearby_mines = None
        self.images = gui.core_images

        self.configure(image=self.images['unexp'])
        self.image = self.images['unexp']

        self.bind('<Enter>', self.mouse_enter)
        self.bind('<Leave>', self.mouse_leave)
        self.bind('<ButtonPress-1>', self.press_click)
        self.bind('<ButtonRelease-1>', self.release_click)
        self.bind('<ButtonPress-2>', self.middle_mouse_press)
        self.bind('<ButtonRelease-2>', self.middle_mouse_release)
        self.bind('<ButtonPress-3>', self.place_flag)
        self.bind('<space>', self.press_space)

    def press(self):
        self.configure(image=self.images['exp_0'])

    def relieve(self):
        self.configure(image=self.images['unexp'])

    def mouse_enter(self, event):
        if self.info.pressed and not self.explored and not self.info.locked:
            self.press()
        if self.info.middle_pressed and not self.info.locked:
            self.event_generate('<ButtonPress-2>')

    def mouse_leave(self, event):
        if self.info.pressed and not self.explored and not self.info.locked:
            self.relieve()
        elif self.info.middle_pressed and not self.info.locked:
            for tile in find_nearby(self.loc):
                if tile in self.gui.coretiles and not self.gui.coretiles[tile].flag \
                        and not self.gui.coretiles[tile].explored:
                    self.gui.coretiles[tile].relieve()

    def press_click(self, event):
        self.info.pressed = True
        self.gui.start_button.configure(image=self.gui.start_images['suspense_start'])
        if not self.explored and not self.info.locked and not self.flag:
            self.press()

    def middle_mouse_press(self, event):
        self.info.middle_pressed = True
        if not self.info.locked and not self.flag:
            for tile in find_nearby(self.loc):
                if tile in self.gui.coretiles and not self.gui.coretiles[tile].flag \
                        and not self.gui.coretiles[tile].explored:
                    self.gui.coretiles[tile].press()

    def middle_mouse_release(self, event):
        self.info.middle_pressed = False
        if not self.info.locked:
            for tile in find_nearby(self.info.current.loc):
                if self.check_nearby_flags() == self.nearby_mines and self.info.current.explored:
                    if tile in self.gui.coretiles and not self.gui.coretiles[tile].flag \
                            and not self.gui.coretiles[tile].explored:
                        self.gui.coretiles[tile].interpret_adjacent()
                elif tile in self.gui.coretiles and not self.gui.coretiles[tile].flag \
                        and not self.gui.coretiles[tile].explored:
                    self.gui.coretiles[tile].relieve()

    def place_flag(self, event):
        if not self.info.locked:
            if not self.flag and not self.explored:
                self.flag = True
                self.configure(image=self.images['flag'])
                self.mine_counter.flagged_mine()
            elif not self.explored:
                self.flag = False
                self.configure(image=self.images['unexp'])
                self.mine_counter.unflagged_mine()

    def press_space(self, event):
        if not self.explored:
            self.event_generate('<ButtonPress-3>')
        elif self.check_nearby_flags() == self.nearby_mines:
            for tile in find_nearby(self.loc):
                if tile in self.gui.coretiles and not self.gui.coretiles[tile].flag:
                    self.gui.coretiles[tile].interpret_adjacent()

    def release_click(self, event):
        self.info.pressed = False
        self.gui.start_button.configure(image=self.gui.start_images['start'])
        if not self.info.started and not self.flag:
            boardgen.distribute_mines(self.gui, self.info.current.loc)
            self.timer.start_timer()
            self.info.current.interpret_adjacent()
            self.info.started = True
        elif self.info.current.mine and not self.info.locked and not self.flag:
            boardgen.clicked_mine(self.gui)
        elif not self.info.locked and not self.flag:
            self.info.current.interpret_adjacent()

    # Checks nearby tiles when the tile is clicked in order to determine what number
    # it should be assigned.
    def interpret_adjacent(self):
        adj_mines = 0
        compared_tiles = []
        if self.mine:
            boardgen.clicked_mine(self.gui)
            self.configure(image=self.images['triggered_mine'])
            return
        for tile in find_nearby(self.loc):
            if tile in self.gui.coretiles and self.gui.coretiles[tile] != self:
                compared_tile = self.gui.coretiles[tile]
                compared_tiles.append(compared_tile)
                if compared_tile.mine:
                    adj_mines += 1
        self.nearby_mines = adj_mines
        self.configure(image=self.images['exp_%s' % str(adj_mines)])
        if not self.explored:
            self.info.explored_tile_cnt += 1
        self.explored = True
        boardgen.check_win(self.gui, self.info)
        if adj_mines == 0:
            for tile in compared_tiles:
                if not tile.explored and not tile.flag and not tile.mine:
                    tile.interpret_adjacent()

    # Used for space and middle mouse buttons, checks to make sure that space and middle mouse are
    # valid key presses at that tile
    def check_nearby_flags(self):
        adj_flags = 0
        for tile in find_nearby(self.loc):
            if tile in self.gui.coretiles and self.gui.coretiles[tile].flag:
                adj_flags += 1
        return adj_flags

    # Only called by clicked_mine function in boardgen file. Causes mines to be revealed when game is won
    def reveal_mine(self):
        if self.info.current == self and self.mine:
            self.configure(image=self.images['triggered_mine'])
        elif not self.flag and self.mine:
            self.configure(image=self.images['mine'])
        elif self.flag and not self.mine:
            self.configure(image=self.images['misflagged_mine'])


# Class for start button near top of GUI
class StartButton(Widget):

    def __init__(self, gui, timer, mine_counter):
        super().__init__(gui.master, gui.info)
        self.gui = gui
        self.timer = timer
        self.mine_counter = mine_counter
        self.images = gui.start_images

        self.configure(image=self.images['start'])
        self.image = self.images['start']

        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)
        self.bind('<ButtonPress-1>', self.press_click)
        self.bind('<ButtonRelease-1>', self.release_click)

    def pressed(self):
        self.configure(image=self.images['pressed_start'])

    def relieve(self):
        self.configure(image=self.images['start'])

    def enter(self, event):
        if self.info.pressed:
            self.pressed()

    def leave(self, event):
        if self.info.pressed:
            self.relieve()

    def press_click(self, event):
        self.info.pressed = True
        self.pressed()

    # Only function with consequence to the game. Causes board to be reset to original state.
    def release_click(self, event):
        self.info.pressed = False
        self.relieve()
        boardgen.reset_board(self.gui, self.timer, self.mine_counter)


# Used to create mine counter and timer in corners of game board. Stores necessary images
# alongside basic set-up like placing the individual digits.
class Display(object):

    def __init__(self, master, info, x, y):
        self.master = master
        self.info = info

        img_paths = ['sb_-'] + ['sb_' + str(x) for x in range(0, 10)]
        self.images = Images(img_paths).img_dict

        self.first_digit = Widget(self.master, self.info)
        self.first_digit.configure(image=self.images['sb_0'])
        self.second_digit = Widget(self.master, self.info)
        self.second_digit.configure(image=self.images['sb_0'])
        self.third_digit = Widget(self.master, self.info)
        self.third_digit.configure(image=self.images['sb_0'])

        self.first_digit.place(x=x, y=y)
        self.second_digit.place(x=x - 20, y=y)
        self.third_digit.place(x=x - 40, y=y)


# Timer that is in top right of game board. Uses several instances of Timer classes from threading
# module to drive timer
class Timer(Display):

    def __init__(self, master, info, x, y):
        super().__init__(master, info, x, y)
        self.time = 0
        self.timer_thread = threading.Timer(1, self.increment_timer)
        self.timer_thread.setDaemon(daemonic=True)

    def start_timer(self):
        self.timer_thread.start()

    def increment_timer(self):
        self.timer_thread = threading.Timer(1, self.increment_timer)
        self.timer_thread.setDaemon(daemonic=True)
        if self.info.started and not self.info.locked:
            self.time += 1
            if self.time <= 999:
                time = str(self.time).zfill(3)
                self.first_digit.configure(image=self.images['sb_%s' % time[2]])
                self.second_digit.configure(image=self.images['sb_%s' % time[1]])
                self.third_digit.configure(image=self.images['sb_%s' % time[0]])
            self.start_timer()

    def reset_timer_images(self):
        self.timer_thread.cancel()
        self.timer_thread = threading.Timer(1, self.increment_timer)
        self.timer_thread.setDaemon(daemonic=True)
        self.time = 0
        self.first_digit.configure(image=self.images['sb_0'])
        self.second_digit.configure(image=self.images['sb_0'])
        self.third_digit.configure(image=self.images['sb_0'])


# Counter in top left of game board that counts how many mines are left to be found
class MineCounter(Display):

    def __init__(self, master, info, x, y):
        super().__init__(master, info, x, y)
        self.mines_undiscovered = boardgen.mine_cnt
        self.set_counter_images()

    def flagged_mine(self):
        self.mines_undiscovered -= 1
        self.set_counter_images()

    def unflagged_mine(self):
        self.mines_undiscovered += 1
        self.set_counter_images()

    def set_counter_images(self):
        if self.mines_undiscovered <= 999:
            mines_undiscovered = str(self.mines_undiscovered).zfill(3)
            self.first_digit.configure(image=self.images['sb_%s' % mines_undiscovered[2]])
            self.second_digit.configure(image=self.images['sb_%s' % mines_undiscovered[1]])
            self.third_digit.configure(image=self.images['sb_%s' % mines_undiscovered[0]])

    def reset_counter(self):
        self.mines_undiscovered = boardgen.mine_cnt
        self.set_counter_images()
