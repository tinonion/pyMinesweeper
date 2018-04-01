import tkinter as tk
from PIL import Image, ImageTk
import boardgen


def gen_image(path):
    img = Image.open(path)
    processed_img = ImageTk.PhotoImage(img)
    return processed_img


def place_ele(gui, img, x, y):
    widget = Widget(gui.master, gui.info)
    widget.configure(image=img)
    widget.image = img
    widget.grid(column=x, row=y)
    return widget


class Info(object):

    def __init__(self):
        self.pressed = False
        self.middle_pressed = False
        self.current = None
        self.current_id = None
        self.widget_dict = dict()
        self.coretile_lst = []
        self.gui = None


class Images(object):

    def __init__(self, img_paths):
        self.img_paths = img_paths
        self.img_dict = dict()

        for path in img_paths:
            self.img_dict[path] = gen_image('./sprites/%s.jpg' % path)


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
        try:
            self.info.current.release_specific()
        except AttributeError:
            pass


class CoreTile(Widget):

    def __init__(self, gui, column, row):
        super().__init__(gui.master, gui.info)
        self.gui = gui
        self.loc = (column, row)
        self.mine = False
        self.flag = False
        self.explored = False
        self.adj_mines = None
        self.images = gui.core_images.img_dict

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
        if self.info.pressed and not self.explored and not self.gui.lost:
            self.press()
        if self.info.middle_pressed and not self.gui.lost:
            self.event_generate('<ButtonPress-2>')

    def mouse_leave(self, event):
        if self.info.pressed and not self.explored and not self.gui.lost:
            self.relieve()
        elif self.info.middle_pressed and not self.gui.lost:
            for x in range(-1, 2):
                for y in range(-1, 2):
                    col = self.loc[0] + x
                    row = self.loc[1] + y
                    if (col, row) in self.gui.coretiles and not self.gui.coretiles[(col, row)].flag \
                            and not self.gui.coretiles[(col, row)].explored:
                        self.gui.coretiles[(col, row)].relieve()

    def press_click(self, event):
        self.info.pressed = True
        if not self.explored and not self.gui.lost and not self.flag:
            self.press()

    def middle_mouse_press(self, event):
        self.info.middle_pressed = True
        if not self.gui.lost and not self.flag:
            for x in range(-1, 2):
                for y in range(-1, 2):
                    col = self.loc[0] + x
                    row = self.loc[1] + y
                    if (col, row) in self.gui.coretiles and not self.gui.coretiles[(col, row)].flag \
                            and not self.gui.coretiles[(col, row)].explored:
                        self.gui.coretiles[(col, row)].configure(image=self.images['exp_0'])

    def middle_mouse_release(self, event):
        self.info.middle_pressed = False
        tile = self.info.current
        if not self.gui.lost:
            if self.check_nearby_flags() == self.adj_mines and self.info.current.explored:
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        col = tile.loc[0] + x
                        row = tile.loc[1] + y
                        if (col, row) in self.gui.coretiles and not self.gui.coretiles[(col, row)].flag \
                                and not self.gui.coretiles[(col, row)].explored:
                            self.gui.coretiles[(col, row)].interpret_adjacent()
            else:
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        col = tile.loc[0] + x
                        row = tile.loc[1] + y
                        if (col, row) in self.gui.coretiles and not self.gui.coretiles[(col, row)].flag \
                                and not self.gui.coretiles[(col, row)].explored:
                            self.gui.coretiles[(col, row)].relieve()

    def place_flag(self, event):
        if not self.gui.lost:
            if not self.flag and not self.explored:
                self.flag = True
                self.configure(image=self.images['flag'])
            elif not self.explored:
                self.flag = False
                self.configure(image=self.images['unexp'])

    def press_space(self, event):
        if not self.explored:
            self.event_generate('<ButtonPress-3>')
        elif self.check_nearby_flags() == self.adj_mines:
            for x in range(-1, 2):
                for y in range(-1, 2):
                    col = self.loc[0] + x
                    row = self.loc[1] + y
                    if (col, row) in self.gui.coretiles and not self.gui.coretiles[(col, row)].flag:
                        self.gui.coretiles[(col, row)].interpret_adjacent()

    def release_specific(self):
        self.info.pressed = False
        if not self.gui.started and not self.flag:
            boardgen.distribute_mines(self.gui, self.loc)
            self.info.current.interpret_adjacent()
            self.gui.started = True
        elif self.info.current.mine and not self.gui.lost and not self.flag:
            boardgen.clicked_mine(self.gui)
        elif not self.gui.lost and not self.flag:
            self.info.current.explored = True
            self.info.current.interpret_adjacent()

    def interpret_adjacent(self):
        adj_mines = 0
        compared_safe = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                col = self.loc[0] + x
                row = self.loc[1] + y
                if (col, row) in self.gui.coretiles and self.gui.coretiles[(col, row)] != self:
                    compared_tile = self.gui.coretiles[(col, row)]
                    if compared_tile.mine:
                        adj_mines += 1
                    else:
                        compared_safe.append(compared_tile)
        self.adj_mines = adj_mines
        self.configure(image=self.images['exp_%s' % str(adj_mines)])
        self.explored = True
        if adj_mines == 0:
            for tile in compared_safe:
                if not tile.explored and not tile.flag:
                    tile.interpret_adjacent()

    def check_nearby_flags(self):
        adj_flags = 0
        for x in range(-1, 2):
            for y in range(-1, 2):
                col = self.loc[0] + x
                row = self.loc[1] + y
                if (col, row) in self.gui.coretiles and self.gui.coretiles[(col, row)].flag:
                    adj_flags += 1
        return adj_flags

    def reveal_mine(self):
        if self.info.current == self:
            self.configure(image=self.images['triggered_mine'])
        elif self.mine:
            self.configure(image=self.images['mine'])
        elif self.flag:
            self.configure(image=self.images['misflagged_mine'])


class StartButton(Widget):

    def __init__(self, gui):
        super().__init__(gui.master, gui.info)
        self.gui = gui
        self.images = gui.start_images

        self.configure(image=self.images.img_dict['start'])
        self.image = self.images.img_dict['start']

        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)
        self.bind('<ButtonPress-1>', self.press_click)
        self.bind('<ButtonRelease-1>', self.release_click)

    def pressed(self):
        self.configure(image=self.images.img_dict['pressed_start'])

    def relieve(self):
        self.configure(image=self.images.img_dict['start'])

    def enter(self, event):
        if self.info.pressed:
            self.pressed()

    def leave(self, event):
        if self.info.pressed:
            self.relieve()

    def press_click(self, event):
        self.info.pressed = True
        self.pressed()

    def release_specific(self):
        self.relieve()
        boardgen.reset_board(self.gui)


class GUI(object):

    def __init__(self, master, info):
        self.master = master
        self.coretiles = dict()
        self.info = info
        self.info.gui = self
        self.started = False
        self.lost = False

        gui_img_paths = ['unexp', 'border_LR', 'border_TB', 'border_TLcorner', 'border_TRcorner', 'border_BLcorner',
                         'border_BRcorner', 'border_Rjoint', 'border_Ljoint', 'blank']
        self.gui_images = Images(gui_img_paths).img_dict

        for x in range(1, 31):
            for y in [0, 3, 20]:
                place_ele(self, self.gui_images['border_TB'], x, y)

        for x in range(1, 31):
            for y in [1, 2]:
                place_ele(self, self.gui_images['blank'], x, y)

        for x in [0, 31]:
            for y in range(4, 20):
                place_ele(self, self.gui_images['border_LR'], x, y)
            for y in range(1, 3):
                place_ele(self, self.gui_images['border_LR'], x, y)

        place_ele(self, self.gui_images['border_Ljoint'], 0, 3)
        place_ele(self, self.gui_images['border_Rjoint'], 31, 3)
        place_ele(self, self.gui_images['border_TRcorner'], 31, 0)
        place_ele(self, self.gui_images['border_TLcorner'], 0, 0)
        place_ele(self, self.gui_images['border_BRcorner'], 31, 20)
        place_ele(self, self.gui_images['border_BLcorner'], 0, 20)

        start_img_paths = ['start', 'pressed_start', 'failed_start', 'suspense_start', 'completed_start']
        self.start_images = Images(start_img_paths)
        start_button = StartButton(self)
        start_button.place(x=377, y=19)

        core_img_paths = ['unexp', 'mine', 'triggered_mine', 'misflagged_mine', 'flag'] \
                         + ['exp_' + str(x) for x in range(0, 9)]
        self.core_images = Images(core_img_paths)
        for x in range(1, 31):
            for y in range(4, 20):
                tile = CoreTile(self, x, y)
                tile.grid(column=x, row=y)
                self.coretiles[tile.loc] = tile


class Root(object):

    def __init__(self, info):
        self.info = info
        self.root = tk.Tk()

        self.root.bind('<Motion>', self.mouse_motion)

    def mouse_motion(self, event):
        x, y = self.root.winfo_pointerxy()
        try:
            new_id = self.root.winfo_containing(x, y).winfo_id()
            if new_id in self.info.widget_dict and new_id != self.info.current_id:
                if self.info.current is not None:
                    self.info.current.event_generate('<Leave>')
                    self.info.current.mouse = False
                self.info.current = self.info.widget_dict[new_id]
                self.info.current.focus_set()
                self.info.current_id = new_id
                self.info.current.mouse = True
                self.info.current.event_generate('<Enter>')
        except AttributeError:
            pass
