# Incremental Pulse

A terminal-based incremental adventure game where every action takes **10 seconds**, and every decision shapes your progression.

---

## 🎮 Overview

**Pulse** is a simple but engaging incremental game where the player performs timed actions, gains rewards, and invests them into a **skill tree system**.

---

## 🔁 Core Gameplay Loop

Choose Action → Wait 10s → Gain Rewards → Upgrade Skills → Repeat

- Perform actions
- Earn XP, coins, and materials
- Unlock skills
- Become stronger over time

---

## ⚔️ Actions

Each action takes **10 seconds** and provides different rewards.

### Available Actions

- 💪 Train Strength
- ⛏️ Mine Stone
- 🐍 Hunt Slime
- 🌲 Explore Forest
- 🧠 Study Magic

### Rewards

- ⭐ XP (experience points)
- 💰 Coins (currency)
- 🧱 Materials (resources)

---

## 🌳 Skill Tree

The skill tree allows players to upgrade their abilities and improve efficiency.

### Skill Paths

#### 💥 Strength Path
- Increase damage output

#### 💰 Resource Path
- Boost coin and material gain

#### 📚 XP Path
- Increase XP gain

#### ⚡ Speed Path
- Improve action efficiency
- Potential future cooldown reduction

---

## 🧩 Terminal Interface Example

---
==== 10 Second Quest ====

1.Create player
2.Show player
3.Start action
4.Collect rewards
5.Show inventory
6.Show skill tree
7.Unlock skill
8.Exit


### Action Example
Choose action:

1.Train Strength
2.Mine Stone
3.Hunt Slime

Action started...
Wait 10 seconds...

Action complete!
You gained:
+15 XP
+10 Coins
+3 Materials


---

## 🗂️ Data Storage (CSV)

The game uses CSV files for data persistence.

### players.csv
- player_id
- name
- level
- xp
- coins

### actions.csv
- action_id
- action_name
- duration
- xp_reward
- coin_reward
- resource_reward

### skills.csv
- skill_id
- skill_name
- skill_type
- cost
- bonus_value
- required_skill_id

### inventory.csv
- inventory_id
- player_id
- resource_name
- quantity

---

## 🏗️ Classes

### Player
Handles player data and progression.

### Action
Manages timed actions and rewards.

### SkillTree
Handles skill unlocking and bonuses.

### Inventory
Manages player resources.

---

## 🔧 Features

- ⏱️ Timed actions (10 seconds)
- 📈 Incremental progression
- 🌳 Skill tree system
- 💾 CSV-based data storage
- 🖥️ Terminal interface

---

## 🧪 Functionality Overview

Each class includes CRUD operations and gameplay logic.

### Player (8 functions)
- add_player
- get_players
- get_player_by_id
- update_player
- delete_player
- find_player_by_name
- add_xp
- add_coins

### Action (8 functions)
- add_action
- get_actions
- get_action_by_id
- update_action
- delete_action
- start_action
- complete_action
- filter_actions_by_reward

### SkillTree (8 functions)
- add_skill
- get_skills
- get_skill_by_id
- update_skill
- delete_skill
- unlock_skill
- check_skill_requirements
- get_unlocked_skills

### Inventory (8 functions)
- add_resource
- get_inventory
- get_resource_by_name
- update_resource_quantity
- delete_resource
- collect_reward
- filter_resources
- resource_exists

---

## 🚀 Future Improvements

- 🎲 Random reward bonuses
- 💎 Resource rarity system
- 📈 Level system
- 👹 Boss fights
- 🔓 Unlockable actions
- ♻️ Prestige system

---

## ▶️ Getting Started

```bash
    git clone https://github.com/your-username/10-second-quest.git
    cd 10-second-quest
    python main.py
```


---
## 📄 Project Description

This project is a terminal-based incremental game where the player performs timed actions, earns rewards, and invests them into a skill tree progression system.

## 📜 License
  MIT License



# 💡 "You only have 10 seconds. What will you do with them?"
