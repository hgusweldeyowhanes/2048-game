# 2048

Mobile-style 2048 built with **Python + Kivy**. Neon tiles, dark board, swipe + arrow controls, and a local leaderboard.

## Run (desktop)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Or: setup.bat
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py

# Or: ./setup.sh
```

## Controls

| Input | Action |
|-------|--------|
| Swipe / drag | Move tiles |
| On-screen arrows | Move tiles |
| Keyboard arrows / WASD | Move tiles (desktop) |

## Project layout

```
2048-game/
├── main.py           # App + game logic + neon UI
├── game_utils.py     # Optional helpers (themes, stats)
├── config.json       # Defaults (theme, grid)
├── requirements.txt  # kivy
├── buildozer.spec    # Android APK build
├── Dockerfile        # Optional Linux container
├── setup.bat / .sh   # Local install helpers
└── README.md
```

Runtime data (`leaderboard.json`) is stored in the app user data folder (safe on Android).

## Pre-build checklist

Before `buildozer` / packaging:

- [ ] Game runs on desktop: `python main.py`
- [ ] Swipe and arrows both move tiles
- [ ] Scores save after game over / new game
- [ ] `requirements.txt` lists only what you need (`kivy`)
- [ ] `buildozer.spec` `source.include_patterns` points at `main.py`
- [ ] No `.venv`, docs, or `__pycache__` in the APK (excluded in spec)
- [ ] Optional: add `data/icon.png` + `data/presplash.png`, then uncomment icon lines in `buildozer.spec`

## Android build (Linux / WSL recommended)

Buildozer does **not** run well on native Windows. Use Ubuntu/WSL or a Linux CI VM.

```bash
# In WSL / Linux, from this folder:
pip install buildozer cython
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config \
  zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

buildozer -v android debug
# APK output: ./bin/
```

Install the APK on a device or emulator, then test swipe + leaderboard.

## Docker note

The Dockerfile installs Kivy for Linux. A GUI still needs a display (`DISPLAY` / X11). Prefer desktop `python main.py` for playtesting; use Docker mainly for dependency smoke tests.

## License

Use freely for learning and personal projects.
