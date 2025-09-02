import json, os, random, sys, time
from pathlib import Path

import tkinter as tk
from tkinter import ttk

# pip install pillow 
try: 
    from PIL import Image, ImageTK
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


# -- Packaging helper -- 
def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)


def load_sheets(json_path: str):
    with open(resource_path(json_path), "r", encoding="utf-8") as f:
        sheets = json.load(f)

    stickerList = []
    for sheet in sheets:
        sheetImgPath = resource_path(sheet["image"])
        for s in sheet["stickers"]:
            word = s["Word"]
            vowels = s["Vowels"]
            stickerList.append({
                "Word": word,
                "Vowels": vowels,
                "sheet": sheet[sheet],
                "image" : sheetImgPath
            })
    return sheets, stickerList


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

        # Left: Do we build an image preview?
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)

        slots = ttk.Frame(left)
        slots.pack(pady=10)

        # Placeholders
        self.img_labels = []
        for i in range(3):
            lbl = ttk.Label(slots, text=f"[slot {i+1}]", width=32, anchor="center")
            lbl.pack(side="left", padx=8, pady=8)
            self.img_labels.append(lbl)

        # Right: results text area
        right = ttk.Frame(main, width=320)
        right.pack(side="right", fill="y")
        ttk.Label(right, text="Result", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.result = tk.Text(right, height=16, width=38, wrap="word")
        self.result.pack(fill="y", pady=(6, 0))
        self.result.configure(state="disabled")

        # Bottom: buttons
        footer = ttk.Frame(self, padding=12)
        footer.pack(fill="x")
        self.pick_btn = ttk.Button(footer, text="Press to get stickers!", command=self.on_press)
        self.pick_btn.pack()

        # State
        self.animating = False
        
        # If PIL is not available, warn
        if not PIL_AVAILABLE: 
            self._write_result("Pillow not found. Install with: pip install pillow\n"
                               "You can still test UI; images will appear later.")

    def on_press(self):
        if self.animating:
            return
        self.animating = True
        self.pick_btn.state(["disabled"])

        # Shuffle animation?
        frames = 12
        delay = 40 

        def tick(i=0):
                if i < frames:
                    for idx, lbl in enumerate(self.img_labels, start=1):
                        lbl.config(text=f"shuffling {i+1}…")
                    self.after(delay, lambda: tick(i + 1))
                else:
                    self.show_result()

        tick()

    def show_result(self):
        # For now, just fake 3 “picks”. We’ll wire JSON + images next.
        words = random.sample(["Eldrazi", "Guacamole", "Tightrope",
                            "Misunderstood", "Trapeze", "Elf"], 3)

        # Update placeholders
        for lbl, w in zip(self.img_labels, words):
            lbl.config(text=w)

        # Vowel count helper (we’ll later use your JSON’s values or compute)
        def count_vowels(s: str) -> int:
            return sum(1 for ch in s if ch.lower() in "aeiouy")

        # total = sum(count_vowels(w) for w in words)
        # lines = ["Your stickers:\n"] + [f"- {w} (vowels: {count_vowels(w)})" for w in words]
        # lines.append(f"\nTotal vowels: {total}")
        # self._write_result("\n".join(lines))

        counts = {w: count_vowels(w) for w in words}
        max_count = max(counts.values())
        candidates = [w for w, c in counts.items() if c == max_count]
        winner = random.choice(candidates)

        self._write_result(f"Top vowels: {winner} (vowels: {counts[winner]})")

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