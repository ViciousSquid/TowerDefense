import tkinter as tk
from core.game import TowerDefenseGame

if __name__ == "__main__":
    root = tk.Tk()
    game = TowerDefenseGame(root)
    root.mainloop()
