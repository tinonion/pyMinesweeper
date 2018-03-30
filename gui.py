import tkinter as tk
from PIL import Image, ImageTk
import boardgen


def gen_image(path):
    img = Image.open(path)
    processed_img = ImageTk.PhotoImage(img)
    return processed_img


def place_ele(master, img, x, y):
    widget = tk.Label(master, image=img, borderwidth=0)
    widget.image = img
    widget.grid(column=x, row=y)
    return widget


class Info(object):

    def __init__(self):
        self.pressed = False
        self.current = None
        self.current_id = None
        self.label_dict = dict()
        self.gui = None


class CoreTile(object):

    def __init__(self, master, info, column, row):
        self.info = info
        self.mouse = None
        self.master = master
        self.loc = (column, row)
        self.mine = False
        self.explored = False

        self.core_image_dict = {
            'unexp': gen_image('./sprites/unexp.jpg'),
            '0': gen_image('./sprites/exp_blank.jpg'),
            'mine': gen_image('./sprites/mine.jpg'),
        }

        for num in range(1, 9):
            self.core_image_dict[str(num)] = gen_image('./sprites/exp_%s.jpg' % str(num))

        self.Label = tk.Label(self.master, borderwidth=0, image=self.core_image_dict['unexp'])
        self.Label.image = self.core_image_dict['unexp']
        self.id = self.Label.winfo_id()

        self.info.label_dict[self.id] = self

        self.Label.bind('<Enter>', self.mouse_enter)
        self.Label.bind('<Leave>', self.mouse_leave)
        self.Label.bind('<ButtonPress-1>', self.press_click)
        self.Label.bind('<ButtonRelease-1>', self.release_click)

    def __repr__(self):
        return str(self.loc)

    def press(self):
        self.Label.configure(image=self.core_image_dict['0'])

    def relieve(self):
        self.Label.configure(image=self.core_image_dict['unexp'])

    def mouse_enter(self, event):
        if self.info.pressed and not self.explored:
            self.press()

    def mouse_leave(self, event):
        if self.info.pressed and not self.explored:
            self.relieve()

    def press_click(self, event):
        self.info.pressed = True
        if not self.explored:
            self.press()

    def release_click(self, event):
        self.info.pressed = False
        if self.info.current.mine:
            self.info.current.explored = True
            self.info.current.Label.configure(image=self.core_image_dict['mine'])
        else:
            self.info.current.explored = True
            self.info.current.interpret_adjacent()

    def interpret_adjacent(self):
        adj_mines = 0
        compared_safe = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                col = self.loc[0] + x
                row = self.loc[1] + y
                if (col, row) in self.info.gui.tiles and self.info.gui.tiles[(col, row)] != self:
                    compared_tile = self.info.gui.tiles[(col, row)]
                    if compared_tile.mine:
                        adj_mines += 1
                    else:
                        compared_safe.append(compared_tile)
        self.Label.configure(image=self.core_image_dict['%s' % str(adj_mines)])
        self.explored = True
        if adj_mines == 0:
            for tile in compared_safe:
                if not tile.explored:
                    tile.interpret_adjacent()


class StartBtn(object):

    def __init__(self, master):
        self.master = master

        self.start_img_dict = {
            'start': gen_image('./sprites/start.jpg'),
            'pressed_start': gen_image('./sprites/pressed_start.jpg')
            'suspense_start': gen_image('./sprites/suspense_start.jpg'),
            'failed_start': gen_image('./sprites/failed_start.jpg'),
            'completed_start': gen_image('./sprites/completed_start.jpg'),
        }

        self.Label = tk.Label(self.master, borderwidth=0, image=self.start_img_dict['start'])
        self.Label.image = self.start_img_dict['start']

        self.Label.bind('<Enter>', self.mouse_enter)
        self.Label.bind('<Leave>', self.mouse_leave)
        self.Label.bind('<ButtonPress-1>', self.press_click)
        self.Label.bind('<ButtonRelease-1>', self.release_click)

    def pressed(self):
        self.Label.configure(image=self.start_img_dict['pressed_start'])

    def relieve(self):
        self.Label.configure(image=self.start_img_dict['start'])


class GUI(object):

    def __init__(self, master, info):
        self.master = master
        self.tiles = {}
        self.info = info
        self.info.gui = self

        gui_image_dict = {
            'unexp': gen_image('./sprites/unexp.jpg'),
            'exp_blank': gen_image('./sprites/exp_blank.jpg'),
            'border_LR': gen_image('./sprites/border_LR.jpg'),
            'border_TB': gen_image('./sprites/border_TB.jpg'),
            'border_TLcorner': gen_image('./sprites/border_TLcorner.jpg'),
            'border_TRcorner': gen_image('./sprites/border_TRcorner.jpg'),
            'border_BLcorner': gen_image('./sprites/border_BLcorner.jpg'),
            'border_BRcorner': gen_image('./sprites/border_BRcorner.jpg'),
            'border_Rjoint': gen_image('./sprites/border_Rjoint.jpg'),
            'border_Ljoint': gen_image('./sprites/border_Ljoint.jpg'),
            'blank': gen_image('./sprites/blank.jpg'),
            'start': gen_image('./sprites/start.jpg')
        }

        for x in range(1, 31):
            for y in [0, 3, 20]:
                place_ele(master, gui_image_dict['border_TB'], x, y)

        for x in range(1, 31):
            for y in [1, 2]:
                place_ele(master, gui_image_dict['blank'], x, y)

        for x in [0, 31]:
            for y in range(4, 20):
                place_ele(master, gui_image_dict['border_LR'], x, y)
            for y in range(1, 3):
                place_ele(master, gui_image_dict['border_LR'], x, y)

        place_ele(master, gui_image_dict['border_Ljoint'], 0, 3)
        place_ele(master, gui_image_dict['border_Rjoint'], 31, 3)
        place_ele(master, gui_image_dict['border_TRcorner'], 31, 0)
        place_ele(master, gui_image_dict['border_TLcorner'], 0, 0)
        place_ele(master, gui_image_dict['border_BRcorner'], 31, 20)
        place_ele(master, gui_image_dict['border_BLcorner'], 0, 20)

        for x in range(1, 31):
            for y in range(4, 20):
                tile = CoreTile(master, self.info, x, y)
                tile.Label.grid(column=x, row=y)
                self.tiles[tile.loc] = tile

        start_btn = StartBtn(self.master)
        start_btn.Label.place(x=377, y=19)


class Root(object):

    def __init__(self, input):
        self.input = input
        self.root = tk.Tk()

        self.root.bind('<Motion>', self.mouse_motion)

    def mouse_motion(self, event):
        x, y = self.root.winfo_pointerxy()
        new_id = self.root.winfo_containing(x, y).winfo_id()
        if new_id in self.input.label_dict and new_id != self.input.current_id:
            if self.input.current is not None:
                self.input.current.Label.event_generate('<Leave>')
                self.input.current.mouse = False
            self.input.current = self.input.label_dict[new_id]
            self.input.current_id = new_id
            self.input.current.mouse = True
            self.input.current.Label.event_generate('<Enter>')