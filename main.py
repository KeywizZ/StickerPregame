import json, os, random, sys
import tkinter as tk
from tkinter import ttk

# pip install pillow
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

DATA_JSON = "data.json"
CONFIG_FILENAME = "config.json"
APP_ICON = "assets/name-sticker-goblin.ico"

WINDOW_W = 980
WINDOW_H = 640
SLOT_W = 190
SLOT_H = 280
RESULT_W = 320
RESULT_H = 380
THUMB_SIZE = (SLOT_W - 12, SLOT_H - 12)

THEMES = {
    "light": {
        "bg": "#f4f4f8",
        "header": "#ffffff",
        "surface": "#ffffff",
        "surface_alt": "#ececf2",
        "border": "#d4d4dc",
        "text": "#1a1a22",
        "text_muted": "#6b6b78",
        "accent": "#6d28d9",
        "accent_hover": "#7c3aed",
        "accent_text": "#ffffff",
        "slot_bg": "#f0f0f6",
        "result_bg": "#fafafc",
        "winner": "#059669",
        "pill_track": "#ececf2",
        "pill_active": "#6d28d9",
        "pill_active_text": "#ffffff",
        "pill_inactive_text": "#6b6b78",
        "info_bg": "#ececf2",
        "info_fg": "#6b6b78",
        "info_hover_bg": "#6d28d9",
        "info_hover_fg": "#ffffff",
        "tooltip_bg": "#ffffff",
        "tooltip_fg": "#1a1a22",
        "tooltip_border": "#d4d4dc",
    },
    "dark": {
        "bg": "#12121a",
        "header": "#1a1a26",
        "surface": "#1e1e2a",
        "surface_alt": "#262636",
        "border": "#3a3a4e",
        "text": "#ececf2",
        "text_muted": "#9898a8",
        "accent": "#8b5cf6",
        "accent_hover": "#a78bfa",
        "accent_text": "#ffffff",
        "slot_bg": "#16161f",
        "result_bg": "#181822",
        "winner": "#34d399",
        "pill_track": "#262636",
        "pill_active": "#8b5cf6",
        "pill_active_text": "#ffffff",
        "pill_inactive_text": "#9898a8",
        "info_bg": "#262636",
        "info_fg": "#9898a8",
        "info_hover_bg": "#8b5cf6",
        "info_hover_fg": "#ffffff",
        "tooltip_bg": "#1e1e2a",
        "tooltip_fg": "#ececf2",
        "tooltip_border": "#3a3a4e",
    },
}


# -- Path helpers --
def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)


def user_config_path() -> str:
    appdata = os.environ.get("APPDATA")
    if appdata:
        config_dir = os.path.join(appdata, "StickerGoblin")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, CONFIG_FILENAME)
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, CONFIG_FILENAME)


def load_config() -> dict:
    path = user_config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_config(data: dict) -> None:
    path = user_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


class HoverTooltip:
    def __init__(self, widget: tk.Widget, theme_manager: "ThemeManager"):
        self.widget = widget
        self.theme = theme_manager
        self.tip_window: tk.Toplevel | None = None
        self.text = ""
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def set_text(self, text: str):
        self.text = text

    def _show(self, _event=None):
        if not self.text:
            return
        self._hide()
        c = THEMES[self.theme.mode]
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x - 120}+{y}")

        frame = tk.Frame(
            tw,
            bg=c["tooltip_bg"],
            highlightbackground=c["tooltip_border"],
            highlightthickness=1,
            padx=10,
            pady=8,
        )
        frame.pack()
        lbl = tk.Label(
            frame,
            text=self.text,
            justify="left",
            bg=c["tooltip_bg"],
            fg=c["tooltip_fg"],
            font=("Segoe UI", 9),
        )
        lbl.pack()
        self.theme.register_tooltip(tw, frame, lbl)

    def _hide(self, _event=None):
        if self.tip_window:
            self.theme.unregister_tooltip(self.tip_window)
            self.tip_window.destroy()
            self.tip_window = None


class CircleInfoButton(tk.Canvas):
    SIZE = 22

    def __init__(self, parent, theme_manager: "ThemeManager"):
        super().__init__(
            parent,
            width=self.SIZE,
            height=self.SIZE,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.theme = theme_manager
        self._hover = False
        self.theme.register_info_button(self)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None):
        self._hover = True
        self.redraw()

    def _on_leave(self, _event=None):
        self._hover = False
        self.redraw()

    def redraw(self):
        c = THEMES[self.theme.mode]
        self.configure(bg=c["surface"])
        self.delete("all")
        fill = c["info_hover_bg"] if self._hover else c["info_bg"]
        fg = c["info_hover_fg"] if self._hover else c["info_fg"]
        pad = 1
        self.create_oval(
            pad,
            pad,
            self.SIZE - pad,
            self.SIZE - pad,
            outline=c["border"],
            fill=fill,
            width=1,
        )
        self.create_text(
            self.SIZE // 2,
            self.SIZE // 2,
            text="i",
            fill=fg,
            font=("Segoe UI", 9, "bold"),
        )


class PillToggle(tk.Frame):
    def __init__(self, parent, theme_manager: "ThemeManager", on_change):
        super().__init__(parent, bd=0, highlightthickness=0)
        self.theme = theme_manager
        self.on_change = on_change
        self._segments: dict[str, tk.Label] = {}

        for mode, label in (("light", "Light"), ("dark", "Dark")):
            seg = tk.Label(
                self,
                text=label,
                font=("Segoe UI", 9, "bold"),
                padx=14,
                pady=5,
                cursor="hand2",
            )
            seg.pack(side="left")
            seg.bind("<Button-1>", lambda _e, m=mode: self._select(m))
            self._segments[mode] = seg

        self.theme.register_pill(self)
        self.update_visual()

    def _select(self, mode: str):
        if mode != self.theme.mode:
            self.on_change(mode)

    def update_visual(self):
        c = THEMES[self.theme.mode]
        self.configure(bg=c["pill_track"])
        for mode, seg in self._segments.items():
            if mode == self.theme.mode:
                seg.configure(
                    bg=c["pill_active"],
                    fg=c["pill_active_text"],
                )
            else:
                seg.configure(
                    bg=c["pill_track"],
                    fg=c["pill_inactive_text"],
                )


class ThemeManager:
    def __init__(self, root: tk.Tk, initial_mode: str = "light"):
        self.root = root
        self.mode = initial_mode if initial_mode in THEMES else "light"
        self.style = ttk.Style(root)
        self.style.theme_use("clam")
        self._widgets: dict[str, list] = {
            "text_areas": [],
            "tk_frames": [],
            "slot_frames": [],
            "slot_labels": [],
            "pills": [],
            "info_buttons": [],
            "tooltips": [],
        }

    def register_text(self, widget: tk.Text):
        self._widgets["text_areas"].append(widget)

    def register_frame(self, widget: tk.Frame, kind: str = "tk_frames"):
        self._widgets[kind].append(widget)

    def register_slot_label(self, widget: tk.Label):
        self._widgets["slot_labels"].append(widget)

    def register_pill(self, widget: PillToggle):
        self._widgets["pills"].append(widget)

    def register_info_button(self, widget):
        self._widgets["info_buttons"].append(widget)

    def register_tooltip(self, window: tk.Toplevel, frame: tk.Frame, label: tk.Label):
        self._widgets["tooltips"].append((window, frame, label))
        self._apply_tooltip(window, frame, label)

    def unregister_tooltip(self, window: tk.Toplevel):
        self._widgets["tooltips"] = [
            t for t in self._widgets["tooltips"] if t[0] is not window
        ]

    def set_mode(self, mode: str) -> str:
        if mode in THEMES:
            self.mode = mode
            self.apply()
            save_config({"theme": self.mode})
        return self.mode

    def toggle(self) -> str:
        return self.set_mode("dark" if self.mode == "light" else "light")

    def _apply_tooltip(self, _window, frame: tk.Frame, label: tk.Label):
        c = THEMES[self.mode]
        frame.configure(bg=c["tooltip_bg"], highlightbackground=c["tooltip_border"])
        label.configure(bg=c["tooltip_bg"], fg=c["tooltip_fg"])

    def apply(self):
        c = THEMES[self.mode]
        s = self.style

        self.root.configure(bg=c["bg"])

        s.configure(".", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10))
        s.configure("TFrame", background=c["bg"])
        s.configure("Header.TFrame", background=c["header"])
        s.configure("Surface.TFrame", background=c["surface"])
        s.configure("Card.TFrame", background=c["surface"], relief="flat")
        s.configure("Footer.TFrame", background=c["bg"])

        s.configure("TLabel", background=c["bg"], foreground=c["text"])
        s.configure("Header.TLabel", background=c["header"], foreground=c["text"], font=("Segoe UI", 20, "bold"))
        s.configure("Subtitle.TLabel", background=c["header"], foreground=c["text_muted"], font=("Segoe UI", 10))
        s.configure("Section.TLabel", background=c["surface"], foreground=c["text"], font=("Segoe UI", 11, "bold"))
        s.configure("Muted.TLabel", background=c["bg"], foreground=c["text_muted"], font=("Segoe UI", 9))

        s.configure(
            "Accent.TButton",
            background=c["accent"],
            foreground=c["accent_text"],
            borderwidth=0,
            focuscolor=c["accent"],
            font=("Segoe UI", 11, "bold"),
            padding=(24, 12),
        )
        s.map(
            "Accent.TButton",
            background=[("active", c["accent_hover"]), ("disabled", c["border"])],
            foreground=[("disabled", c["text_muted"])],
        )

        for txt in self._widgets["text_areas"]:
            txt.configure(
                bg=c["result_bg"],
                fg=c["text"],
                insertbackground=c["text"],
                selectbackground=c["accent"],
                selectforeground=c["accent_text"],
                relief="flat",
                highlightthickness=1,
                highlightbackground=c["border"],
                highlightcolor=c["accent"],
            )
            txt.tag_configure("winner", foreground=c["winner"], font=("Segoe UI", 10, "bold"))
            txt.tag_configure("heading", foreground=c["text"], font=("Segoe UI", 10, "bold"))
            txt.tag_configure("muted", foreground=c["text_muted"])

        for fr in self._widgets["tk_frames"]:
            fr.configure(bg=c["border"])

        for fr in self._widgets["slot_frames"]:
            fr.configure(bg=c["bg"], highlightthickness=0)

        for lbl in self._widgets["slot_labels"]:
            lbl.configure(bg=c["bg"], fg=c["text_muted"])

        for pill in self._widgets["pills"]:
            pill.update_visual()

        for btn in self._widgets["info_buttons"]:
            if hasattr(btn, "redraw"):
                btn.redraw()

        for _window, frame, label in self._widgets["tooltips"]:
            self._apply_tooltip(_window, frame, label)


class StickerGoblinApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sticker Goblin")
        self._set_window_icon()
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WINDOW_W) // 2
        y = (self.winfo_screenheight() - WINDOW_H) // 2
        self.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

        saved_theme = load_config().get("theme", "light")
        self.theme = ThemeManager(self, initial_mode=saved_theme)

        # Header
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.pack(fill="x")

        title_block = ttk.Frame(header, style="Header.TFrame")
        title_block.pack(side="left", fill="x", expand=True)
        ttk.Label(title_block, text="Sticker Goblin", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            title_block,
            text="Pick three cards — highest vowel count wins!",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        self.pill_toggle = PillToggle(header, self.theme, self._on_theme_change)
        self.pill_toggle.pack(side="right")

        sep = tk.Frame(self, height=1)
        sep.pack(fill="x")
        self.theme.register_frame(sep)

        # Content
        main = ttk.Frame(self, padding=(20, 16))
        main.pack(fill="x")

        # Left: sticker slots
        left = ttk.Frame(main)
        left.pack(side="left", padx=(0, 16))

        ttk.Label(left, text="Your picks", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            left,
            text="Press the button to draw three sheets",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        slots = ttk.Frame(left)
        slots.pack()

        self.img_labels = []
        self.slot_frames = []
        for i in range(3):
            outer = tk.Frame(slots, width=SLOT_W, height=SLOT_H, bd=0, highlightthickness=0)
            outer.pack(side="left", padx=(0 if i == 0 else 6, 0))
            outer.pack_propagate(False)
            self.theme.register_frame(outer, "slot_frames")

            lbl = tk.Label(outer, text="", anchor="center", bd=0, highlightthickness=0)
            lbl.pack(fill="both", expand=True)
            self.theme.register_slot_label(lbl)
            self.img_labels.append(lbl)
            self.slot_frames.append(outer)

        # Right: results panel
        right_outer = tk.Frame(main, width=RESULT_W, height=RESULT_H + 60, padx=1, pady=1)
        right_outer.pack(side="right")
        right_outer.pack_propagate(False)
        self.theme.register_frame(right_outer)

        right = ttk.Frame(right_outer, style="Surface.TFrame", padding=14, width=RESULT_W, height=RESULT_H + 60)
        right.pack(fill="both")
        right.pack_propagate(False)

        results_header = ttk.Frame(right, style="Surface.TFrame")
        results_header.pack(fill="x")

        ttk.Label(results_header, text="Results", style="Section.TLabel").pack(side="left", anchor="w")

        self.info_btn = CircleInfoButton(results_header, self.theme)
        self.info_tooltip = HoverTooltip(self.info_btn, self.theme)
        self.last_roll_info = ""

        ttk.Label(right, text="Words and vowel counts from your draw", style="Muted.TLabel").pack(
            anchor="w", pady=(2, 8)
        )

        self.result = tk.Text(
            right,
            height=20,
            width=34,
            wrap="word",
            font=("Segoe UI", 10),
            padx=10,
            pady=10,
            state="disabled",
            cursor="arrow",
        )
        self.result.pack()
        self.theme.register_text(self.result)

        # Footer
        footer = ttk.Frame(self, style="Footer.TFrame", padding=(20, 14))
        footer.pack(fill="x")

        self.pick_btn = ttk.Button(
            footer,
            text="Press to get stickers!",
            style="Accent.TButton",
            command=self.on_press,
        )
        self.pick_btn.pack()

        self.theme.apply()

        # State
        self.animating = False
        self.cards = []
        self.sheet_images = {}
        self._info_visible = False

        self._load_cards(DATA_JSON)
        self._clear_slots()

        if not PIL_AVAILABLE:
            self._write_result(
                "Pillow not found. Install with: pip install pillow\n"
                "You can still test UI; images will appear later."
            )

    def _set_window_icon(self):
        icon_path = resource_path(APP_ICON)
        if not os.path.isfile(icon_path):
            return
        try:
            self.iconbitmap(default=icon_path)
        except Exception:
            if PIL_AVAILABLE:
                try:
                    self._app_icon = ImageTk.PhotoImage(Image.open(icon_path))
                    self.iconphoto(True, self._app_icon)
                except Exception:
                    pass

    def _on_theme_change(self, mode: str):
        self.theme.set_mode(mode)

    def _show_info_btn(self):
        if not self._info_visible:
            self.info_btn.pack(side="right", anchor="e")
            self._info_visible = True

    def _hide_info_btn(self):
        if self._info_visible:
            self.info_btn.pack_forget()
            self._info_visible = False

    def _build_roll_info(self, chosen_cards: list) -> str:
        sheets = ", ".join(str(c["sheet"]) for c in chosen_cards)
        lines = [f"Selected sheets: {sheets}", "", "Stickers by sheet:"]
        for card in chosen_cards:
            words = ", ".join(s["word"] for s in card["stickers"])
            lines.append(f"  Sheet {card['sheet']}: {words}")
        return "\n".join(lines)

    def _load_cards(self, json_file: str):
        path = resource_path(json_file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as ex:
            self._write_result(f"Failed to load {json_file}:\n{ex}")
            return

        self.cards = []
        for card in data:
            sheet = card.get("sheet")
            image = card.get("image")
            stickers = card.get("stickers", [])

            if sheet is None or image is None or not isinstance(stickers, list):
                continue

            cleaned = []
            for s in stickers:
                v = s.get("vowels", s.get("Vowels"))
                if "word" in s and v is not None:
                    cleaned.append({"word": s["word"], "vowels": v})
            if not cleaned:
                continue

            self.cards.append({"sheet": sheet, "image": image, "stickers": cleaned})

        if PIL_AVAILABLE:
            for c in self.cards:
                try:
                    img_path = resource_path(c["image"])
                    im = Image.open(img_path)
                    im.thumbnail(THUMB_SIZE, Image.LANCZOS)
                    self.sheet_images[c["sheet"]] = ImageTk.PhotoImage(im)
                except Exception:
                    pass

    def _clear_slots(self):
        for lbl in self.img_labels:
            lbl.configure(image="", text="")
            lbl.image = None

    def _set_label_image(self, lbl: tk.Label, card: dict):
        sheet = card["sheet"]
        if PIL_AVAILABLE and sheet in self.sheet_images:
            pi = self.sheet_images[sheet]
            lbl.configure(image=pi, text="", anchor="center")
            lbl.image = pi
        else:
            lbl.configure(text=f"Sheet {sheet}", image="", anchor="center")
            lbl.image = None

    def on_press(self):
        if self.animating or len(self.cards) < 3:
            return
        self.animating = True
        self.pick_btn.state(["disabled"])
        self._hide_info_btn()

        frames = 14
        delay = 35

        def tick(i=0):
            if i < frames:
                shown = random.sample(self.cards, 3)
                for lbl, card in zip(self.img_labels, shown):
                    self._set_label_image(lbl, card)
                self.after(delay, lambda: tick(i + 1))
            else:
                self.show_result()

        tick()

    def show_result(self):
        chosen_cards = random.sample(self.cards, 3)

        for lbl, card in zip(self.img_labels, chosen_cards):
            self._set_label_image(lbl, card)

        all_words = []
        for card in chosen_cards:
            for s in card["stickers"]:
                all_words.append({"word": s["word"], "vowels": s["vowels"], "sheet": card["sheet"]})

        max_v = max(s["vowels"] for s in all_words)
        winners = [s for s in all_words if s["vowels"] == max_v]
        winner_words = {w["word"] for w in winners}

        self.last_roll_info = self._build_roll_info(chosen_cards)
        self.info_tooltip.set_text(self.last_roll_info)
        self._show_info_btn()

        self.result.configure(state="normal")
        self.result.delete("1.0", "end")

        self.result.insert("end", "Stickers\n", "heading")
        for s in all_words:
            tag = "winner" if s["word"] in winner_words else ""
            self.result.insert("end", f"  {s['word']}", tag)
            self.result.insert("end", f"  —  {s['vowels']} vowels  ", "muted")
            self.result.insert("end", "\n")

        self.result.insert("end", "\n")
        if len(winners) == 1:
            self.result.insert("end", "Top vowel word\n", "heading")
            w = winners[0]
            self.result.insert("end", f"{w['word']}  —  {w['vowels']} vowels", "winner")
        else:
            self.result.insert("end", "Top vowel words (tie)\n", "heading")
            for w in winners:
                self.result.insert("end", f"  {w['word']}  —  {w['vowels']} vowels\n", "winner")

        self.result.configure(state="disabled")

        self.animating = False
        self.pick_btn.state(["!disabled"])

    def _write_result(self, text: str):
        self.result.configure(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("end", text)
        self.result.configure(state="disabled")


if __name__ == "__main__":
    app = StickerGoblinApp()
    app.mainloop()
