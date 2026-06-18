import tkinter as tk
from tkinter import ttk

from stickergoblin.config import THEMES
from stickergoblin.paths import save_config
from stickergoblin.widgets import PillToggle


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
