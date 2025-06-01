# QuestMaster: Agentic AI for Interactive Storytelling

## 🧭 Overview

**QuestMaster** is a two-phase AI-driven system that assists authors in designing and delivering interactive narrative quests. It integrates **classical planning (PDDL)** with **generative AI (LLMs)** to produce immersive and logically consistent storytelling experiences.

---

## 📌 Phase 1: Story Generation

### 🎯 Objective

Help authors generate a PDDL-modeled adventure by guiding them through an interactive narrative design process using LLM agents.

### 📝 Input

- **Lore Document** containing:
  - **Quest Description**: Initial state, goals, obstacles, and world context
  - **Branching Factor**: Min/max number of choices at each state
  - **Depth Constraints**: Min/max steps to goal

### 🔁 Workflow

1. **PDDL Generation**  
   - Converts the Lore into a `domain.pddl` and `problem.pddl` file.
   - Every line is annotated with natural language comments.
  
2. **Validation with Classical Planner**  
   - Uses tools like **Fast Downward** to ensure a solvable plan exists.

3. **Interactive Refinement Loop (if needed)**  
   - If no valid plan exists:
     - A **Reflection Agent** identifies issues and suggests fixes.
     - The user is engaged via chat to approve changes or provide input.

### ✅ Output

- Validated `domain.pddl` and `problem.pddl` files
- Finalized Lore document (if updated)

---

## 🎮 Phase 2: Interactive Story Game

### 🎯 Objective

Use the output from Phase 1 to build a web-based interactive adventure game.

### 🛠 Workflow

- Generate an HTML-based interface using LLMs
- Incorporate state-based images (optional)
- Render interactive choices and dynamic storytelling

---

## 📦 Deliverables

1. ✅ **Project ZIP**: Full source code and dependencies  
2. 🧾 **Example Quest**:  
   - Input: `Lore Document`  
   - Output: `domain.pddl`, `problem.pddl`, and HTML interface

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/umbertocicciaa/QuestMasterAI.git questmaster
cd questmaster

# (Optional) Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the main script
python main.py
```
