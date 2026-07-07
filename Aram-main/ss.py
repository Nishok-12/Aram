import tkinter as tk
from tkinter import ttk


class AramHelpWindow:

    def __init__(self, parent):

        self.parent = parent

        self.font_size = 12
        self.current_theme = "dark"

        self.help_win = tk.Toplevel(parent)
        self.help_win.title("உதவி - ARAM IDE")
        self.help_win.geometry("1200x700")

        self.set_theme_colors()

        self.help_win.configure(bg=self.bg)

        self.create_topbar()
        self.create_layout()
        self.create_topics()

    # =========================
    # THEME
    # =========================

    def set_theme_colors(self):

        if self.current_theme == "dark":
            self.bg = "#1e1e1e"
            self.fg = "white"
            self.panel = "#2a2a2a"
            self.code_bg = "#151515"

        else:
            self.bg = "white"
            self.fg = "black"
            self.panel = "#eeeeee"
            self.code_bg = "#f5f5f5"

    def toggle_theme(self):

        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"

        self.set_theme_colors()

        self.help_win.configure(bg=self.bg)

        self.left_frame.configure(bg=self.panel)
        self.right_frame.configure(bg=self.bg)

        self.content_text.configure(
            bg=self.bg,
            fg=self.fg,
            insertbackground=self.fg
        )

        self.code_text.configure(
            bg=self.code_bg,
            fg="#00ff88",
            insertbackground="white"
        )

    # =========================
    # TOP BAR
    # =========================

    def create_topbar(self):

        topbar = tk.Frame(self.help_win, bg=self.panel, height=40)
        topbar.pack(fill="x")

        theme_btn = tk.Button(
            topbar,
            text="🌙 Theme",
            command=self.toggle_theme
        )
        theme_btn.pack(side="left", padx=5, pady=5)

        font_plus = tk.Button(
            topbar,
            text="A+",
            command=self.increase_font
        )
        font_plus.pack(side="left", padx=5)

        font_minus = tk.Button(
            topbar,
            text="A-",
            command=self.decrease_font
        )
        font_minus.pack(side="left", padx=5)

        self.language_var = tk.StringVar(value="தமிழ்")

        lang_combo = ttk.Combobox(
            topbar,
            textvariable=self.language_var,
            values=["தமிழ்", "English"],
            width=10,
            state="readonly"
        )

        lang_combo.pack(side="left", padx=10)

        search_entry = tk.Entry(topbar, width=30)
        search_entry.pack(side="right", padx=10, pady=5)

    # =========================
    # MAIN LAYOUT
    # =========================

    def create_layout(self):

        main_frame = tk.Frame(self.help_win, bg=self.bg)
        main_frame.pack(fill="both", expand=True)

        # LEFT INDEX
        self.left_frame = tk.Frame(main_frame, bg=self.panel, width=250)
        self.left_frame.pack(side="left", fill="y")

        # RIGHT CONTENT
        self.right_frame = tk.Frame(main_frame, bg=self.bg)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # TREEVIEW
        self.tree = ttk.Treeview(self.left_frame)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_topic_select)

        # CONTENT TITLE
        self.title_label = tk.Label(
            self.right_frame,
            text="ARAM HELP",
            font=("Nirmala UI", 18, "bold"),
            bg=self.bg,
            fg=self.fg
        )

        self.title_label.pack(pady=10)

        # CONTENT TEXT
        self.content_text = tk.Text(
            self.right_frame,
            wrap="word",
            font=("Nirmala UI", self.font_size),
            bg=self.bg,
            fg=self.fg,
            insertbackground=self.fg
        )

        self.content_text.pack(fill="both", expand=True, padx=10)

        # CODE LABEL
        code_label = tk.Label(
            self.right_frame,
            text="Sample Program",
            font=("Nirmala UI", 14, "bold"),
            bg=self.bg,
            fg=self.fg
        )

        code_label.pack()

        # CODE BOX
        self.code_text = tk.Text(
            self.right_frame,
            height=10,
            font=("Consolas", self.font_size),
            bg=self.code_bg,
            fg="#00ff88",
            insertbackground="white"
        )

        self.code_text.pack(fill="x", padx=10, pady=10)

        # COPY BUTTON
        copy_btn = tk.Button(
            self.right_frame,
            text="📋 Copy Program",
            command=self.copy_code
        )

        copy_btn.pack(pady=5)

    # =========================
    # TOPICS
    # =========================

    def create_topics(self):

        # IDE GUIDE
        ide_root = self.tree.insert("", "end", text="Exploring ARAM GUI")

        self.tree.insert(ide_root, "end", text="Interface Overview")
        self.tree.insert(ide_root, "end", text="Toolbar Buttons")
        self.tree.insert(ide_root, "end", text="Open Save")
        self.tree.insert(ide_root, "end", text="Shortcuts")
        self.tree.insert(ide_root, "end", text="Theme Change")

        # TUTORIALS
        tutorial_root = self.tree.insert("", "end", text="ARAM Tutorials")

        self.tree.insert(tutorial_root, "end", text="Numbers")
        self.tree.insert(tutorial_root, "end", text="Strings")
        self.tree.insert(tutorial_root, "end", text="Variables")
        self.tree.insert(tutorial_root, "end", text="Input Output")
        self.tree.insert(tutorial_root, "end", text="If Else")
        self.tree.insert(tutorial_root, "end", text="Loops")

    # =========================
    # TOPIC CLICK
    # =========================

    def on_topic_select(self, event):

        selected = self.tree.focus()

        topic = self.tree.item(selected)["text"]

        self.load_topic(topic)

    # =========================
    # LOAD TOPICS
    # =========================

    def load_topic(self, topic):

        self.content_text.delete("1.0", "end")
        self.code_text.delete("1.0", "end")

        self.title_label.config(text=topic)

        # -----------------------
        # INTERFACE OVERVIEW
        # -----------------------

        if topic == "Interface Overview":

            explanation = """
ARAM IDE contains:

• Left keyword sidebar
• Tamil code editor
• English translation pane
• Output console
• Toolbar buttons

This environment helps Tamil students learn programming easily.
"""

            self.content_text.insert("end", explanation)

        # -----------------------
        # SHORTCUTS
        # -----------------------

        elif topic == "Shortcuts":

            explanation = """
Keyboard Shortcuts:

Ctrl + N → New File
Ctrl + S → Save File
Ctrl + Z → Undo
Ctrl + Y → Redo
F5 → Run Program
F4 → Exit
"""

            self.content_text.insert("end", explanation)

        # -----------------------
        # NUMBERS
        # -----------------------

        elif topic == "Numbers":

            explanation = """
Numbers in ARAM:

• முழுஎண்
• புள்ளிஎண்

Example program:
"""

            code = '''எண் = 10
புள்ளி = 3.14

காட்டு(எண்)
காட்டு(புள்ளி)
'''

            self.content_text.insert("end", explanation)
            self.code_text.insert("end", code)

        # -----------------------
        # STRINGS
        # -----------------------

        elif topic == "Strings":

            explanation = """
Strings are text enclosed within double quotes.
"""

            code = '''காட்டு("வணக்கம் உலகம்")
'''

            self.content_text.insert("end", explanation)
            self.code_text.insert("end", code)

        # -----------------------
        # INPUT OUTPUT
        # -----------------------

        elif topic == "Input Output":

            explanation = """
Using பெறு() and காட்டு()
"""

            code = '''பெயர் = பெறு("பெயரை உள்ளிடவும்:")

காட்டு("வணக்கம்")
காட்டு(பெயர்)
'''

            self.content_text.insert("end", explanation)
            self.code_text.insert("end", code)

        # -----------------------
        # IF ELSE
        # -----------------------

        elif topic == "If Else":

            explanation = """
Conditional statements in ARAM.
"""

            code = '''எண் = 10

எனில் எண் > 5:
    காட்டு("பெரியது")
முடி
'''

            self.content_text.insert("end", explanation)
            self.code_text.insert("end", code)

        # -----------------------
        # LOOPS
        # -----------------------

        elif topic == "Loops":

            explanation = """
Loop example in ARAM.
"""

            code = '''சுற்று i = 1 முதல் 5:

    காட்டு(i)

முடி
'''

            self.content_text.insert("end", explanation)
            self.code_text.insert("end", code)

    # =========================
    # COPY CODE
    # =========================

    def copy_code(self):

        code = self.code_text.get("1.0", "end")

        self.help_win.clipboard_clear()
        self.help_win.clipboard_append(code)

    # =========================
    # FONT CONTROL
    # =========================

    def increase_font(self):

        self.font_size += 1

        self.content_text.configure(
            font=("Nirmala UI", self.font_size)
        )

        self.code_text.configure(
            font=("Consolas", self.font_size)
        )

    def decrease_font(self):

        if self.font_size > 8:
            self.font_size -= 1

        self.content_text.configure(
            font=("Nirmala UI", self.font_size)
        )

        self.code_text.configure(
            font=("Consolas", self.font_size)
        )


# ======================================
# OPEN HELP WINDOW
# ======================================

def open_help_window():

    AramHelpWindow(root)


# ======================================
# MAIN APP
# ======================================

root = tk.Tk()

root.geometry("1000x600")

help_btn = tk.Button(
    root,
    text="உதவி",
    command=open_help_window
)

help_btn.pack(pady=20)

root.mainloop()