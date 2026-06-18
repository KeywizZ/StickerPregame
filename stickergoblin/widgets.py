import tkinter as tk

from stickergoblin.config import THEMES


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
