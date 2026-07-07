# ARAM IDE with Tkinter (Fullscreen + Multi-window + Thread-safe Input)
# Aram IDE GUI_Version_7.1 (Adds keywords for file handling, switch cases, list/tuple/set and enabling scrolling on left pane)

import AramLexer, AramParser, AramInterpreter
import tkinter as tk
from tkinter import filedialog, messagebox
import sys, time, re, threading, logging, traceback
from tkinter import Menu
import queue

# The global variable to hold the output widget
global_result_text = None

# ---------- Global error handling ----------
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("aram_ide_errors.log", encoding="utf-8"),
        logging.StreamHandler(sys.stderr)
    ]
)


def _format_exc(exc_type, exc_value, exc_tb) -> str:
    return "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

def _handle_uncaught(exc_type, exc_value, exc_tb):
    msg = _format_exc(exc_type, exc_value, exc_tb)
    logging.error(msg)
    if global_result_text:
        global_result_text.insert(tk.END, f"\nUnhandled Error:\n{msg}", "error_msg")
        global_result_text.see(tk.END)
    else:
        print(f"Unhandled Error:\n{msg}", file=sys.stderr)

sys.excepthook = _handle_uncaught

if hasattr(threading, "excepthook"):
    def _thread_excepthook(args):
        _handle_uncaught(args.exc_type, args.exc_value, args.exc_traceback)
    threading.excepthook = _thread_excepthook


# ---------- Compiler Pipeline ----------
def lexer(code):
    lexer = AramLexer.Lexer(code)
    tokens, hasError = lexer.tokenize()
    return None if hasError else tokens

def parser(tokens):
    parser = AramParser.Parser(tokens)
    ast, hasError = parser.parse()
    return None if hasError else ast

def interpreter(ast):
    interpreter = AramInterpreter.Interpreter(ast)
    res, hasError = interpreter.interpret()
    return None if hasError else res

def compile_run_helper(code: str, input_callback=None) -> str:
    try:
        lex = lexer(code)
        if lex is None:
            raise Exception("சொற்றொடர் பிழை (Syntax Error)")

        parse = parser(lex)
        if parse is None:
            raise Exception("கட்டமைப்புப் பிழை (Parse Error)")

        # --- safe input() override ---
        def aram_input(prompt=""):
            if input_callback:
                return input_callback(prompt)
            else:
                return input(prompt)

        import builtins
        old_input = builtins.input
        builtins.input = aram_input

        res = None
        try:
            res = interpreter(parse)
        finally:
            builtins.input = old_input

        return str(res) if res is not None else ""

    except Exception as e:
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        return f"IDE பிழை (IDE Error):\n{tb}"


# ---------- Tamil → English Keyword Map ----------
# A dictionary to map Tamil keywords to their English counterparts
TAMIL_TO_ENGLISH = {
    # Logical Operators
    "மற்றும்": "and",
    "அல்லது": "or",
    "இல்லை": "not",
    "உண்மை": "true",
    "பொய்": "false",
    
    # I/O Keywords
    "காட்டு": "print",
    "பெறு": "input",
    
    # Loop Keywords
    "உண்மைவரை": "while",
    "சுற்று": "for",
    "முடி": "end",
    
    # Condition Keywords
    "எனில்": "if",
    "பிறஎனில்": "elif",
    "பொய்எனில்": "else",
    "தேர்வு": "switch",
    "பிரிவு": "case",
    "இயல்பு": "default",
    
    # Function Keywords
    "செய்": "def",
    "கொடு": "return",
    "உடை": "break",
    "தொடர்": "continue",
    
    # Import
    "சேர்": "import",
    
    # Data Types
    "முழுஎண்": "int",
    "புள்ளிஎண்": "float",
    "வாக்கியம்": "string",
    "வகை": "type",
    
    # Exit
    "வெளியேறு()": "exit()",
    
    # Exceptional Handling
    "முயற்சி": "try",
    "தவிர": "except",
    "முடிவில்": "finally",
    
    # List/Set/Tuple
    "பட்டியல்_உருவாக்கு": "list creation",
    "தொகுப்பு_உருவாக்கு": "tuple creation",
    "கணம்_உருவாக்கு": "set creation",
    "பிரி": "slicing",
    "இணை": "concatenate",
    "தொடர்": "multiples(*n)",
    "நீளம்": "length",
    "நீக்கு": "remove",
    "உறுப்பு_சேர்": "append",
    "உள்ளது": "in",
    
    # File Handling
    "திற": "open",
    "நிறுத்து": "seek",
    "படி": "read",
    "எழுது": "write",
    "மூடு": "close",
    "துவக்கம்": "rewind",
}

ENGLISH_TO_TAMIL = {v: k for k, v in TAMIL_TO_ENGLISH.items() if v}

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
            "சுழற்சி": "Loop Keywords",
            "நிபந்தனை": "Conditional Statements",
            "செயல்": "Function Keywords",
            "சேர்": "Import Keywords",
            "தரவு வகைகள்": "Data Types",
            "வெளியேறு": "exit",
            "பிழை கையாளுதல்": "Exception Handling",
            "பட்டியல்/ தொகுப்பு/ கணம்": "List/Tuple/Set Keywords",
            "கொப்பு கையாளுதல்": "File Handling ",
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
        try:
            result = self.tk.call(self._orig, command, *args)
            if command in ("insert", "delete", "replace", "yview"):
                self.event_generate("<<Change>>", when="tail")
            return result
        except tk.TclError as e:
            errmsg = str(e)
            if any(msg in errmsg for msg in [
                "tag doesn't exist",
                "sel",
                "nothing to redo",
                "nothing to undo"
            ]):
                return ""
            else:
                raise


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
        self.output_queue = queue.Queue()

        # Autocomplete state
        self.suggestions_win = None
        self.suggestions_listbox = None
        self.suggestion_items = []
        #self._suppress_popup_once = False  # used after accepting a suggestion

        self._setup_gui()
        self.update_title()
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)

        # ---------- Bindings for autocomplete and auto-replace ----------
        #self.code_text.bind("<KeyRelease>", self._on_key_release, add="+")
        self.code_text.bind("<space>", self._auto_replace_en_to_ta, add="+")
        self.code_text.bind("<Return>", self._auto_replace_en_to_ta, add="+")
        self.code_text.bind("(", self._auto_replace_en_to_ta, add="+")

    # ---------- Title ----------
    def update_title(self):
        if self.current_file:
            filename = self.current_file.split("/")[-1]
            self.root.title(f"அறம் Compiler IDE - {filename}")
        else:
            self.root.title("அறம் Compiler IDE - Untitled.aram")

    # ---------- Direct Input in result pane (prompt) ----------
    def request_input(self, prompt=""):
        input_ready = threading.Event()
        user_value = {"text": None}

        self.result_text.insert(tk.END, prompt)
        self.result_text.see(tk.END)
        self.root.update_idletasks()

        entry = tk.Entry(self.result_text, width=50)
        self.result_text.window_create(tk.END, window=entry)
        entry.focus_set()

        def on_enter(event):
            user_value["text"] = entry.get()
            entry.destroy()
            self.result_text.insert(tk.END, user_value["text"] + "\n")
            self.result_text.see(tk.END)
            input_ready.set()
        
        entry.bind("<Return>", on_enter)

        input_ready.wait()
        return user_value["text"]

    # ---------- Utilities for autocomplete ----------
    @staticmethod
    def _is_word_char(ch: str) -> bool:
        return ch.isalnum() or ch == "_" or ("\u0B80" <= ch <= "\u0BFF")

    def _current_word_range(self):
        idx = self.code_text.index("insert")
        line, col = map(int, idx.split("."))
        line_text = self.code_text.get(f"{line}.0", f"{line}.end")
        n = len(line_text)

        i = col - 1
        while i >= 0 and self._is_word_char(line_text[i]):
            i -= 1
        start_col = i + 1

        j = col
        while j < n and self._is_word_char(line_text[j]):
            j += 1
        end_col = j

        word = line_text[start_col:end_col]
        return word, f"{line}.{start_col}", f"{line}.{end_col}"

    def _close_suggestions(self):
        if self.suggestions_win is not None:
            try:
                self.suggestions_win.destroy()
            except Exception:
                pass
        self.suggestions_win = None
        self.suggestions_listbox = None
        self.suggestion_items = []

    def _place_suggestions(self, at_index: str):
        bbox = self.code_text.bbox(at_index)
        if not bbox:
            x = self.code_text.winfo_rootx() + 40
            y = self.code_text.winfo_rooty() + 20
        else:
            x = self.code_text.winfo_rootx() + bbox[0]
            y = self.code_text.winfo_rooty() + bbox[1] + bbox[3]

        win = tk.Toplevel(self.code_text)
        win.wm_overrideredirect(True)
        win.attributes("-topmost", True)
        win.geometry(f"+{x}+{y}")

        lb = tk.Listbox(win, height=min(7, len(self.suggestion_items)), font=("Courier New", 11))
        lb.pack(fill="both", expand=True)

        for item in self.suggestion_items:
            lb.insert(tk.END, item)

        def accept(_=None):
            try:
                sel = lb.curselection()
                if not sel:
                    return "break"
                choice = lb.get(sel[0])
                word, start, end = self._current_word_range()
                self.code_text.delete(start, end)
                self.code_text.insert(start, choice)
            finally:
                self._suppress_popup_once = True
                self._close_suggestions()
            return "break"

        def move_up(_=None):
            if lb.size() == 0:
                return "break"
            cur = lb.curselection()
            idx = 0 if not cur else max(0, cur[0] - 1)
            lb.selection_clear(0, tk.END)
            lb.selection_set(idx)
            lb.activate(idx)
            return "break"

        def move_down(_=None):
            if lb.size() == 0:
                return "break"
            cur = lb.curselection()
            idx = (cur[0] + 1) if cur else 0
            idx = min(idx, lb.size() - 1)
            lb.selection_clear(0, tk.END)
            lb.selection_set(idx)
            lb.activate(idx)
            return "break"

        lb.bind("<Return>", accept)
        lb.bind("<Tab>", accept)
        lb.bind("<Double-Button-1>", accept)
        lb.bind("<Escape>", lambda e: (self._close_suggestions(), "break"))
        lb.bind("<Up>", move_up)
        lb.bind("<Down>", move_down)

        def on_focus_out(_=None):
            self._close_suggestions()
        win.bind("<FocusOut>", on_focus_out)

        self.suggestions_win = win
        self.suggestions_listbox = lb
        if lb.size() > 0:
            lb.selection_set(0)
            lb.activate(0)

        # keep focus in editor
        self.code_text.focus_set()

        # Tab should accept first suggestion even without lb focus
        self.code_text.bind("<Tab>", lambda e: (lb.selection_clear(0, tk.END),
                                                 lb.selection_set(0),
                                                 lb.activate(0),
                                                 lb.event_generate("<Return>"),
                                                 "break"), add="+")

    def _collect_variables(self):
        text = self.code_text.get("1.0", tk.END)
        vars_found = re.findall(r"(^|[^=!><])\s*([A-Za-z_0-9\u0B80-\u0BFF]+)\s*=", text)
        names = {m[1] for m in vars_found if m[1] not in ("==","", " ")}
        return sorted(names)

    def _build_candidates(self):
        tamil_keys = list(TAMIL_TO_ENGLISH.keys())
        english_keys = [v for v in TAMIL_TO_ENGLISH.values() if v]
        return tamil_keys + english_keys + self._collect_variables()

    def _show_autocomplete(self):
        if self._suppress_popup_once:
            self._suppress_popup_once = False
            self._close_suggestions()
            return

        word, start, end = self._current_word_range()

        # ✅ do not show autocomplete for empty or very short words
        if not word or len(word) < 2:
            self._close_suggestions()
            return

        all_items = self._build_candidates()
        wlow = word.lower()
        items = [s for s in all_items if s.lower().startswith(wlow) and s != word]

        if not items:
            self._close_suggestions()
            return

        self.suggestion_items = items
        self._close_suggestions()
        self._place_suggestions(end)

    def _maybe_close_autocomplete_on_nav(self, keysym: str):
        if keysym in ("Escape", "Left", "Right", "Up", "Down", "Home", "End", "Next", "Prior"):
            self._close_suggestions()

    def _auto_replace_en_to_ta(self, event):
        # skip if autocomplete is open
        if self.suggestions_win is not None:
            return

        word, start, end = self._current_word_range()
        if not word:
            return

        repl = ENGLISH_TO_TAMIL.get(word)
        if repl:
            if event.keysym == "space":
                trigger = " "
            elif event.keysym == "Return":
                trigger = "\n"
            elif event.char == "(":
                trigger = "("
            else:
                trigger = ""

            self.code_text.delete(start, end)
            self.code_text.insert(start, repl + trigger)
            return "break"
        return

    def _on_key_release(self, event):
        # Corrected: We're removing "space" and "Return" from the ignored keys so autocomplete can be triggered.
        if event.keysym in (
            "Escape", "Left", "Right", "Up", "Down", "Home", "End", "Next", "Prior"
        ):
            self._close_suggestions()
            return

        if not event.char.isalnum() and event.char not in ("_",):
            return

        self._show_autocomplete()

    # ---------- GUI setup ----------
    def _setup_gui(self):
        self.code_text = None
        self.english_text = None
        self.result_text = None

        # ---------- Top Toolbar ----------
        top = tk.Frame(self.root, bg="#f7f7f7")
        top.pack(fill="x")
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
            ToolTip(btn, f"({shortcut})")

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
                    # Logical Operators - கருத்து குறிகள்
                    ("கருத்து குறிகள்", [
                        ("மற்றும்", "and"),
                        ("அல்லது", "or"),
                        ("இல்லை", "not"),
                        ("உண்மை", "true"),
                        ("பொய்", "false")
                    ]),
                    
                    # I/O Key Words - உள்ளீடு / வெளியீடு
                    ("உள்ளீடு / வெளியீடு", [
                        ("காட்டு()", "print()"),
                        ("பெறு()", "input()")
                    ]),
                    
                    # Loop Key Words - சுழற்சி
                    ("சுழற்சி", [
                        ("உண்மைவரை()", "while()"),
                        ("சுற்று()", "for()"),
                        ("முடி", "end")
                    ]),
                    
                    # Condition Key Words - நிபந்தனை
                    ("நிபந்தனை", [
                        ("எனில்", "if"),
                        ("பிறஎனில்", "elif"),
                        ("பொய்எனில்", "else"),
                        ("தேர்வு()", "switch()"),
                        ("பிரிவு :", "case"),
                        ("இயல்பு :", "default")
                    ]),
                    
                    # Function Key Words - செயல்
                    ("செயல்", [
                        ("செய்", "func"),
                        ("கொடு", "return"),
                        ("உடை", "break"),
                        ("தொடர்", "continue")
                    ]),

                    # Import
                    ("சேர்", [
                        ("சேர்", "import")
                    ]),
                    
                    # Data Types - தரவு வகைகள்
                    ("தரவு வகைகள்", [
                        ("முழுஎண்()", "int()"),
                        ("புள்ளிஎண்()", "float()"),
                        ("வாக்கியம்()", "string()"),
                        ("வகை()", "type()"),
                    ]),

                    # Exit - வெளியேறு
                    ("வெளியேறு", [
                        ("வெளியேறு()", "exit()")
                    ]),
                   
                    # Exceptional Handling - பிழை கையாளுதல்
                    ("பிழை கையாளுதல்", [
                        ("முயற்சி :", "try"),
                        ("தவிர :", "except"),
                        ("முடிவில் :", "finally")
                    ]),
                    
                    # List/Set/Tuple
                    ("பட்டியல் / தொகுப்பு / கணம்", [
                        ("பட்டியல்_உருவாக்கு()", "list creation()"),
                        ("தொகுப்பு_உருவாக்கு()", "tuple creation()"),
                        ("கணம்_உருவாக்கு()", "set creation()"),
                        ("பிரி()", "slicing()"),
                        ("இணை()", "concatenate()"),
                        ("தொடர்()", "multiples(*n)"),
                        ("நீளம்()", "length()"),
                        ("நீக்கு()", "remove()"),
                        ("உறுப்பு_சேர்()", "append()"),
                        ("உள்ளது()", "in()")
                    ]),
                    
                    # File Handling - கொப்பு கையாளுதல்
                    ("கொப்பு கையாளுதல்", [
                        ("திற()", "open()"),
                        ("நிறுத்து()", "seek()"),
                        ("படி()", "read()"),
                        ("எழுது()", "write()"),
                        ("மூடு()", "close()"),
                        ("துவக்கம்()", "rewind()")
                    ])
                ]
        
        # --- Scrollable left accordion ---
        self.left_frame.config(width=250)   # Fix width of left pane

        canvas = tk.Canvas(self.left_frame, bg="white", highlightthickness=0, width=250)
        scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        scrollable_frame = tk.Frame(canvas, bg="white")
        accordion = Accordion(
            scrollable_frame,
            sections,
            lambda txt: self.code_text.insert(tk.INSERT, txt + " "),
            bg="white"
        )
        accordion.pack(fill="both", expand=True)

        # Create frame inside canvas
        frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Expand scrollable_frame to canvas width
        def _on_canvas_configure(event):
            canvas.itemconfig(frame_window, width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)

        # Update scrollregion when contents change
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)



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

        # Set the global reference
        global global_result_text
        global_result_text = self.result_text

        welcome_msg = (
            ">>வாழ்த்துகள்! நீங்கள் அறம் IDE-யில் இருக்கிறீர்கள்.\n"
            ">>இங்கு உங்கள் குறியீடுகளை எழுதலாம், இயக்கலாம் மற்றும் சேமிக்கலாம்.\n\n"
        )
        self.result_text.insert("1.0", welcome_msg, "welcome_msg")
        self.result_text.tag_config("welcome_msg", foreground="blue", font=("Courier New", 11, "italic"))
        self.result_text.see(tk.END)

        # ---------- Editor update + highlighting + autocomplete combined handler ----------
        def update_editor_and_features(event=None):
            # 1) Syntax mirror & highlighting
            self.code_modified = True
            english_code_local = translate_tamil_to_english(self.code_text.get("1.0", tk.END))
            self.english_text.config(state="normal")
            self.english_text.delete("1.0", tk.END)
            self.english_text.insert("1.0", english_code_local)
            self.english_text.config(state="disabled")

            # Clear old tags
            self.code_text.tag_remove("keyword", "1.0", tk.END)
            self.code_text.tag_remove("string", "1.0", tk.END)
            self.english_text.tag_remove("keyword", "1.0", tk.END)
            self.english_text.tag_remove("string", "1.0", tk.END)

            # Tamil keywords highlight (green)
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

            # Strings highlight (red)
            code_buf = self.code_text.get("1.0", tk.END)
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', code_buf):
                start_index = f"1.0+{match.start()}c"
                end_index = f"1.0+{match.end()}c"
                self.code_text.tag_add("string", start_index, end_index)
            self.code_text.tag_config("string", foreground="red")

            # English pane highlights
            english_keywords = [v for v in TAMIL_TO_ENGLISH.values() if v]
            english_buf = self.english_text.get("1.0", tk.END)
            for word in english_keywords:
                if not word: 
                    continue
                for match in re.finditer(re.escape(word), english_buf, re.IGNORECASE):
                    start_index = f"1.0+{match.start()}c"
                    end_index = f"1.0+{match.end()}c"
                    self.english_text.config(state="normal")
                    self.english_text.tag_add("keyword", start_index, end_index)
                    self.english_text.config(state="disabled")
            self.english_text.tag_config("keyword", foreground="green")
            for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', english_buf):
                start_index = f"1.0+{match.start()}c"
                end_index = f"1.0+{match.end()}c"
                self.english_text.config(state="normal")
                self.english_text.tag_add("string", start_index, end_index)
                self.english_text.config(state="disabled")
            self.english_text.tag_config("string", foreground="red")

            # Line numbers
            line_nums.redraw()
            line_nums_eng.redraw()

            # 2) Autocomplete popup (on "typing" keys only)
            if event is not None:
                ks = event.keysym
                # Suppress on navigation/dismiss keys
                self._maybe_close_autocomplete_on_nav(ks)
                # Show on regular character insertions/backspace/underscore etc.
                if (len(event.char) == 1 and event.char.isprintable()) or ks in ("BackSpace", "underscore"):
                    self._show_autocomplete()

        # Context menu
        self.context_menu = Menu(self.root, tearoff=0, font=("Arial", 10))
        def add_menu_item(menu, text, shortcut=None, command=None):
            if shortcut:
                menu.add_command(label=text, command=command)
                menu.entryconfig("end", accelerator=shortcut)
            else:
                menu.add_command(label=text, command=command)
        add_menu_item(self.context_menu, "புதிய", "Ctrl+N", self.new_file)
        add_menu_item(self.context_menu, "திற", "Ctrl+O", self.open_file)
        add_menu_item(self.context_menu, "சேமி", "Ctrl+S", self.save_file)
        self.context_menu.add_separator()
        add_menu_item(self.context_menu, "வெட்டு", "Ctrl+X", lambda: self.code_text.event_generate("<<Cut>>"))
        add_menu_item(self.context_menu, "நகல்", "Ctrl+C", lambda: self.code_text.event_generate("<<Copy>>"))
        add_menu_item(self.context_menu, "ஒட்டு", "Ctrl+V", lambda: self.code_text.event_generate("<<Paste>>"))
        add_menu_item(self.context_menu, "அழி", "F3", lambda: self.code_text.delete("sel.first","sel.last"))
        self.context_menu.add_separator()
        add_menu_item(self.context_menu, "ரத்து செய்", "Ctrl+Z", lambda: self.code_text.event_generate("<<Undo>>"))
        add_menu_item(self.context_menu, "மீண்டும் செய்", "Ctrl+Y", lambda: self.code_text.event_generate("<<Redo>>"))
        self.context_menu.add_separator()
        add_menu_item(self.context_menu, "அனைத்தையும் தேர்ந்தெடு  ", "Ctrl+A", lambda: self.code_text.tag_add("sel","1.0","end"))
        self.context_menu.add_separator()
        add_menu_item(self.context_menu, "இயக்கு", "F5", self.run_code)
        add_menu_item(self.context_menu, "வெளியேறு", "F4", self.on_quit)

        # Bindings
        self.root.bind("<Button-3>", self.show_context_menu)
        # Combine editor update + autocomplete via add='+'
        self.code_text.bind("<<Change>>", update_editor_and_features, add="+")
        self.code_text.bind("<KeyRelease>", update_editor_and_features, add="+")
        self.english_text.bind("<<Change>>", lambda e: line_nums_eng.redraw(), add="+")
        self.english_text.bind("<Configure>", lambda e: line_nums_eng.redraw(), add="+")
        self.code_text.bind("<Configure>", lambda e: line_nums.redraw(), add="+")
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_file_as())
        self.root.bind("<F5>", lambda e: self.run_code())
        self.root.bind("<Control-l>", lambda e: self.toggle_left())
        self.root.bind("<Control-r>", lambda e: self.toggle_right())
        self.root.bind("<F4>", lambda e: self.on_quit())
        self.root.bind("<F3>", lambda e: self.clear_code())

        # Auto-replace bindings on Space/Return
        self.code_text.bind("<space>", self._auto_replace_en_to_ta, add="+")
        self.code_text.bind("<Return>", self._auto_replace_en_to_ta, add="+")
        # Close suggestions if user clicks elsewhere
        self.code_text.bind("<Button-1>", lambda e: self._close_suggestions(), add="+")

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

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

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

    # ---------- Run code ----------
    def run_code(self):
        src = self.code_text.get("1.0", tk.END).rstrip()
        if not src.strip():
            self.result_text.insert(tk.END, "குறியீடு இல்லை\n")
            return

        filename = self.current_file.split("/")[-1] if self.current_file else "Untitled.aram"
        self.result_text.insert(tk.END, f"\n[இயக்கப்படுகிறது] {filename}\n", "running_msg")
        self.result_text.tag_config("running_msg", foreground="green")
        self.result_text.see(tk.END)

        # Use a queue to pass output from the worker thread to the GUI thread
        output_queue = queue.Queue()

        def run_in_thread():
            output_message = ""
            error_message = ""
            start_time = time.time()
            try:
                # Redirect stdout/stderr to the queue
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                
                class QueueOutput:
                    def write(self, s):
                        output_queue.put(s)
                    def flush(self):
                        pass

                sys.stdout = QueueOutput()
                sys.stderr = QueueOutput()

                # Call the compile_run_helper function
                output_message = compile_run_helper(src, input_callback=self.request_input)

            except SystemExit as e:
                # Catch the SystemExit exception specifically and handle it gracefully
                error_message = f"IDE Status: Program exited with code {e.code}"
                # Signal the main thread to shut down
                output_queue.put('SHUTDOWN_REQUEST')
                return # Exit the thread gracefully
            except Exception as e:
                tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
                error_message = f"IDE பிழை (IDE Error):\n{tb}"
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
                end_time = time.time()
                completion_message = f"[முடிந்தது] {filename} குறியீடு {end_time - start_time:.3f} வினாடிகளில் நிறைவுற்றது\n"

                if output_message and output_message.strip():
                    output_queue.put(output_message + "\n")
                
                if error_message:
                    output_queue.put(error_message + "\n")

                output_queue.put(completion_message)
                output_queue.put(None)  # Sentinel value to stop the poller

        def check_queue():
            try:
                while True:
                    message = output_queue.get_nowait()
                    if message is None:
                        return # Stop checking
                    if message == 'SHUTDOWN_REQUEST':
                        # Received the signal to shut down.
                        self.root.destroy()
                        return
                    
                    # Determine the tag for the message
                    if "பிழை" in message or "Error" in message:
                        tag = "error_msg"
                    elif "[முடிந்தது]" in message:
                        tag = "done_msg" # Use the new yellow tag
                    else:
                        tag = None

                    self.result_text.insert(tk.END, message, tag)
                    self.result_text.see(tk.END)
                    self.result_text.tag_config("error_msg", foreground="red")
                    self.result_text.tag_config("done_msg", foreground="red") # <-- New Tag
                    
            except queue.Empty:
                pass
            
            # Re-schedule the check
            self.root.after(100, check_queue)

        threading.Thread(target=run_in_thread, daemon=True).start()
        check_queue()

    # ---------- Quit ----------
    def on_quit(self):
        self._close_suggestions()
        if self.code_modified:
            ans = messagebox.askyesnocancel(
                "வெளியேறு", "குறியீடு மாற்றங்கள் சேமிக்கப்படவில்லை. சேமிக்க விருகிறீர்களா?"
            )
            if ans is True:
                self.save_file()
                self.root.destroy()
            elif ans is False:
                self.root.destroy()
        else:
            if messagebox.askyesno("வெளியேறு", "நிச்சயமாக வெளியேற விரும்புகிறீர்களா ?"):
                self.root.destroy()

# ---------- Start IDE ----------
if __name__=="__main__":
    try:
        root = tk.Tk()
        ARAMWindow(root)
        root.mainloop()
    except Exception as e:
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logging.error(f"Fatal unhandled error: {tb}")