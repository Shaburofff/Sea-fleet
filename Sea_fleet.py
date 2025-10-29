import tkinter as tk
import random
from collections import deque

class Ship:
    def __init__(self, size):
        self.size = size
        self.hits = 0
        self.positions = []
    @property
    def is_sunk(self):
        return self.hits >= self.size

class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sea Fleet")
        self.size = 10
        self.root.configure(bg="#f8f4e9")

        # Поля
        self.player_ships = []
        self.bot_ships = []
        self.player_board = [['~'] * self.size for _ in range(self.size)]
        self.bot_hidden = [['~'] * self.size for _ in range(self.size)]
        self.player_hits = set()
        self.bot_hits = set()
        self.game_over = False
        self.placing = True
        self.ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.placed = 0

        self.player_score = 0
        self.bot_score = 0
        self.total_ship_cells = sum(self.ship_sizes)  

        self.target_queue = deque()
        self.place_ships_randomly(self.bot_ships, self.bot_hidden)

        self.create_ui()
        self.update_status("Размещайте корабли на своём флоте")

    def create_ui(self):
        main = tk.Frame(self.root, bg="#f8f4e9")
        main.grid(row=0, column=0, padx=15, pady=15)

        # ПИ
        p_frame = tk.Frame(main, bg="#f8f4e9")
        p_frame.grid(row=0, column=0, padx=20)
        tk.Label(p_frame, text="Ваш флот", fg="#333", bg="#f8f4e9", font=("Comic Sans MS", 10, "bold")).grid(row=0, column=0, columnspan=10)
        # СИ
        self.player_score_label = tk.Label(p_frame, text=f"Очки: 0 / {self.total_ship_cells}", fg="#333", bg="#f8f4e9", font=("Comic Sans MS", 8))
        self.player_score_label.grid(row=1, column=0, columnspan=10)
        self.p_btns = []
        for i in range(10):
            row = []
            for j in range(10):
                cell = tk.Frame(p_frame, width=22, height=22, bg="#f8f4e9",
                                highlightbackground="#d0c5b5", highlightthickness=1,
                                relief="sunken")
                cell.grid(row=i+2, column=j, padx=0, pady=0) 
                btn = tk.Button(cell, width=2, height=1, bg="#f8f4e9", fg="#333",
                                activebackground="#e0d5c5", relief="flat",
                                font=("Comic Sans MS", 8),
                                command=lambda r=i, c=j: self.place(r, c))
                btn.pack(expand=True, fill="both")
                row.append(btn)
            self.p_btns.append(row)

        # ПБ
        b_frame = tk.Frame(main, bg="#f8f4e9")
        b_frame.grid(row=0, column=1, padx=20)
        tk.Label(b_frame, text="Флот врага", fg="#333", bg="#f8f4e9", font=("Comic Sans MS", 10, "bold")).grid(row=0, column=0, columnspan=10)
        # СБ
        self.bot_score_label = tk.Label(b_frame, text=f"Очки: 0 / {self.total_ship_cells}", fg="#333", bg="#f8f4e9", font=("Comic Sans MS", 8))
        self.bot_score_label.grid(row=1, column=0, columnspan=10)
        self.b_btns = []
        for i in range(10):
            row = []
            for j in range(10):
                cell = tk.Frame(b_frame, width=22, height=22, bg="#f8f4e9",
                                highlightbackground="#d0c5b5", highlightthickness=1,
                                relief="sunken")
                cell.grid(row=i+2, column=j, padx=0, pady=0)
                btn = tk.Button(cell, width=2, height=1, bg="#f8f4e9", fg="#333",
                                activebackground="#e0d5c5", relief="flat",
                                font=("Comic Sans MS", 8),
                                command=lambda r=i, c=j: self.attack(r, c))
                btn.pack(expand=True, fill="both")
                row.append(btn)
            self.b_btns.append(row)
        ctrl = tk.Frame(self.root, bg="#f8f4e9")
        ctrl.grid(row=1, column=0, pady=8)
        self.orient = tk.StringVar(value="horizontal")
        tk.Radiobutton(ctrl, text="→", variable=self.orient, value="horizontal",
                       bg="#f8f4e9", fg="#333", selectcolor="#e0d5c5",
                       activeforeground="#333", font=("Comic Sans MS", 9)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(ctrl, text="↓", variable=self.orient, value="vertical",
                       bg="#f8f4e9", fg="#333", selectcolor="#e0d5c5",
                       activeforeground="#333", font=("Comic Sans MS", 9)).pack(side=tk.LEFT, padx=10)

        self.status = tk.Label(self.root, text="", fg="#333", bg="#f8f4e9", font=("Comic Sans MS", 11))
        self.status.grid(row=2, column=0, pady=8)

    def can_place(self, board, x, y, size, orient):
        if orient == "h":
            if y + size > 10: return False
            for j in range(y, y+size):
                if board[x][j] != '~': return False
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        nx, ny = x+dx, j+dy
                        if 0 <= nx < 10 and 0 <= ny < 10 and board[nx][ny] != '~':
                            return False
        else:
            if x + size > 10: return False
            for i in range(x, x+size):
                if board[i][y] != '~': return False
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        nx, ny = i+dx, y+dy
                        if 0 <= nx < 10 and 0 <= ny < 10 and board[nx][ny] != '~':
                            return False
        return True

    def place_ship(self, board, x, y, size, orient, ships):
        ship = Ship(size)
        pos = []
        if orient == "h":
            for j in range(y, y+size):
                board[x][j] = 'S'
                pos.append((x, j))
        else:
            for i in range(x, x+size):
                board[i][y] = 'S'
                pos.append((i, y))
        ship.positions = pos
        ships.append(ship)

    def place_ships_randomly(self, ships, board):
        sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for size in sizes:
            for _ in range(100):
                x, y = random.randint(0,9), random.randint(0,9)
                orient = random.choice(["h", "v"])
                if self.can_place(board, x, y, size, orient):
                    self.place_ship(board, x, y, size, orient, ships)
                    break

    def place(self, x, y):
        if not self.placing or self.placed >= len(self.ship_sizes):
            return
        size = self.ship_sizes[self.placed]
        orient = "h" if self.orient.get() == "horizontal" else "v"
        if self.can_place(self.player_board, x, y, size, orient):
            self.place_ship(self.player_board, x, y, size, orient, self.player_ships)
            cells = [(x, j) for j in range(y, y+size)] if orient == "h" else [(i, y) for i in range(x, x+size)]
            for (i, j) in cells:
                self.p_btns[i][j].config(bg="#c0b5a5")
            self.placed += 1
            if self.placed == len(self.ship_sizes):
                self.placing = False
                for row in self.p_btns:
                    for b in row:
                        b.config(state=tk.DISABLED)
                self.update_status("Флот готов")
                self.root.after(800, self.bot_turn)
            else:
                self.update_status("Размещайте корабли")
        else:
            self.update_status("Невозможно разместить здесь")

    def attack(self, x, y):
        if self.game_over or self.placing or (x, y) in self.player_hits:
            return
        self.player_hits.add((x, y))
        if self.bot_hidden[x][y] == 'S':
            self.b_btns[x][y].config(bg="#a09585", highlightbackground="black", highlightthickness=1)
            for ship in self.bot_ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    # Обновляем счёт
                    self.player_score += 1
                    self.player_score_label.config(text=f"Очки: {self.player_score} / {self.total_ship_cells}")
                    if ship.is_sunk:
                        self.update_status("Корабль врага потоплен!")
                        for px, py in ship.positions:
                            self.b_btns[px][py].config(bg="#ff6b6b", highlightbackground="white", highlightthickness=2)
                    else:
                        self.update_status("Попадание!")
                    break
            if all(s.is_sunk for s in self.bot_ships):
                self.update_status("Победа!")
                self.game_over = True
                return
        else:
            self.b_btns[x][y].config(bg="#e0d5c5")
            self.update_status("Мимо!")
        self.root.after(600, self.bot_turn)

    def get_neighbors(self, x, y):
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < 10 and 0 <= ny < 10 and (nx, ny) not in self.bot_hits:
                yield (nx, ny)

    def bot_turn(self):
        if self.game_over:
            return

        while self.target_queue and self.target_queue[0] in self.bot_hits:
            self.target_queue.popleft()
        if self.target_queue:
            x, y = self.target_queue.popleft()
        else:
            candidates = []
            has_big_ships = any(len(s.positions) > 1 and not s.is_sunk for s in self.player_ships)
            for i in range(10):
                for j in range(10):
                    if (i, j) not in self.bot_hits:
                        if not has_big_ships or (i + j) % 2 == 0:
                            candidates.append((i, j))
            if not candidates:
                candidates = [(i, j) for i in range(10) for j in range(10) if (i, j) not in self.bot_hits]
            x, y = random.choice(candidates) if candidates else (0, 0)

        self.bot_hits.add((x, y))

        if self.player_board[x][y] == 'S':
            self.p_btns[x][y].config(bg="#a09585", highlightbackground="black", highlightthickness=1)
            for nb in self.get_neighbors(x, y):
                self.target_queue.append(nb)
            sunk = False
            for ship in self.player_ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    # Обновление счётчика
                    self.bot_score += 1
                    self.bot_score_label.config(text=f"Очки: {self.bot_score} / {self.total_ship_cells}")
                    if ship.is_sunk:
                        sunk = True
                        for px, py in ship.positions:
                            self.p_btns[px][py].config(bg="#ff6b6b", highlightbackground="white", highlightthickness=2)
                        for px, py in ship.positions:
                            for adj in self.get_neighbors(px, py):
                                if adj in self.target_queue:
                                    self.target_queue.remove(adj)
                        self.target_queue = deque(p for p in self.target_queue if p not in self.bot_hits)
                    break
            if all(s.is_sunk for s in self.player_ships):
                self.update_status("Ваш флот уничтожен(")
                self.game_over = True
                return
            msg = "Бот потопил корабль!" if sunk else "Бот попал!"
            self.update_status(msg)
            self.root.after(600, self.bot_turn)
        else:
            self.p_btns[x][y].config(bg="#e0d5c5")
            self.update_status("Бот промахнулся!")

    def update_status(self, msg):
        self.status.config(text=msg)

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    BattleshipGame(root)
    root.mainloop()
