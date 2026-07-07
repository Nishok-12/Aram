# ARAM Implementation with Tkinter GUI (Fullscreen + Toggle Panels + Multi-Window Safe)
#Aram IDE GUI_Version_1 (Supports All Highliting but Input not fully functional and Error is not handled (i.e.Window exits))

import ThiranLexer, ThiranParser, ThiranInterpreter
import tkinter as tk
from tkinter import filedialog, messagebox
import io, sys
import time
import re 

# ---------- Compiler Pipeline ----------
def lexer(code):
    lexer = ThiranLexer.Lexer(code)
    tokens, hasError = lexer.tokenize()
    return None if hasError else tokens

def parser(tokens):
    parser = ThiranParser.Parser(tokens)
    ast, hasError = parser.parse()
    return None if hasError else ast

def interpreter(ast):
    interpreter = ThiranInterpreter.Interpreter(ast)
    res, hasError = interpreter.interpret()
    return None if hasError else res

def compile_run(code: str) -> str:
    try:
        lex = lexer(code)
        if lex is None:
            return "சொற்றொடர் பிழை"
        parse = parser(lex)
        if parse is None:
            return "கட்டமைப்புப் பிழை"
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        res = interpreter(parse)
        sys.stdout = old_stdout
        output = buffer.getvalue()
        if output.strip():
            return output
        elif res is not None:
            return str(res)
        else:
            return "இயக்க பிழை"
    except Exception as e:
        return f"பிழை: {str(e)}"

# ---------- Tamil → English Keyword Map ----------
TAMIL_TO_ENGLISH = {
    "பட்டியலில்_இணை": "append_list",
    "பட்டியலில்_நீக்கு": "remove_from_list",
    "பட்டியலில்_சேர்": "add_to_list",
    "பட்டியலில்_சுருக்கு": "pop_list",
    "பட்டியல்_நீளம்": "list_len",
    "காட்டு": "print",
    "பெறு": "input",
    "முழுஎண்": "int",
    "புள்ளிஎண்": "float",
    "வாக்கியம்": "str",
    "வகை": "type",
    "வெளியேறு": "exit",
    "உண்மைவரை": "while",
    "சுற்று": "for",
    "முடி": "",
    "எனில்": "if",
    "பிறஎனில்": "elif",
    "பொய்எனில்": "else",
    "செய்": "def",
    "கொடு": "return",
    "உடை": "break",
    "தொடர்": "continue",
    "மற்றும்": "and",
    "அல்லது": "or",
    "இல்லை": "not",
    "உண்மை": "true",
    "பொய்": "false",
    "முயற்சி": "try",
    "தவிர": "except",
    "முடிவில்": "finally",
    "சேர்": "import",
}

# ---------- Tooltip ----------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, bg="#ffffe0", relief="solid", borderwidth=1,
                 font=("Arial", 10)).pack(ipadx=4, ipady=2)

    def _hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ---------- Accordion ----------
class Accordion(tk.Frame):
    def __init__(self, master, sections, on_insert, **kwargs):
        super().__init__(master, **kwargs)
        self.sections = sections
        self.on_insert = on_insert
        self.headers, self.frames = {}, {}
        self.active = None
        self._build()

    def _build(self):
        header_tooltips = {
            "கருத்து குறிகள்": "Logical Operator Keywords",
            "உள்ளீடு / வெளியீடு": "Input / Output Keywords",
            "சேர்": "Import Keywords",
            "சுழற்சி": "Loop Keywords",
            "நிபந்தனை": "Conditional Statements",
            "செயல்": "Function Keywords",
            "பட்டியல்": "List Keywords",
            "தரவு வகைகள்": "Data Types",
            "பிழை கையாளுதல்": "Exception Handling",
        }
        for title, items in self.sections:
            header = tk.Button(self, text=title, anchor="w", bg="#f2f2f2", fg="#111",
                            relief="flat", font=("Arial", 11, "bold"),
                            command=lambda t=title: self.toggle(t))
            header.pack(fill="x", pady=(2, 0), ipady=4, padx=2)
            self.headers[title] = header
            if title in header_tooltips:
                ToolTip(header, header_tooltips[title])
            frame = tk.Frame(self, bg="#fff")
            frame.pack(fill="x")
            frame.pack_forget()
            self.frames[title] = frame
            for tamil, eng in items:
                lbl = tk.Label(frame, text=tamil, anchor="w", bg="#fff", fg="green",
                            font=("Arial", 11), padx=12, pady=2)
                lbl.pack(fill="x")
                ToolTip(lbl, eng)
                lbl.bind("<Button-1>", lambda e, txt=tamil: self.on_insert(txt))

    def toggle(self, title):
        for t, fr in self.frames.items():
            fr.pack_forget()
            self.headers[t].config(bg="#f2f2f2")
        if self.active != title:
            self.frames[title].pack(fill="x", after=self.headers[title])
            self.headers[title].config(bg="#e0e0e0")
            self.active = title
        else:
            self.active = None

# ---------- Line Numbers ----------
class TextLineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text = text_widget
    def redraw(self, *_):
        self.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum,
                             font=("Courier New", 10), fill="#999")
            i = self.text.index(f"{i}+1line")

class CodeText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
    def _proxy(self, command, *args):
        result = self.tk.call(self._orig, command, *args)
        if command in ("insert", "delete", "replace") or command == "yview":
            self.event_generate("<<Change>>", when="tail")
        return result

# ---------- Translation ----------
def translate_tamil_to_english(text):
    for tamil in sorted(TAMIL_TO_ENGLISH, key=len, reverse=True):
        text = text.replace(tamil, TAMIL_TO_ENGLISH[tamil])
    return text

# ---------- ARAM IDE Window ----------
class ARAMWindow:
    def __init__(self, root):
        self.root = root
        self.root.state("zoomed")
        self.current_file = None
        self.code_modified = False
        self.left_visible = True
        self.right_visible = True
        self._setup_gui()
        self.update_title()
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)

    def update_title(self):
        if self.current_file:
            filename = self.current_file.split("/")[-1]
            self.root.title(f"அறம் Compiler IDE - {filename}")
        else:
            self.root.title("அறம் Compiler IDE - Untitled.aram")

    def _setup_gui(self):
        self.code_text = None
        self.english_text = None
        self.result_text = None

        # ---------- Top Toolbar ----------
        top = tk.Frame(self.root, bg="#f7f7f7")
        top.pack(fill="x")
        # Define buttons with their commands, colors, and shortcuts
        buttons = [
            ("புதிய", self.new_file, "#fff", "New-Ctrl+N"),
            ("திற", lambda: self.open_file(), "#fff", "Open-Ctrl+O"),
            ("சேமி", lambda: self.save_file(), "#fff", "Save-Ctrl+S"),
            ("மறு சேமி", lambda: self.save_file_as(), "#fff", "Save As-Ctrl+Shift+S"),
            ("அழி", lambda: self.clear_code(), "#fff", "Clear-F3"),
            ("இயக்கு", lambda: self.run_code(), "#08CB0E", "Run-F5"),
            ("முக்கிய சொற்கள்", self.toggle_left, "#0342FF", "Keywords-Ctrl+L"),
            ("ஆங்கில குறியீடு", self.toggle_right, "#0342FF", "English Code-Ctrl+R"),
            ("வெளியேறு", self.on_quit, "#FF0000", "Exit-F4"),
        ]
        for txt, cmd, color, shortcut in buttons:
            btn = tk.Button(
                top, text=txt, command=cmd,
                bg=color, fg="white" if color in ("#08CB0E", "#0342FF", "#FF0000") else "black"
            )
            btn.pack(side="left", padx=5, pady=5)
            ToolTip(btn, f"({shortcut})")  # Add tooltip showing the shortcut


        # ---------- Main Panes ----------
        self.main_paned = tk.PanedWindow(self.root, orient="vertical", sashrelief="raised", sashwidth=5)
        self.main_paned.pack(fill="both", expand=True)
        self.middle_paned = tk.PanedWindow(self.main_paned, orient="horizontal", sashrelief="raised", sashwidth=5)
        self.main_paned.add(self.middle_paned, stretch="always")

        # Left Accordion
        self.left_frame = tk.Frame(self.middle_paned, bg="white")
        self.middle_paned.add(self.left_frame, minsize=200)
        tk.Label(self.left_frame, text="முக்கிய சொற்கள்", bg="#eceff1", font=("Arial",12,"bold")).pack(fill="x")
        sections = [
            ("கருத்து குறிகள்", [("மற்றும்","and"),("அல்லது","or"),("இல்லை","not"),("உண்மை","true"),("பொய்","false")]),
            ("உள்ளீடு / வெளியீடு", [("காட்டு()","print()"),("பெறு()","input()")]),
            ("சேர்", [("சேர்","import")]),
            ("சுழற்சி", [("உண்மைவரை","while"),("சுற்று","for"),("முடி()","end")]),
            ("நிபந்தனை", [("எனில்","if"),("பிறஎனில்","elif"),("பொய்எனில்","else")]),
            ("செயல்", [("செய்","def"),("கொடு","return"),("உடை","break"),("தொடர்","continue")]),
            ("பட்டியல்", [("பட்டியலில்_இணை()","append_list()"),("பட்டியலில்_நீக்கு()","remove_from_list()"),
                          ("பட்டியலில்_சேர்()","add_to_list()"),("பட்டியலில்_சுருக்கு()","pop_list()"),
                          ("பட்டியல்_நீளம்()","list_len()")]),
            ("தரவு வகைகள்", [("முழுஎண்()","int()"),("புள்ளிஎண்()","float()"),("வாக்கியம்()","string()"),
                               ("வகை()","type()"),("வெளியேறு()","exit()")]),
            ("பிழை கையாளுதல்", [("முயற்சி","try"),("தவிர","except"),("முடிவில்","finally")]),
        ]
        accordion = Accordion(self.left_frame, sections, lambda txt: self.code_text.insert(tk.INSERT, txt+" "), bg="white")
        accordion.pack(fill="both", expand=True)

        # Center Tamil editor
        self.center_frame = tk.Frame(self.middle_paned, bg="white")
        self.middle_paned.add(self.center_frame, stretch="always")
        tk.Label(self.center_frame, text="அறம் குறியீடு", bg="#eceff1", font=("Arial",12,"bold")).pack(fill="x")
        editor_wrap = tk.Frame(self.center_frame)
        editor_wrap.pack(fill="both", expand=True)
        y_scroll = tk.Scrollbar(editor_wrap, orient="vertical")
        y_scroll.pack(side="right", fill="y")
        self.code_text = CodeText(editor_wrap, wrap="none", font=("Courier New",12), bg="white", yscrollcommand=y_scroll.set, undo=True, autoseparators=True, maxundo=-1)
        y_scroll.config(command=self.code_text.yview)
        line_nums = TextLineNumbers(editor_wrap, self.code_text, width=40, bg="#f5f5f5")
        line_nums.pack(side="left", fill="y")
        self.code_text.pack(side="left", fill="both", expand=True)

        # Right English pane
        self.right_frame = tk.Frame(self.middle_paned, bg="white")
        self.middle_paned.add(self.right_frame, minsize=250)
        tk.Label(self.right_frame, text="ஆங்கில குறியீடு", bg="#eceff1", font=("Arial",12,"bold")).pack(fill="x")
        editor_wrap_eng = tk.Frame(self.right_frame)
        editor_wrap_eng.pack(fill="both", expand=True)
        y_scroll_eng = tk.Scrollbar(editor_wrap_eng, orient="vertical")
        y_scroll_eng.pack(side="right", fill="y")
        self.english_text = CodeText(editor_wrap_eng, wrap="none", font=("Courier New",12), bg="white", yscrollcommand=y_scroll_eng.set)
        y_scroll_eng.config(command=self.english_text.yview)
        line_nums_eng = TextLineNumbers(editor_wrap_eng, self.english_text, width=40, bg="#f5f5f5")
        line_nums_eng.pack(side="left", fill="y")
        self.english_text.pack(side="left", fill="both", expand=True)

        # Bottom result pane
        bottom_frame = tk.Frame(self.main_paned, bg="white")
        self.main_paned.add(bottom_frame, minsize=150)
        tk.Label(bottom_frame, text="வெளியீடு", bg="#eceff1", font=("Arial",12,"bold")).pack(fill="x")
        self.result_text = tk.Text(bottom_frame, height=8, font=("Courier New",12), bg="white")
        self.result_text.pack(fill="both", expand=True)
        # ---------- Welcome / Notice Message on IDE Open ----------
        welcome_msg = (
            ">>வாழ்த்துகள்! நீங்கள் அறம் IDE-வில் இருக்கிறீர்கள்.\n"
            ">>இங்கு உங்கள் குறியீடுகளை எழுதலாம், இயக்கலாம், மற்றும் சேமிக்கலாம்.\n\n"
        )
        self.result_text.insert("1.0", welcome_msg, "welcome_msg")
        self.result_text.tag_config("welcome_msg", foreground="blue", font=("Courier New", 11, "italic"))
        self.result_text.see(tk.END)

        # # ---------- Common Editor Functions ----------
        # def cut_text(event=None):
        #     try:
        #         if self.code_text.tag_ranges("sel"):
        #             self.code_text.event_generate("<<Cut>>")
        #     except tk.TclError:
        #         pass
        #     return "break"

        # def copy_text(event=None):
        #     try:
        #         if self.code_text.tag_ranges("sel"):
        #             self.code_text.event_generate("<<Copy>>")
        #     except tk.TclError:
        #         pass
        #     return "break"

        # def paste_text(event=None):
        #     try:
        #         self.code_text.event_generate("<<Paste>>")
        #     except tk.TclError:
        #         pass
        #     return "break"

        # def undo_text(event=None):
        #     try:
        #         self.code_text.edit_undo()
        #     except tk.TclError:
        #         pass
        #     return "break"

        # def redo_text(event=None):
        #     try:
        #         self.code_text.edit_redo()
        #     except tk.TclError:
        #         pass
        #     return "break"

        # def select_all(event=None):
        #     try:
        #         self.code_text.tag_add("sel", "1.0", "end-1c")  # avoid including the extra newline
        #     except tk.TclError:
        #         pass
        #     return "break"
        
        # # ---------- Common Editor Shortcuts ----------
        # self.root.bind("<Control-x>", cut_text)
        # self.root.bind("<Control-c>", copy_text)
        # self.root.bind("<Control-v>", paste_text)
        # self.root.bind("<Control-z>", undo_text)
        # self.root.bind("<Control-y>", redo_text)
        # self.root.bind("<Control-a>", select_all)

       # ---------- Editor update ----------
        def update_editor(event=None):
            self.code_modified = True

            # ---------- Update English translation pane ----------
            english_code = translate_tamil_to_english(self.code_text.get("1.0", tk.END))
            
            # Temporarily enable English pane to update
            self.english_text.config(state="normal")
            self.english_text.delete("1.0", tk.END)
            self.english_text.insert("1.0", english_code)
            self.english_text.config(state="disabled")  # make read-only again

            # ---------- Remove old tags ----------
            self.code_text.tag_remove("keyword", "1.0", tk.END)
            self.code_text.tag_remove("string", "1.0", tk.END)
            self.english_text.tag_remove("keyword", "1.0", tk.END)
            self.english_text.tag_remove("string", "1.0", tk.END)

            # ---------- Highlight Tamil keywords (green) ----------
            for word in TAMIL_TO_ENGLISH.keys():
                start = "1.0"
                while True:
                    pos = self.code_text.search(word, start, stopindex=tk.END)
                    if not pos:
                        break
                    end = f"{pos}+{len(word)}c"
                    self.code_text.tag_add("keyword", pos, end)
                    start = end
            self.code_text.tag_config("keyword", foreground="green")

            # ---------- Highlight Tamil strings (red, including quotes) ----------
            code = self.code_text.get("1.0", tk.END)
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', code):
                start_index = f"1.0+{match.start()}c"
                end_index = f"1.0+{match.end()}c"
                self.code_text.tag_add("string", start_index, end_index)
            self.code_text.tag_config("string", foreground="red")

            # ---------- Highlight English keywords (green) ----------
            english_keywords = [v for v in TAMIL_TO_ENGLISH.values() if v]  # skip empty translations
            english_code = self.english_text.get("1.0", tk.END)
            for word in english_keywords:
                if not word:
                    continue
                for match in re.finditer(re.escape(word), english_code, re.IGNORECASE):
                    start_index = f"1.0+{match.start()}c"
                    end_index = f"1.0+{match.end()}c"
                    self.english_text.config(state="normal")  # temporarily enable to add tags
                    self.english_text.tag_add("keyword", start_index, end_index)
                    self.english_text.config(state="disabled")
            self.english_text.tag_config("keyword", foreground="green")

            # ---------- Highlight English strings (red, including quotes) ----------
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', english_code):
                start_index = f"1.0+{match.start()}c"
                end_index = f"1.0+{match.end()}c"
                self.english_text.config(state="normal")
                self.english_text.tag_add("string", start_index, end_index)
                self.english_text.config(state="disabled")
            self.english_text.tag_config("string", foreground="red")

            # ---------- Redraw line numbers ----------
            line_nums.redraw()
            line_nums_eng.redraw()



        # Bind the editor events
        self.code_text.bind("<<Change>>", update_editor)
        self.code_text.bind("<KeyRelease>", update_editor)
        self.english_text.bind("<<Change>>", lambda e: line_nums_eng.redraw())
        self.english_text.bind("<Configure>", lambda e: line_nums_eng.redraw())
        self.code_text.bind("<Configure>", lambda e: line_nums.redraw())

        # ---------- Keyboard Shortcuts ----------
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_file_as())  # Ctrl+Shift+S
        self.root.bind("<F5>", lambda e: self.run_code())
        self.root.bind("<Control-l>", lambda e: self.toggle_left())
        self.root.bind("<Control-r>", lambda e: self.toggle_right())
        self.root.bind("<F4>", lambda e: self.on_quit())
        self.root.bind("<F3>", lambda e: self.clear_code())  # Clear code
        

    # ---------- Panel Toggle ----------
    def toggle_left(self):
        if self.left_visible:
            self.middle_paned.forget(self.left_frame)
        else:
            self.middle_paned.add(self.left_frame, minsize=200, before=self.center_frame)
        self.left_visible = not self.left_visible

    def toggle_right(self):
        if self.right_visible:
            self.middle_paned.forget(self.right_frame)
        else:
            self.middle_paned.add(self.right_frame, minsize=250, after=self.center_frame)
        self.right_visible = not self.right_visible

    # ---------- Button Handlers ----------
    def new_file(self):
        new_root = tk.Toplevel()
        ARAMWindow(new_root)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("ARAM files","*.aram"),("All Files","*.*")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f:
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert("1.0", f.read())
            self.current_file = path
            self.code_modified = False
            self.update_title()
        except Exception as e:
            messagebox.showerror("பிழை", f"கோப்பு திறக்க முடியவில்லை:\n{str(e)}")

    def save_file(self):
        if self.current_file:
            with open(self.current_file,"w",encoding="utf-8") as f:
                f.write(self.code_text.get("1.0", tk.END).rstrip())
            messagebox.showinfo("சேமி", f"{self.current_file.split('/')[-1]} சேமிக்கப்பட்டது.")
        else:
            self.save_file_as()
        self.update_title()
        self.code_modified = False

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".aram", filetypes=[("ARAM files","*.aram"),("All Files","*.*")])
        if not path: return
        self.current_file = path
        with open(self.current_file,"w",encoding="utf-8") as f:
            f.write(self.code_text.get("1.0", tk.END).rstrip())
        messagebox.showinfo("மறு சேமி", f"{self.current_file.split('/')[-1]} சேமிக்கப்பட்டது.")
        self.update_title()
        self.code_modified = False

    def clear_code(self):
        if messagebox.askyesno("அழி", "உங்கள் குறியீடு முழுவதும் அழிக்கப்பட வேண்டுமா ?"):
            self.code_text.delete("1.0", tk.END)

    def run_code(self):
        src = self.code_text.get("1.0", tk.END).rstrip()
        if not src.strip():
            self.result_text.insert(tk.END, "குறியீடு இல்லை\n")
            self.result_text.see(tk.END)
            return

        filename = self.current_file.split("/")[-1] if self.current_file else "Untitled.aram"

        # Insert "[Running] filename.aram" in green at the bottom
        running_msg = f"[இயக்கப்படுகிறது] {filename}\n"
        self.result_text.insert(tk.END, running_msg, "running_msg")
        self.result_text.tag_config("running_msg", foreground="green")
        self.result_text.see(tk.END)
        self.result_text.update()

        start_time = time.time()

        # Compile and run
        output = compile_run(src)
        end_time = time.time()
        elapsed = end_time - start_time

        # Append program output below previous content with auto-scrolling
        if output.strip():
            for line in output.splitlines():
                self.result_text.insert(tk.END, line + "\n")
                self.result_text.see(tk.END)   # scroll to latest
                self.result_text.update()      # force update to GUI
                time.sleep(0.05)               # optional delay for effect

        # Append done message in red
        done_msg = f"[முடிந்தது] {filename} குறியீடு {elapsed:.3f} வினாடிகளில் நிறைவுற்றது\n"
        self.result_text.insert(tk.END, done_msg, "done_msg")
        self.result_text.tag_config("done_msg", foreground="red")
        self.result_text.see(tk.END)
        self.result_text.update()



    def on_quit(self):
        if self.code_modified:
            ans = messagebox.askyesnocancel(
                "வெளியேறு", "குறியீடு மாற்றங்கள் சேமிக்கப்படவில்லை. சேமிக்க விருகிறீர்களா?"
            )
            if ans is True:
                self.save_file()
                self.root.destroy()   # close only this window
            elif ans is False:
                self.root.destroy()   # close only this window
            # Cancel (None) → do nothing
        else:
            if messagebox.askyesno("வெளியேறு", "நிச்சயமாக வெளியேற விரும்புகிறீர்களா ?"):
                self.root.destroy() 
 
# ---------- Start IDE ----------
if __name__=="__main__":
    root = tk.Tk()
    ARAMWindow(root)
    root.mainloop()
