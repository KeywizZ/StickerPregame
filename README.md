# Sticker Goblin

A small Windows desktop app for picking three random Unfinity name sticker sheets and finding the word with the most vowels.

![Sticker Goblin](assets/unf-107m-name-sticker-goblin.jpg)

## How it works

1. Click **Press to get stickers!**
2. Three random sticker sheets are drawn.
3. Every sticker word from those sheets is listed with its vowel count.
4. The word(s) with the **highest vowel count** win.

## Features

- **Light & dark themes** — toggle with the pill in the header
- **Theme persistence** — your choice is remembered between sessions
- **Results panel** — sticker names, vowel counts, and highlighted winners
- **Info tooltip** — after a roll, hover the **ⓘ** icon in the Results panel to see which sheets were drawn and which stickers came from each
- **Portable `.exe`** — no Python install required

## Download

Grab `StickerGoblin.exe` from the [latest release](https://github.com/YOUR_USERNAME/StickersPregame/releases) and run it.

**Requirements:** Windows 10 or later

## Run from source

### Prerequisites

- Python 3.10+
- [Pillow](https://pypi.org/project/pillow/)

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/StickersPregame.git
cd StickersPregame
python -m venv .venv
.venv\Scripts\activate
pip install pillow
python main.py
