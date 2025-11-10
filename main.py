import tkinter as tk
import random

# /c:/Users/user/OneDrive/Desktop/Analis/main.py
# Simple Snake game using tkinter


CELL_SIZE = 20
COLUMNS = 30
ROWS = 20
WIDTH = CELL_SIZE * COLUMNS
HEIGHT = CELL_SIZE * ROWS
UPDATE_MS = 100  # speed (lower is faster)

class SnakeGame(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.pack()
        master.title("Snake")
        self.reset()
        self.bind_all("<Key>", self.on_key)
        self.after(UPDATE_MS, self.game_loop)

    def reset(self):
        self.direction = (1, 0)  # moving right
        start_x = COLUMNS // 2
        start_y = ROWS // 2
        self.snake = [(start_x - i, start_y) for i in range(3)]  # head first
        self.spawn_food()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.draw()

    def spawn_food(self):
        free = {(x, y) for x in range(COLUMNS) for y in range(ROWS)} - set(self.snake)
        self.food = random.choice(list(free)) if free else None

    def on_key(self, event):
        key = event.keysym
        dx, dy = self.direction
        if key in ("Up", "w") and dy != 1:
            self.direction = (0, -1)
        elif key in ("Down", "s") and dy != -1:
            self.direction = (0, 1)
        elif key in ("Left", "a") and dx != 1:
            self.direction = (-1, 0)
        elif key in ("Right", "d") and dx != -1:
            self.direction = (1, 0)
        elif key in ("p", "space"):
            self.paused = not self.paused
        elif key in ("r", "Return") and self.game_over:
            self.reset()

    def step(self):
        if self.game_over or self.paused:
            return
        dx, dy = self.direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)
        # Check wall collision
        if not (0 <= new_head[0] < COLUMNS and 0 <= new_head[1] < ROWS):
            self.game_over = True
            return
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return
        # Move snake
        self.snake.insert(0, new_head)
        if self.food and new_head == self.food:
            self.score += 1
            self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.delete("all")
        # Draw food
        if self.food:
            x, y = self.food
            self.create_rectangle(x*CELL_SIZE, y*CELL_SIZE,
                                  (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
                                  fill="red", outline="")
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = "#00FF00" if i == 0 else "#008000"
            self.create_rectangle(x*CELL_SIZE, y*CELL_SIZE,
                                  (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
                                  fill=color, outline="")
        # HUD
        self.create_text(6, 6, anchor="nw", fill="white",
                         text=f"Score: {self.score}  {'PAUSED' if self.paused else ''}")
        if self.game_over:
            self.create_text(WIDTH//2, HEIGHT//2, fill="white",
                             font=("TkDefaultFont", 24), text="GAME OVER\nPress R to restart")

    def game_loop(self):
        self.step()
        self.draw()
        self.after(UPDATE_MS, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()