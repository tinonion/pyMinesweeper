import random


def distribute_mines(tile_dict, mine_cnt):
    not_mine_lst = []
    for key in tile_dict:
        not_mine_lst.append(tile_dict[key])
    for mine in range(mine_cnt):
        mine_loc = random.randint(0, len(not_mine_lst) - 1)
        not_mine_lst[mine_loc].mine = True
        not_mine_lst.pop(mine_loc)


