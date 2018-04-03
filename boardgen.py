import random


mine_cnt = 99


# Resets board to original state
def reset_board(gui, timer, mine_counter):
    gui.info.started = False
    gui.info.locked = False
    gui.info.explored_tile_cnt = 0
    timer.reset_timer_images()
    mine_counter.reset_counter()
    gui.start_button.configure(image=gui.start_images['start'])
    for tile_loc in gui.coretiles:
        gui.coretiles[tile_loc].mine = False
        gui.coretiles[tile_loc].flag = False
        gui.coretiles[tile_loc].explored = False
        gui.coretiles[tile_loc].configure(image=gui.core_images['unexp'])


# Distributes mines on first click, called in core tile class in gui file
def distribute_mines(gui, tile_loc):
    eligible_tiles = list()
    coretile_dict = gui.coretiles
    for key in coretile_dict:
        eligible_tiles.append(coretile_dict[key])
    for x in range(-1, 2):
        for y in range(-1, 2):
            col = tile_loc[0] + x
            row = tile_loc[1] + y
            if (col, row) in gui.coretiles:
                eligible_tiles.remove(coretile_dict[(col, row)])
    for mine in range(mine_cnt):
        mine_loc = random.randint(0, len(eligible_tiles) - 1)
        eligible_tiles[mine_loc].mine = True
        gui.info.explored_tile_cnt += 1
        eligible_tiles.pop(mine_loc)


# Runs when a mine is clicked, causes lose state
def clicked_mine(gui):
    gui.info.locked = True
    gui.timer.timer_thread.cancel()
    gui.start_button.configure(image=gui.start_images['failed_start'])
    for coretile in gui.info.coretile_lst:
        coretile.reveal_mine()


def check_win(gui, info):
    if info.explored_tile_cnt == len(info.coretile_lst):
        info.locked = True
        gui.start_button.configure(image=gui.start_images['completed_start'])
        for coretile in gui.info.coretile_lst:
            coretile.reveal_mine()
