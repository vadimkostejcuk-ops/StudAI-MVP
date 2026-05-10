import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

conn = sqlite3.connect('stud_wallet.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        balance INTEGER DEFAULT 0,
        language TEXT DEFAULT 'en'
    )
''')
conn.commit()

def init_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance, language) VALUES (?, 0, 'en')", (user_id,))
    conn.commit()

def add_stud(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 0

def set_language(user_id, lang):
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()

def get_language(user_id):
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 'en'

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
user_sessions = {}

def get_system_prompt(lang):
    prompts = {
        'en': (
            "You are a strict tutor. "
            "RULE 1 (STOP GENERATING): When explaining, set up the formula, plug in the numbers, and STOP. DO NOT calculate the final answer yourself. Ask the user to calculate it. "
            "RULE 2: If the user provides the CORRECT answer, praise them and MUST append the [SUCCESS] tag at the very end. "
            "RULE 3: If the answer is WRONG, point out the error. Do NOT use [SUCCESS]. "
            "RULE 4 (FORMATTING): NEVER use the caret symbol (^) for exponents. Use Unicode superscripts exclusively (e.g., x², 2³, ⁴)."
        ),
        'ru': (
            "Ты строгий преподаватель. "
            "ПРАВИЛО 1 (СТОП-КРАН): Когда объясняешь задачу, напиши формулу, подставь числа и НЕМЕДЛЕННО ОСТАНОВИСЬ. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать финальный ответ или вычислять его в твоем сообщении. Заставь студента посчитать результат. "
            "ПРАВИЛО 2: Если студент написал ПРАВИЛЬНЫЙ ответ, похвали и ОБЯЗАТЕЛЬНО добавь тег [SUCCESS] в самый конец. "
            "ПРАВИЛО 3: Если ответ неверный, укажи на ошибку. Тег [SUCCESS] использовать запрещено. "
            "ПРАВИЛО 4 (ФОРМАТИРОВАНИЕ): КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать символ '^' для степеней (например x^2). Используй исключительно юникод-символы верхнего регистра: ², ³, ⁴, ⁿ (например: x², 2³). Пиши только на грамотном русском."
        ),
        'ua': (
            "Ти суворий викладач. "
            "ПРАВИЛО 1 (СТОП-КРАН): Коли пояснюєш задачу, напиши формулу, підстав числа і НЕГАЙНО ЗУПИНИСЬ. КАТЕГОРИЧНО ЗАБОРОНЕНО писати фінальну відповідь або обчислювати її у твоєму повідомленні. Змусь студента порахувати результат. "
            "ПРАВИЛО 2: Якщо студент написав ПРАВИЛЬНУ відповідь, похвали і ОБОВ'ЯЗКОВО додай тег [SUCCESS] у самий кінець. "
            "ПРАВИЛО 3: Якщо відповідь неправильна, вкажи на помилку. Тег [SUCCESS] використовувати заборонено. "
            "ПРАВИЛО 4 (ФОРМАТУВАННЯ): КАТЕГОРИЧНО ЗАБОРОНЕНО використовувати символ '^' для степенів (наприклад x^2). Використовуй виключно юнікод-символи верхнього регістру: ², ³, ⁴, ⁿ (наприклад: x², 2³). Пиши тільки чистою українською."
        )
    }
    return prompts.get(lang, prompts['en'])

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="Українська 🇺🇦", callback_data="lang_ua")]
    ])
    
    await message.answer(
        "Welcome to StudAI! 🚀\nSelect your language / Выберите язык / Оберіть мову:",
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith('lang_'))
async def lang_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split('_')[1]
    
    set_language(user_id, lang)
    user_sessions[user_id] = [{"role": "system", "content": get_system_prompt(lang)}]
    
    balance = get_balance(user_id)

    welcome_texts = {
        'en': f"Language set to English! 🇬🇧\nYour balance: {balance} $STUD 🪙\nSend me a task, let's fly!",
        'ru': f"Язык установлен на Русский! 🇷🇺\nТвой баланс: {balance} $STUD 🪙\nСкидывай задачу, полетели!",
        'ua': f"Мову встановлено на Українську! 🇺🇦\nТвій баланс: {balance} $STUD 🪙\nСкидай задачу, полетіли!"
    }
    
    await callback.message.edit_text(welcome_texts[lang])
    await callback.answer()

@dp.message()
async def handle_prompt(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    lang = get_language(user_id)
    
    if user_id not in user_sessions:
        user_sessions[user_id] = [{"role": "system", "content": get_system_prompt(lang)}]
        
    user_sessions[user_id].append({"role": "user", "content": message.text})

    wait_texts = {'en': "⏳ Thinking...", 'ru': "⏳ Думаю...", 'ua': "⏳ Думаю..."}
    wait_msg = await message.answer(wait_texts[lang])

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_sessions[user_id]
        )
        
        bot_reply = response.choices[0].message.content
        
        if "[SUCCESS]" in bot_reply:
            bot_reply = bot_reply.replace("[SUCCESS]", "").strip()
            user_sessions[user_id].append({"role": "assistant", "content": bot_reply})
            await wait_msg.delete()
            await message.answer(bot_reply)
            
            add_stud(user_id, 5)
            new_balance = get_balance(user_id)
            
            success_texts = {
                'en': f"✅ Task solved! +5 $STUD earned!\nBalance: {new_balance} 🪙",
                'ru': f"✅ Задача решена! +5 $STUD начислено!\nБаланс: {new_balance} 🪙",
                'ua': f"✅ Задачу вирішено! +5 $STUD нараховано!\nБаланс: {new_balance} 🪙"
            }
            await message.answer(success_texts[lang])
        else:
            user_sessions[user_id].append({"role": "assistant", "content": bot_reply})
            await wait_msg.delete()
            await message.answer(bot_reply)
            
    except Exception as e:
        if wait_msg: await wait_msg.delete()
        await message.answer("⚠️ Error / Ошибка / Помилка. Try again later.")
        print(f"Log Error [{user_id}]: {e}")

async def main():
    print("🚀 StudAI v2: Multilanguage Edition Launched!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
