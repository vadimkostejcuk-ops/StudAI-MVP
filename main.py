import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI

# 1. ЗАГРУЗКА ОКРУЖЕНИЯ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. ИНИЦИАЛИЗАЦИЯ КЛИЕНТОВ
client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
user_sessions = {}

# 3. РАБОТА С БАЗОЙ ДАННЫХ (SQLite)
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

# 4. СИСТЕМНЫЕ ПРОМПТЫ (Адаптивный ИИ-Препод)
def get_system_prompt(lang):
    prompts = {
        'en': (
            "You are a friendly, lively, and experienced AI tutor. You can greet the user naturally, chat, and discuss what subject they want to learn. "
            "RULE 1 (TEACHING): When the user gives you a specific problem to solve, NEVER give the final answer. Explain the core concept, write the initial formulas or reactions, do the first steps, and STOP. Ask the user a question so they finish the calculation or logic themselves. "
            "RULE 2 (SUCCESS): If the user answers correctly, praise them warmly and EXACTLY append [SUCCESS] at the very end of your message. "
            "RULE 3 (FORMATTING): Give step-by-step explanations with each step on a new line. Do NOT use markdown headers or titles. Just clean, readable text. "
            "RULE 4 (SYMBOLS): Use Unicode exclusively for exponents (e.g., x², 2³), never use ^."
        ),
        'ru': (
            "Ты дружелюбный, живой и опытный ИИ-репетитор. Ты можешь естественно общаться, здороваться и обсуждать со студентом, какой предмет он хочет учить. "
            "ПРАВИЛО 1 (ОБУЧЕНИЕ): Когда студент дает конкретную задачу, НИКОГДА не пиши финальный ответ. Объясни суть, напиши начальную формулу или реакцию, сделай первые шаги и ОСТАНОВИСЬ. Задай вопрос, чтобы студент сам закончил расчет или сделал вывод. "
            "ПРАВИЛО 2 (SUCCESS): Если студент отвечает правильно, тепло похвали его и ОБЯЗАТЕЛЬНО добавь тег [SUCCESS] в самый конец сообщения. "
            "ПРАВИЛО 3 (ФОРМАТИРОВАНИЕ): Объясняй пошагово, каждый шаг с новой строки. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать заголовки. Только чистый, аккуратный и понятный текст. "
            "ПРАВИЛО 4 (СИМВОЛЫ): Исключительно юникод для степеней (², ³), запрещено использовать '^'."
        ),
        'ua': (
            "Ти доброзичливий, живий і досвідчений ШІ-репетитор. Ти можеш природно спілкуватися, вітатися та обговорювати зі студентом, який предмет він хоче вчити. "
            "ПРАВИЛО 1 (НАВЧАННЯ): Коли студент дає конкретну задачу, НІКОЛИ не пиши фінальну відповідь. Поясни суть, напиши початкову формулу або реакцію, зроби перші кроки і ЗУПИНИСЬ. Постав запитання, щоб студент сам закінчив розрахунок або зробив висновок. "
            "ПРАВИЛО 2 (SUCCESS): Якщо студент відповідає правильно, тепло похвали його і ОБОВ'ЯЗКОВО додай тег [SUCCESS] у самий кінець повідомлення. "
            "ПРАВИЛО 3 (ФОРМАТУВАННЯ): Пояснюй покроково, кожен крок з нового рядка. КАТЕГОРИЧНО ЗАБОРОНЕНО використовувати заголовки. Тільки чистий, акуратний і зрозумілий текст. "
            "ПРАВИЛО 4 (СИМВОЛИ): Виключно юнікод для степенів (², ³), заборонено використовувати '^'."
        )
    }
    return prompts.get(lang, prompts['en'])

# 5. ОБРАБОТКА КОМАНД (МЕНЮ)
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="Українська 🇺🇦", callback_data="lang_ua")]
    ])
    await message.answer("Welcome to StudAI! 🚀\nSelect your language / Выберите язык / Оберіть мову:", reply_markup=kb)

@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    balance = get_balance(user_id)
    lang = get_language(user_id)
    texts = {'en': f"💰 Your balance: {balance} $STUD", 'ru': f"💰 Твой баланс: {balance} $STUD", 'ua': f"💰 Твій баланс: {balance} $STUD"}
    await message.answer(texts.get(lang, texts['en']))

@dp.message(Command("rules"))
async def cmd_rules(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    texts = {
        'en': "📚 *How to earn $STUD:*\n1. Send a task.\n2. I give theory.\n3. YOU solve the final step.\n4. Correct = +5 $STUD!",
        'ru': "📚 *Как заработать $STUD:*\n1. Скинь задачу.\n2. Я дам теорию.\n3. ТЫ решаешь финал.\n4. Верно = +5 $STUD!",
        'ua': "📚 *Як заробити $STUD:*\n1. Скинь задачу.\n2. Я дам теорію.\n3. ТИ вирішуєш фінал.\n4. Вірно = +5 $STUD!"
    }
    await message.answer(texts.get(lang, texts['en']), parse_mode="Markdown")

@dp.message(Command("wallet"))
async def cmd_wallet(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    texts = {'en': "🔗 Web3 Wallet: Integration in progress...", 'ru': "🔗 Web3 Кошелек: В разработке...", 'ua': "🔗 Web3 Гаманець: В розробці..."}
    await message.answer(texts.get(lang, texts['en']))

@dp.message(Command("language"))
async def cmd_language(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="Українська 🇺🇦", callback_data="lang_ua")]
    ])
    await message.answer("Select language / Выберите язык / Оберіть мову:", reply_markup=kb)

# 6. ВЫБОР ЯЗЫКА
@dp.callback_query(F.data.startswith('lang_'))
async def lang_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split('_')[1]
    set_language(user_id, lang)
    user_sessions[user_id] = [{"role": "system", "content": get_system_prompt(lang)}]
    balance = get_balance(user_id)
    welcome_texts = {
        'en': f"Success! 🇬🇧\nBalance: {balance} $STUD\nLet's learn something!",
        'ru': f"Готово! 🇷🇺\nБаланс: {balance} $STUD\nЧто будем учить сегодня?",
        'ua': f"Готово! 🇺🇦\nБаланс: {balance} $STUD\nЩо будемо вчити сьогодні?"
    }
    await callback.message.edit_text(welcome_texts[lang])
    await callback.answer()

# 7. ОСНОВНОЙ ИИ-ОБРАБОТЧИК (Learn-to-Earn)
@dp.message()
async def handle_prompt(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    lang = get_language(user_id)
    
    if user_id not in user_sessions:
        user_sessions[user_id] = [{"role": "system", "content": get_system_prompt(lang)}]
    
    # 1. Добавляем ввод юзера в память (ТО САМОЕ ИСПРАВЛЕНИЕ)
    user_sessions[user_id].append({"role": "user", "content": message.text})
    
    # 2. Обрезаем контекст (Склероз на 10 сообщений + Системный промпт)
    user_sessions[user_id] = [user_sessions[user_id][0]] + user_sessions[user_id][-10:]

    wait_texts = {'en': "⏳ Thinking...", 'ru': "⏳ Думаю...", 'ua': "⏳ Думаю..."}
    wait_msg = await message.answer(wait_texts[lang])

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_sessions[user_id]
        )
        bot_reply = response.choices[0].message.content.strip()
        
        # Защита от пустых ответов
        if not bot_reply:
            if wait_msg: await wait_msg.delete()
            await message.answer("⚠️ Ошибка генерации. Попробуй еще раз!")
            return 

        if "[SUCCESS]" in bot_reply:
            # Награда за правильный ответ
            bot_reply = bot_reply.replace("[SUCCESS]", "").strip()
            user_sessions[user_id].append({"role": "assistant", "content": bot_reply})
            await wait_msg.delete()
            await message.answer(bot_reply)
            
            add_stud(user_id, 5) # Начисляем 5 токенов
            new_balance = get_balance(user_id)
            success_texts = {
                'en': f"✅ Correct! +5 $STUD!\nBalance: {new_balance} 🪙",
                'ru': f"✅ Верно! +5 $STUD начислено!\nБаланс: {new_balance} 🪙",
                'ua': f"✅ Вірно! +5 $STUD нараховано!\nБаланс: {new_balance} 🪙"
            }
            await message.answer(success_texts[lang])
        else:
            # Обычный ответ или подсказка
            user_sessions[user_id].append({"role": "assistant", "content": bot_reply})
            await wait_msg.delete()
            await message.answer(bot_reply)
            
    except Exception as e:
        if wait_msg: await wait_msg.delete()
        await message.answer("⚠️ Connection Error. Try again.")
        print(f"Error [{user_id}]: {e}")

# 8. ЗАПУСК
async def main():
    print("🚀 StudAI v1.0 Production Mode Launched!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
