import json, os, random, sys, time
from pathlib import Path

import tkinter as tk
from tkinter import ttk

# pip install pillow
try:
    from PIL import Image, ImageTk   
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

DATA_JSON = "data.json"

# -- Packaging helper --
def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)


class StickerGoblinApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sticker Goblin")
        self.geometry("940x560")
        self.minsize(860, 520)

        # Top bar
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill="x")
        ttk.Label(header, text="Sticker Goblin", font=("Segoe UI", 18, "bold")).pack(side="left")

        # Content
        main = ttk.Frame(self, padding=(12, 10))
        main.pack(fill="both", expand=True)

        # Left: image previews
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)

        slots = ttk.Frame(left)
        slots.pack(pady=10)

        self.img_labels = []
        for i in range(3):
            lbl = ttk.Label(slots, text=f"[slot {i+1}]", width=32, anchor="center")
            lbl.pack(side="left", padx=8, pady=8)
            self.img_labels.append(lbl)

        # Right: results
        right = ttk.Frame(main, width=320)
        right.pack(side="right", fill="y")
        ttk.Label(right, text="Result", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.result = tk.Text(right, height=16, width=38, wrap="word")
        self.result.pack(fill="y", pady=(6, 0))
        self.result.configure(state="disabled")

        # Bottom: button
        footer = ttk.Frame(self, padding=12)
        footer.pack(fill="x")
        self.pick_btn = ttk.Button(footer, text="Press to get stickers!", command=self.on_press)
        self.pick_btn.pack()

        # State
        self.animating = False
        self.cards = []          
        self.sheet_images = {}

        # Load data + images, then show placeholders
        self._load_cards(DATA_JSON)
        self._show_placeholders()

        if not PIL_AVAILABLE:
            self._write_result("Pillow not found. Install with: pip install pillow\n"
                               "You can still test UI; images will appear later.")

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

            self.cards.append({
                "sheet": sheet,
                "image": image,
                "stickers": cleaned
            })

        # Preload images if Pillow is available
        if PIL_AVAILABLE:
            for c in self.cards:
                try:
                    img_path = resource_path(c["image"])
                    im = Image.open(img_path)
                    im.thumbnail((500, 300), Image.LANCZOS)
                    self.sheet_images[c["sheet"]] = ImageTk.PhotoImage(im)  # <-- store
                except Exception:
                    # If a specific image fails, skip to text fallback
                    pass

    def _show_placeholders(self):
        shown = random.sample(self.cards, min(3, len(self.cards))) if self.cards else []
        for lbl, card in zip(self.img_labels, shown):
            self._set_label_image(lbl, card)
        for i in range(len(shown), 3):
            self.img_labels[i].config(text=f"[slot {i+1}]")
            self.img_labels[i].image = None

    def _set_label_image(self, lbl: ttk.Label, card: dict):
        sheet = card["sheet"]
        if PIL_AVAILABLE and sheet in self.sheet_images:
            pi = self.sheet_images[sheet]
            lbl.config(image=pi, text="")
            lbl.image = pi
        else:
            lbl.config(text=f"[sheet {sheet}]", image="")
            lbl.image = None

    def on_press(self):
        if self.animating or len(self.cards) < 3:
            return
        self.animating = True
        self.pick_btn.state(["disabled"])

        # Simple shuffle animation
        frames = 14
        delay = 35  # ms

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
        # 1) Pick 3 distinct cards
        chosen_cards = random.sample(self.cards, 3)

        # 2) Show their images
        for lbl, card in zip(self.img_labels, chosen_cards):
            self._set_label_image(lbl, card)

        # 3) Collect 9 words and find the max by 'vowels'
        all_words = []
        for card in chosen_cards:
            for s in card["stickers"]:
                all_words.append({"word": s["word"], "vowels": s["vowels"], "sheet": card["sheet"]})

        max_v = max(s["vowels"] for s in all_words)
        winners = [s for s in all_words if s["vowels"] == max_v]

        # 4) Output
        lines = []
        lines.append("Selected cards (sheets): " + ", ".join(str(c["sheet"]) for c in chosen_cards))
        lines.append("\nStickers from these cards:")
        for s in all_words:
            lines.append(f"- {s['word']} - {s['vowels']} (sheet {s['sheet']})")

        if len(winners) == 1:
            lines.append(f"\nTop vowel word: {winners[0]['word']} - {winners[0]['vowels']}")
        else:
            lines.append("\nTop vowel words (tie):")
            for w in winners:
                lines.append(f"- {w['word']} - {w['vowels']} (sheet {w['sheet']})")

        self._write_result("\n".join(lines))

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
