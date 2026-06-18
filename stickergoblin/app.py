import json
import os
import random
import tkinter as tk
from tkinter import ttk

from stickergoblin.config import (
    APP_ICON,
    DATA_JSON,
    RESULT_H,
    RESULT_W,
    SLOT_H,
    SLOT_W,
    THUMB_SIZE,
    WINDOW_H,
    WINDOW_W,
)
from stickergoblin.images import PIL_AVAILABLE, Image, ImageTk
from stickergoblin.paths import load_config, resource_path
from stickergoblin.theme import ThemeManager
from stickergoblin.widgets import CircleInfoButton, HoverTooltip, PillToggle


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
