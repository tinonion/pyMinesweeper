import board_elements as b_e


# Places widget with no function at a specified location and with a specified image. Used for
# event-less GUI elements like borders
def place_ele(gui, img, x, y):
    widget = b_e.Widget(gui.master, gui.info)
    widget.configure(image=img)
    widget.image = img
    widget.grid(column=x, row=y)
    return widget


# Used to store globally required information, like the widget that the mouse is currently
# hovering over
class Info(object):

    def __init__(self, master):
        self.master = master
        self.pressed = False
        self.middle_pressed = False
        self.current = None
        self.current_id = None
        self.widget_dict = dict()
        self.coretile_lst = list()
        self.explored_tile_cnt = 0
        self.gui = None
        self.started = False
        self.locked = False

        self.master.bind('<Motion>', self.mouse_motion)

    def mouse_motion(self, event):
        x, y = self.master.winfo_pointerxy()
        try:
            new_id = self.master.winfo_containing(x, y).winfo_id()
            if new_id in self.widget_dict and new_id != self.current_id:
                if self.current is not None:
                    self.current.event_generate('<Leave>')
                    self.current.mouse = False
                self.current = self.widget_dict[new_id]
                self.current.focus_set()
                self.current_id = new_id
                self.current.mouse = True
                self.current.event_generate('<Enter>')
        except AttributeError:
            pass


# Class that generates and organizes all elements of the game board
class GUI(object):

    def __init__(self, master, info):
        self.master = master
        self.coretiles = dict()
        self.info = info
        self.info.gui = self

        self.master.title('pySweeper')
        self.master.iconbitmap('./sprites/mine_icon.ico')

        gui_img_paths = ['unexp', 'border_LR', 'border_TB', 'border_TLcorner', 'border_TRcorner', 'border_BLcorner',
                         'border_BRcorner', 'border_Rjoint', 'border_Ljoint', 'blank']
        self.gui_images = b_e.Images(gui_img_paths).img_dict

        # Places borders and blank, functionless tiles
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

        # Places timer
        timer = b_e.Timer(self.master, self.info, 707, 21)
        self.timer = timer

        # Places mine counter
        mine_counter = b_e.MineCounter(self.master, self.info, 63, 21)
        self.mine_counter = mine_counter

        # Places start button
        start_img_paths = ['start', 'pressed_start', 'failed_start', 'suspense_start', 'completed_start']
        self.start_images = b_e.Images(start_img_paths).img_dict
        start_button = b_e.StartButton(self, self.timer, self.mine_counter)
        start_button.place(x=377, y=19)
        self.start_button = start_button

        # Places core game board tiles
        core_img_paths = (['unexp', 'mine', 'triggered_mine', 'misflagged_mine', 'flag']
                          + ['exp_' + str(x) for x in range(0, 9)])
        self.core_images = b_e.Images(core_img_paths).img_dict
        for x in range(1, 31):
            for y in range(4, 20):
                tile = b_e.CoreTile(self, timer, mine_counter, x, y)
                tile.grid(column=x, row=y)
                self.coretiles[tile.loc] = tile
                self.info.coretile_lst.append(tile)
