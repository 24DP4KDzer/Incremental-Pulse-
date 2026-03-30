# 🌀 Pulse: Evolution
> "The light is your life. Don't let the pulse fade."

A high-intensity, top-down survival roguelike built in **Python** and **Pygame**. Navigate a world of encroaching shadows, manage your energy, and evolve through a persistent skill tree.

---

## 🕹️ Core Gameplay
* **The Shroud System:** A dynamic, smooth darkness system where safety only exists within your light's radius.
* **Energy Survival:** Your energy constantly drains. Kill enemies and collect coins to fuel your pulse.
* **Wave Evolution:** Enemies scale in speed, health, and armor every wave.
* **Persistent Saves:** Highscores, currency, and skill levels are saved to `players.csv`.

---

## 🎭 Character Classes
* **Wizard:** Ranged specialist with high-energy projectiles.
* **Shadow:** High-speed assassin with critical strike scaling.
* **Dwarf:** Melee powerhouse featuring a 360° axe swing.

---

## 🌳 Skill Tree Paths
* **💥 Combat:** Boost base damage and critical hit chance.
* **💰 Utility:** Increase gold gain and magnet collection range.
* **⚡ Agility:** Unlock dashing and movement speed buffs.
* **🛡️ Survival:** Enhance max health, armor, and life-regen.

---

## 🛠️ Technical Specs
* **Language:** Python 3.x
* **Library:** Pygame
* **Storage:** CSV-based flat-file database for player progression.
* **Architecture:** Modular class-based design (`Player`, `Enemy`, `SkillTree`, `Boss`).

---

## 🚀 Installation & Play
```bash
# Clone the repo
"git clone [https://github.com/24DP4KDzer/Incremental-Pulse-)"

# Install python 3.12

"winget install -e --id Python.Python.3.12"

#Check the verion

"python --version"

#Install pygame
"python -m pip install pygame"

# Launch the game

"py -3.12 c:\Users\**user**\Documents\Incremental-Pulse-\main.py"