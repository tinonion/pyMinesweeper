import random


mine_cnt = 99


def reset_board(gui):
    gui.started = False
    gui.lost = False
    for tile_loc in gui.coretiles:
        gui.coretiles[tile_loc].mine = False
        gui.coretiles[tile_loc].flag = False
        gui.coretiles[tile_loc].explored = False
        gui.coretiles[tile_loc].configure(image=gui.core_images.img_dict['unexp'])


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
        eligible_tiles.pop(mine_loc)


def clicked_mine(gui):
    gui.lost = True
    for coretile_loc in gui.coretiles:
        gui.coretiles[coretile_loc].reveal_mine()
