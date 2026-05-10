# StudAI 🚀 — Web3-Powered AI Tutor

**StudAI** is an innovative EdTech solution developed for the **Web3 Resilience Lab**. It transforms the learning experience by turning a standard AI assistant into a strict, Socratic mentor that incentivizes deep learning through blockchain mechanics.

---

## 💡 The Problem
In the era of LLMs, students often use AI to simply "copy-paste" answers, leading to a decline in actual knowledge retention. During times of remote learning and instability, maintaining academic integrity and motivation is more challenging than ever.

## 🛠 The Solution: Proof of Knowledge
StudAI doesn't just give answers. It guides. 
Using a custom **"Proof of Knowledge"** validation algorithm, the bot:
1. Analyzes the task.
2. Provides theory and the initial setup.
3. Stops and forces the user to calculate the final result.
4. Only upon receiving the correct mathematical answer, the system validates the "block" and rewards the user.

---

## 🚀 Key Features
- **LPU-Powered Intelligence:** Integrated with **Groq (Llama 3.3 70B)** for lightning-fast response times.
- **Anti-Gaslighting Logic:** Advanced prompt engineering ensures the AI stays fair and mathematically accurate.
- **$STUD Tokenomics:** A built-in reward system (SQLite-backed MVP) that tracks student progress and "proof of work".
- **Multilingual UI:** Full support for English, Ukrainian, and Russian.
- **Clean Math UI:** Uses Unicode formatting for professional-grade mathematical expressions (e.g., x², 2³).

---

## 💻 Tech Stack
- **Language:** Python 3.10+
- **Framework:** Aiogram 3.x (Asynchronous Telegram API)
- **Engine:** Groq API (Llama-3.3-70b-versatile)
- **Database:** SQLite3 (User balances & sessions)
- **Environment:** Decoupled config via `.env`

---

## 🔧 Installation & Setup

1. **Clone the repo:**
   ```bash
   git clone [https://github.com/vadimkostejcuk-ops/StudAI-MVP.git](https://github.com/vadimkostejcuk-ops/StudAI-MVP.git)
2. Install dependencies:
    ```pip install aiogram openai python-dotenv ```
3. Configure Environment:
    ```Create a .env file with your credentials: ```
     ```TELEGRAM_TOKEN=your_bot_token ```
     ```GROQ_API_KEY=your_groq_key ```
4. Run the bot:
    ```python main.py ```

   Vadim (Vyacheslav) Kosteichuk Electronics Engineer & Web3 Builder Built for the Web3 Resilience Lab grant program.
