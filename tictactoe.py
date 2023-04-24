import tkinter as tk
from tkinter import messagebox
from tictactoe_ai import TicTacToeAI
import sqlite3
import database

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def init_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, score INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()


def update_score(username, score):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET score = score + ? WHERE username = ?", (score, username))
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY score DESC")
    users = c.fetchall()
    conn.close()
    return users


class ScoreboardWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Tableau des scores")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        tk.Label(self, text="Pseudo").grid(row=0, column=0, sticky="w")
        tk.Label(self, text="Score").grid(row=0, column=1, sticky="w")

        users = get_all_users()
        for i, user in enumerate(users):
            tk.Label(self, text=user[0]).grid(row=i+1, column=0, sticky="w")
            tk.Label(self, text=user[2]).grid(row=i+1, column=1, sticky="w")


class LoginWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Connexion")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.username_label = tk.Label(self, text="Pseudo:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Mot de passe:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self, text="Se connecter", command=self.login)
        self.login_button.pack()

        self.register_button = tk.Button(self, text="S'inscrire", command=self.register)
        self.register_button.pack()

        self.error_label = tk.Label(self, text="", fg="red")
        self.error_label.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if sqlite3.check_user(username, password):
            self.destroy()
            self.master.deiconify()  # Réaffichez la fenêtre principale après la connexion réussie
            app = TicTacToe(self.master)  # Créez une instance de TicTacToe
            app.pack()  # Remplacez app.grid() par app.pack()
        else:
            self.error_label.config(text="Pseudo ou mot de passe incorrect.")

    def on_close(self):
        self.master.destroy()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.config(text="Veuillez remplir tous les champs.")
            return

        if self.user_exists(username):
            self.error_label.config(text="Ce pseudo est déjà pris.")
        else:
            sqlite3.add_user(username, password)
            self.error_label.config(text="Inscription réussie. Vous pouvez vous connecter.")

    def user_exists(self, username):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        return user is not None


class TicTacToe(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Tic Tac Toe")

        self.board = [" "] * 9
        self.player = "X"
        self.opponent = "O"
        self.game_over = False
        self.ai_level = tk.IntVar()
        self.ai_level.set(1)
        self.ai = TicTacToeAI(self.opponent, level=self.ai_level.get())

        self.buttons = []
        for i in range(9):
            button = tk.Button(self, text=" ", width=10, height=3, command=lambda i=i: self.on_click(i))
            button.grid(row=i // 3, column=i % 3)
            self.buttons.append(button)

        tk.Label(self, text="Niveau de l'IA:").grid(row=3, column=0, sticky="w")
        tk.OptionMenu(self, self.ai_level, 1, 2, 3).grid(row=3, column=1)
        tk.Button(self, text="Réinitialiser", command=self.reset_board).grid(row=3, column=2)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_click(self, index):
        if self.board[index] == " " and not self.game_over:
            self.board[index] = self.player
            self.buttons[index].config(text=self.player, state="disabled")

            if self.check_winner(self.board, self.player):
                self.show_result(f"Le joueur {self.player} gagne!")
                self.game_over = True
            elif " " not in self.board:
                self.show_result("Match nul!")
                self.game_over = True
            else:
                move = self.ai.get_move(self.board)
                self.board[move] = self.opponent
                self.buttons[move].config(text=self.opponent, state="disabled")

                if self.check_winner(self.board, self.opponent):
                    self.show_result(f"Le joueur {self.opponent} gagne!")
                    self.game_over = True
                elif " " not in self.board:
                    self.show_result("Match nul!")
                    self.game_over = True

    def show_result(self, result):
        messagebox.showinfo("Résultat", result)
        if "gagne" in result:
            winner = result.split(" ")[2]
            if winner == "X":
                sqlite3.update_score(self.master.login_username, 1)
            else:
                sqlite3.update_score(self.master.login_username, -1)

    def reset_board(self):
        self.board = [" "] * 9
        for button in self.buttons:
            button.config(text=" ", state="normal")
        self.game_over = False
        self.player = "X"
        self.ai = TicTacToeAI(self.opponent, level=self.ai_level.get())

    def on_close(self):
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter le jeu?"):
            self.master.destroy() # Initialisez la base de données

def main():
    init_database()  # Initialisez la base de données

    root = tk.Tk()
    root.withdraw()
    login_window = LoginWindow(root)
    root.geometry("300x350")
    root.resizable(False, False)
    root.mainloop()

if __name__ == "__main__":
    main()