# NEXUS ARCADE — Underground Retro Gaming

A comprehensive, dual-engine gaming platform combining a sleek web-based arcade dashboard with standalone Python-powered interactive games. The platform features a unified experience for tracking stats, achievements, and playing multiple mini-games across both web and desktop environments.

## Overview
**NEXUS ARCADE** is a hybrid application. It utilizes a modern, gritty neon HTML/CSS/JS dashboard (`index.html`) for high-level interaction, game launching, and web-based gameplay, while leveraging Pygame for high-performance 2D standalone gaming experiences.

---
NOTE : "The icons in the top right are not functional , because it is a future scope and there is no Login page for this platform because it is a open source game application for users to play and enjoy."

## Functional Structure

### 1. NEXUS ARCADE Web Platform (`index.html`)
- **Cyberpunk / Underground Aesthetic**: Highly polished dark mode UI with neon accents, dynamic grids, and responsive layouts.
- **Embedded Web Games**: Play right in the browser!
    - **Chase Master**: A canvas-based evasion game featuring vision-cone AI, stamina mechanics, coins, and a highly robust input system (supports WASD, Arrow Keys, and a built-in interactive on-screen D-Pad to prevent iframe focus-loss).
    - **Memory Matrix**: A fast-paced tile-matching game with timer, move tracking, and scalable difficulty (Easy, Medium, Hard).
- **Game Selection Hub**: A centralized, filtering-enabled interface to launch different gaming modules directly in an overlay.

### 2. Standalone Python Mini-Games
#### **Chase Master - Enhanced Edition (`chasing_game_enhanced.py`)**
- **Objective**: Avoid diverse enemy types while collecting coins in a Pygame environment.
- **Advanced Mechanics**: 
    - **Multiple Enemy Types**: Trackers, Tanks, Ghosts, and Bouncers.
    - **Power-up System**: Shields, Invincibility, Teleportation, and multipliers.
    - **Sound Engine**: Procedural sound generation for immersive feedback.
    - **Save System**: Local JSON-based high score tracking (`chase_master_save.json`).

---

## Recent Updates & Fixes
- **Robust Web Inputs**: Re-engineered keyboard event listeners bound to the `window` to prevent focus loss in IDEs and iframes.
- **On-Screen D-Pad**: Added an interactive mobile-friendly directional pad to `index.html` for Chase Master, ensuring movement works regardless of keyboard environment.
- **Custom Game Logos**: The web dashboard now pulls visually distinct game logos directly from the `assets/` folder.

---

## Project Structure
```text
Ai/
├── .venv/                     # Python Virtual Environment
├── assets/                    # Image assets (banner.png, chase-logo.png, etc.)
├── chasing_game_enhanced.py   # Advanced standalone Pygame module
├── game_platform_hub.py       # Integrated Python Hub Logic
├── index.html                 # Main NEXUS ARCADE Web Platform (Start Here)
├── memory-card-game.html      # Standalone HTML Memory Game
├── write_html.py              # Utility script for HTML generation
└── README.md                  # Documentation
```

---

## Setup & Installation

### 1. Web Arcade (Recommended)
Simply open `index.html` in any modern web browser (Chrome, Firefox, Edge). No installation required!
- **Controls**: Use `WASD` or `Arrow Keys` (or the on-screen D-Pad) to move. Use `Shift` to sprint.

### 2. Python Standalone Games
- **Prerequisites**: Python 3.10+, Git.
```powershell
# Navigate to project
cd Ai

# Setup Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate

# Install Dependencies
pip install pygame-ce numpy

# Launch Python Games
python chasing_game_enhanced.py
# OR
python game_platform_hub.py
```

---

## License
This project is for educational and entertainment purposes.
