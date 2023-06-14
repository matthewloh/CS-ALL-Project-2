import tkinter as tk

WIDTH = 800
HEIGHT = 600

class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        
        # Load images for Tom and Jerry
        self.tom_image = tk.PhotoImage(file="tom.png")
        self.jerry_image = tk.PhotoImage(file="jerry.png")
        
        # Create Tom and Jerry objects
        self.tom = self.canvas.create_image(100, 100, image=self.tom_image)
        self.jerry = self.canvas.create_image(700, 500, image=self.jerry_image)
        
        # Bind arrow key events for Tom's movement
        self.canvas.bind_all('<KeyPress-Left>', self.move_tom_left)
        self.canvas.bind_all('<KeyPress-Right>', self.move_tom_right)
        self.canvas.bind_all('<KeyPress-Up>', self.move_tom_up)
        self.canvas.bind_all('<KeyPress-Down>', self.move_tom_down)
        
    def move_tom_left(self, event):
        self.canvas.move(self.tom, -10, 0)
        
    def move_tom_right(self, event):
        self.canvas.move(self.tom, 10, 0)
        
    def move_tom_up(self, event):
        self.canvas.move(self.tom, 0, -10)
        
    def move_tom_down(self, event):
        self.canvas.move(self.tom, 0, 10)
        

if __name__ == '__main__':
    root = tk.Tk()
    game = Game(root)
    root.mainloop()



