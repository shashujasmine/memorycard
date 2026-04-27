# Game Platform Hub - Multi-Game Dashboard

A comprehensive gaming platform combining web-based dashboarding with Python-powered interactive games. The platform features a unified experience for tracking stats, achievements, and playing multiple mini-games.

## Overview
The **Game Platform Hub** is a hybrid application. It utilizes a modern, glassmorphic HTML/CSS/JS dashboard for high-level interaction and statistics, while leveraging Pygame for high-performance 2D gaming experiences.

---

## Functional Structure

### 1. Unified Dashboard (Web)
- **Real-time Statistics**: Tracks player level, total scores, and games played across the platform.
- **Achievement System**: Visual tracking of unlocked rewards and milestones.
- **Game Selection Hub**: A centralized interface to launch different gaming modules.
- **Persistent Storage**: Uses `localStorage` to keep your stats across browser sessions.

### 2. Mini-Games
#### **Memory Card Game (HTML/JS & Python Versions)**
- **Objective**: Match emoji pairs in the shortest time/moves.
- **Features**: Animated card flips, score multiplier for speed, and difficulty scaling.

#### **Chase Master - Enhanced Edition (Python/Pygame)**
- **Objective**: Avoid diverse enemy types while collecting coins.
- **Advanced Mechanics**: 
    - **Multiple Enemy Types**: Trackers, Tanks, Ghosts, and Bouncers.
    - **Power-up System**: Shields, Invincibility, Teleportation, and 2x Coin multipliers.
    - **Sound Engine**: Procedural sound generation for immersive feedback.
    - **Save System**: Local JSON-based high score tracking.

---

## Non-Functional Requirements

| Category | Specification |
| :--- | :--- |
| **Performance** | Pygame modules run at a stable 60 FPS; Web dashboard loads in <1s. |
| **Scalability** | Modular structure allows adding new `.py` or `.html` games with minimal config. |
| **Usability** | Unified control schemes (WASD/Arrows) and glassmorphic UI for premium feel. |
| **Reliability** | Local JSON and localStorage fallbacks ensure game data is never lost during crashes. |
| **Portability** | Cross-platform compatibility (Windows/macOS/Linux) via Python and Web Standards. |

---

## Project Structure
```
Ai/
├── .venv/                     # Python Virtual Environment
├── .gitignore                 # Version control exclusions
├── chasing_game_enhanced.py   # Main Pygame module
├── game_platform_hub.html     # Web Dashboard & HTML Games
├── game_platform_hub.py       # Integrated Hub Logic
├── memory-card-game.html      # Standalone Memory Game
└── README.md                  # Documentation
```

---

## Setup & Installation

### 1. Prerequisites
- **Python 3.10+** (Optimized for 3.14)
- **Git**

### 2. Running the Python Games
```powershell
# Navigate to project
cd Ai

# Setup Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate

# Install Dependencies
pip install pygame-ce numpy

# Launch Game
python chasing_game_enhanced.py
```

### 3. Running the Dashboard
Simply open `game_platform_hub.html` in any modern web browser (Chrome, Firefox, Edge).

---

## Controls
- **Move**: `Arrow Keys` or `WASD`
- **Select/Restart**: `SPACE`
- **Pause/Menu**: `ESC`

---

## License
This project is for educational and entertainment purposes.
