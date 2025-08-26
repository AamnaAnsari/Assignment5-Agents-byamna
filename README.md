# 🧑‍💻 AI Agent Assignments  

This repository contains three Python-based assignments showcasing **Agentic AI development** with tools, handoffs, and orchestrators.  

## 📂 Assignments Overview  

### 1️⃣ Smart Store Agent  
**File:** `product_suggester.py`  
- Suggests products based on user needs.  
- Example:  
  - Input: `"I have a headache"`  
  - Output: Suggests a medicine and explains why.  

🔹 **Concepts Used:**  
- Intent recognition  
- Product recommendation logic  

---

### 2️⃣ Mood Analyzer with Handoff  
**File:** `mood_handoff.py`  
- Uses **two agents**:  
  - **Agent 1:** Detects the user’s mood (`happy`, `sad`, `stressed`, etc.).  
  - **Agent 2:** If mood is `"sad"` or `"stressed"`, suggests a relaxing activity.  
- Utilizes `Runner.run()` to handle multiple agents.  

🔹 **Concepts Used:**  
- Agent handoff  
- Context-aware responses  

---

### 3️⃣ Country Info Bot (Using Tools)  
**File:** `country_info_toolkit.py`  
- Includes **3 tool agents**:  
  1. Capital Finder (returns the capital of a country)  
  2. Language Finder (returns the official language)  
  3. Population Finder (returns population stats)  
- An **Orchestrator Agent** combines all tools to give a complete response.  

🔹 **Concepts Used:**  
- Tool-based agents  
- Orchestration of multiple agents  

---

## Made by Aamna Ansari.
