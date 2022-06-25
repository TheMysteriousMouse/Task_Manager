from datetime import date, timedelta, datetime
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from sqlite3 import Error

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")


new_font = ("Comic Sans MS", 18, "bold")


def create_connection():
    db_file = r'.\tm_database.db'
    conn = None
    try:
        conn = sqlite3.connect(db_file)

    except Error as e:
        print(e)

    return conn

# Creates the Master Window


class Main(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        self.title("Task Manager")
        # Keeps the window from resizing
        self.resizable(0, 0)
        container.pack(side=tk.BOTTOM, expand=True)
        for k in range(8):
            container.columnconfigure(k, weight=1)
            container.rowconfigure(k, weight=1)

        self.frames = {}

        # Creates the different frames for the pages
        for F in (RegisterLogin, Register, LoginPage, HabitPage):
            # Passes the master window and self so the frames have access to functs and sizing  `
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=1, column=1, sticky="nsew")
        # Starting page
        self.show_frame(RegisterLogin)

    # Brings the parameter frame to the top level aka viewing level
    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class RegisterLogin(tk.Frame):
    def __init__(self, parent, container):
        tk.Frame.__init__(self, parent, bg="black")
        register_button = tk.Button(self, text="Register", font=(
            "Comcic Sans MS", 11), command=lambda: container.show_frame(Register))
        login_button = tk.Button(self, text="Login", padx=7, font=(
            "Comcic Sans MS", 11), command=lambda: container.show_frame(LoginPage))

        register_button.pack(anchor="center", pady=15)
        login_button.pack(anchor="center")


class Register(tk.Frame):
    def __init__(self, parent, container):
        tk.Frame.__init__(self, parent, bg="black")

        new_username = tk.Label(self, text="Username:", font=(
            "Comcic Sans MS", 11), bg="black", fg="white")
        new_password = tk.Label(self, text="Password:", font=(
            "Comcic Sans MS", 11), bg="black", fg="white")
        warning = tk.Label(
            self, text="(Will delete previous user)", bg="black", fg="white")

        # Allows access to functions
        self.user_entry = tk.Entry(self)
        self.pass_entry = tk.Entry(self)

        create_button = tk.Button(
            self, text="Create", padx=9, bg="Blue", command=lambda: self.add_user(container))

        new_username.grid(row=0, column=0, padx=10, pady=10)
        self.user_entry.grid(row=0, column=1, padx=10, pady=10)
        new_password.grid(row=1, column=0, padx=10, pady=10)
        self.pass_entry.grid(row=1, column=1, padx=10, pady=10)
        create_button.grid(row=2, column=2)
        warning.grid(row=2, column=1, padx=5)

    def add_user(self, container):
        conn = create_connection()
        with conn:
            cur = conn.cursor()

            username = self.user_entry.get()
            password = self.pass_entry.get()

            cur.execute("DELETE FROM Users;")
            conn.commit()
            cur.execute("DELETE FROM Habits;")
            conn.commit()
            cur.execute(
                """INSERT INTO Users(Name,Password) VALUES(?,?) ;""", (username, password,))

            conn.commit()

            container.show_frame(LoginPage)


class LoginPage(tk.Frame):
    def __init__(self, parent, container):
        tk.Frame.__init__(self, parent, bg="black")
        container.geometry("300x135")

        username_lbl = tk.Label(self, text="Username:", font=(
            "Comcic Sans MS", 11), bg="black", fg="white")
        password_lbl = tk.Label(self, text="Password: ", font=(
            "Comcic Sans MS", 11), bg="black", fg="white")

        self.username_entry = tk.Entry(self)
        self.password_entry = tk.Entry(self, show="*")

        main_button = tk.Button(
            self, bg="Blue", padx=7, text='Submit', command=lambda: self.login(container))

        username_lbl.grid(row=0, column=0)
        self.username_entry.grid(row=0, column=1, pady=10)
        password_lbl.grid(row=1, column=0)
        self.password_entry.grid(row=1, column=1)
        main_button.grid(row=2, column=2)
        for i in range(8):
            self.rowconfigure(i, weight=3, minsize=40)
        for k in range(3):
            self.columnconfigure(k, weight=1, minsize=100)

    def login(self, container):
        conn = create_connection()
        with conn:
            username = self.username_entry.get()
            password = self.password_entry.get()

            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM Users WHERE Name= ? AND Password = ? ", (username, password))
            id = cur.fetchall()
            if id:
                container.geometry("775x586")
                container.show_frame(HabitPage)

            else:
                self.username_entry.delete(0, 'end')
                self.password_entry.delete(0, 'end')
                self.username_entry.insert(0, "User Not Found")


class HabitPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black")

        habit_title_lbl = tk.Label(
            self, text="Habits", font=new_font, fg="white", bg="black")
        top_left_buffer = tk.Label(self, text="                ", bg="black")
        middle_buffer = tk.Label(self, text=3*"               ", bg="black")
        top_right_buffer = tk.Label(self, text="               ", bg="black")
        bottom_left_buffer = tk.Label(
            self, text="                ", bg="black")

        self.read_events()

        self.create_habits_form()

        habit_title_lbl.grid(row=1, column=2, padx=(0, 10))
        top_left_buffer.grid(row=0, column=0)
        top_right_buffer.grid(row=0, column=10)
        middle_buffer.grid(row=0, column=4)
        bottom_left_buffer.grid(row=12, column=0)

    def read_events(self):
        conn = create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT Habit,Goal,Time,Total FROM Habits")

            rows = cur.fetchall()
            display_habit_frame = tk.Frame(
                self, borderwidth=2, relief='sunken')

            scrollbar = ttk.Scrollbar(display_habit_frame)
            scrollbar.grid(row=0, column=8, ipady=40)
            headings = ['Habit', 'Goal', 'Today']

            tree = ttk.Treeview(display_habit_frame, height=5, column=headings,
                                show="headings", yscrollcommand=scrollbar.set)
            scrollbar.config(command=tree.yview)
            tree.grid(row=0, column=2)
            tree.column('Habit', minwidth=0, width=100, stretch=True)
            tree.column('Goal', minwidth=0, width=100, stretch=True)
            tree.column('Today', minwidth=0, width=100, stretch=True)
            delete_button = tk.Button(
                self, text="Delete", command=lambda: self.delete_habit(tree))

            delete_button.grid(row=3, column=2, ipadx=10, pady=10)
            display_habit_frame.grid(row=2, column=2)

            for col in headings:
                tree.heading(col, text=col.title())

            for item in rows:
                tree.insert('', 'end', values=item)

        # Updates the different frames on the page
            if rows != []:
                self.day_passed()
                self.week_passed()

            self.display_graph()
            self.update_time_form()

    def create_habits_form(self):
        create_frame = tk.Frame(self, bg="black")
        stores_new_goal = tk.StringVar(create_frame)
        stores_new_goal.set(1)

        new_habit_lbl = tk.Label(
            self, text="New  Habits", font=new_font, fg="white", bg="black")
        goal_input_lbl = tk.Label(create_frame, text="Goal: ", font=(
            "Comic Sans MS", 11), fg="white", bg="black")
        new_goal = tk.OptionMenu(
            create_frame, stores_new_goal, 1, 2, 3, 4, 5, 6, 7, 8,)

        new_habit_entry = tk.Entry(create_frame, width=17)
        new_habit_entry.insert(tk.END, 'Habit')

        create_button = tk.Button(create_frame, text="Create", command=lambda: self.create_habit(
            new_habit_entry, stores_new_goal))
        create_button.grid(row=2, column=6, padx=(
            100, 0), ipadx=5, pady=(25, 0))

        new_habit_lbl.grid(row=1, column=6, pady=15, padx=(25, 0))
        goal_input_lbl.grid(row=2, column=5, pady=(0, 50))
        new_goal.grid(row=2, column=6, ipadx=27, pady=(0, 50))
        new_habit_entry.grid(row=2, column=6, pady=(0, 120))

        create_frame.grid(row=2, column=6, sticky="nsew")

    def create_habit(self, task_entry, variable):
        conn = create_connection()
        with conn:
            cur = conn.cursor()

            day_created = date.today()
            days = day_created - timedelta(days=1)
            length_checker = self.check_length(task_entry)

            if length_checker:
                cur.execute("""INSERT INTO Habits(Habit,Goal,Date) VALUES(?,?,?) ;""",
                            (task_entry.get(), variable.get(), days))
                conn.commit()
                self.read_events()
                task_entry.delete(0, 'end')
                task_entry.insert(tk.END, 'Habit')
            else:
                task_entry.delete(0, 'end')
                task_entry.insert(tk.END, "HABIT'S TO LONG")

    def check_length(self, new_entry):
        length_habit = len(new_entry.get())
        current_state = 0
        if length_habit <= 8:
            current_state = 1
        return current_state

    def updated_time_query(self):
        conn = create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT Habit FROM Habits;")
            return cur.fetchall()

    def update_time_form(self):

        row_habits = self.updated_time_query()
        update_frame = tk.Frame(self, bg="black")
        stores_new_time = tk.StringVar(update_frame)
        stores_new_time.set(1)

        # Grabs all of the habits from row_habits
        habits = ['None']

        stores_habit = tk.StringVar(update_frame)

        # if there are habits create a list an then send it to tk.OptionMenu
        if row_habits:
            habits = [x[0] for x in row_habits]
            stores_habit.set(habits[0])
        else:
            stores_habit.set('None')

        update_title_lbl = tk.Label(
            update_frame, text="Update Time", font=new_font, fg="white", bg="black")
        habit_input_lbl = tk.Label(update_frame, text="Habit: ", font=(
            'Comic Sans MS', 11), fg="white", bg="black")
        time_input_lbl = tk.Label(update_frame, text="Time: ", font=(
            'Comic Sans MS', 11), fg="white", bg="black")

        select_habit_menu = tk.OptionMenu(update_frame, stores_habit, *habits)
        time_entry = tk.OptionMenu(
            update_frame, stores_new_time, 1, 2, 3, 4, 5, 6, 7, 8,)

        update_button = tk.Button(update_frame, text="Insert", command=lambda: self.update_time(
            stores_new_time, stores_habit))

        update_button.grid(row=8, column=5, ipadx=5,
                           padx=(105, 0), pady=(10, 0))
        update_title_lbl.grid(row=5, column=5, pady=(0, 10))
        update_frame.grid(row=6, column=6, pady=(100, 0))
        time_entry.grid(row=7, column=5, ipadx=27, pady=(10, 0))
        select_habit_menu.grid(row=6, column=5, ipadx=27)
        habit_input_lbl.grid(row=6, column=4)
        time_input_lbl.grid(row=7, column=4)

    def update_time(self, time, habit):
        new_time = time.get()
        habit_selection = habit.get()
        if new_time.isdigit():
            conn = create_connection()
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """SELECT * FROM Habits WHERE Habit = ?""", (habit_selection,))
                row = cur.fetchone()
                current_time = row[4]

                updated_time = current_time + int(new_time)
                total_time = row[4] + int(new_time)

                cur.execute("""UPDATE Habits SET Time=?, Total=? WHERE Habit = ? ;""",
                            (updated_time, total_time, habit_selection))
                conn.commit()
                self.read_events()

    def delete_habit(self, tree):
        conn = create_connection()
        with conn:
            selected_item = tree.selection()[0]
            habit = tree.item(selected_item, 'values')
            cur = conn.cursor()
            cur.execute("""DELETE from Habits WHERE Habit=?;""", (habit[0],))
            conn.commit()
            tree.delete(selected_item)
            self.read_events()

    def display_graph(self):
        conn = create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("""SELECT Habit,Total FROM Habits LIMIT 4;""")
            row = cur.fetchall()
        habit_x = []
        hours_y = []

        for first in row:
            for data in first:
                if type(data) == str:
                    habit_x.append(str(data))
                else:
                    hours_y.append(data)

        graph_frame = tk.Frame(self, bg="black")
        graph_lbl = tk.Label(graph_frame, text="Weekly Progress",
                             font=new_font, fg="white", bg="black")

        x = habit_x
        y = hours_y
        # Randomly grabs a color every time it's called
        colors = ['#FF1818', '#15F4EE', '#39ff14', 'yellow', "#9D27FF"]

        f = Figure(figsize=(4, 2), dpi=70)
        a = f.add_subplot(111)
        a.bar(x, y, color=random.choices(colors, k=len(x)))

        canvas = FigureCanvasTkAgg(f, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=2)
        canvas._tkcanvas.grid(row=2, column=2)

        graph_lbl.grid(row=1, column=2, pady=(90, 10))
        graph_frame.grid(row=6, column=2, pady=(15, 0), rowspan=5)

    def day_passed(self):
        conn = create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("""SELECT * FROM HABITS""")
            row = cur.fetchone()
        database_date = row[5]
        if database_date:
            current_date = date.today()
            date_time_obj = datetime.strptime(database_date, '%Y-%m-%d')
            a = datetime.date(date_time_obj)
            if a < current_date:
                updated_time = 0
                updated_date = date.today()
                cur.execute("""UPDATE HABITS SET Time=?, Date=?""",
                            (updated_time, updated_date,))
                conn.commit()

    def week_passed(self):
        conn = create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("""SELECT * FROM HABITS""")
            row = cur.fetchone()
        database_date = row[5]
        if database_date != '':
            current_date = date.today()
            date_time_obj = datetime.strptime(database_date, '%Y-%m-%d')
            a = datetime.date(date_time_obj)
            if current_date-a == 7:
                updated_time = 0
                updated_date = date.today()
                cur.execute("""UPDATE HABITS SET Time=?, Date=?""",
                            (updated_time, updated_date,))
                conn.commit()


main = Main()
main.mainloop()
