import gui
import boardgen

info_holder = gui.Info()
root = gui.Root(info_holder)
gui = gui.GUI(root.root, info_holder)
boardgen.reset_board(gui)
root.root.mainloop()
