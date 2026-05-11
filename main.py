import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
lo  res = cursor.fetchone()
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
            "You are a friendly, lively, and experienced AI tutor. You can greet the user naturally, chat, and discuss what subject they want to learn. "
            "RULE 1 (TEACHING): When the user gives you a specific problem to solve, NEVER give the final answer. Explain the core concept, write the initial formulas or reactions, do the first steps, and STOP. Ask the user a question so they finish the calculation or logic themselves. "
            "RULE 2 (SUCCESS): If the user answers correctly, praise them warmly and EXACTLY append [SUCCESS] at the very end of your message. "
            "RULE 3 (FORMATTING): Give step-by-step explanations with each step on a new line. Just clean, readable text. "
            "RULE 4 (SYMBOLS): Use Unicode exclusively for exponents (e.g., x², 2³), never use ^."
        ),
        'ru': (
            "Ты дружелюбный, живой и опытный ИИ-репетитор. Ты можешь естественно общаться, здороваться и обсуждать со студентом, какой предмет он хочет учить. "
            "ПРАВИЛО 1 (ОБУЧЕНИЕ): Когда студент дает конкретную задачу, НИКОГДА не пиши финальный ответ. Объясни суть, напиши начальную формулу или реакцию, сделай первые шаги и ОСТАНОВИСЬ. Задай вопрос, чтобы студент сам закончил расчет или сделал вывод. "
            "ПРАВИЛО 2 (SUCCESS): Если студент отвечает правильно, тепло похвали его и ОБЯЗАТЕЛЬНО добавь тег [SUCCESS] в самый конец сообщения. "
            "ПРАВИЛО 3 (ФОРМАТИРОВАНИЕ): Объясняй пошагово, каждый шаг с новой строки. Только чистый, аккуратный и понятный текст. "
            "ПРАВИЛО 4 (СИМВОЛЫ): Исключительно юникод для степеней (², ³), запрещено использовать '^'."
        ),
        'ua': (
            "Ти доброзичливий, живий і досвідчений ШІ-репетитор. Ти можеш природно спілкуватися, вітатися та обговорювати зі студентом, який предмет він хоче вчити. "
            "ПРАВИЛО 1 (НАВЧАННЯ): Коли студент дає конкретну задачу, НІКОЛИ не пиши фінальну відповідь. Поясни суть, напиши початкову формулу або реакцію, зроби перші кроки і ЗУПИНИСЬ. Постав запитання, щоб студент сам закінчив розрахунок або зробив висновок. "
            "ПРАВИЛО 2 (SUCCESS): Якщо студент відповідає правильно, тепло похвали його і ОБОВ'ЯЗКОВО додай тег [SUCCESS] у самий кінець повідомлення. "
            "ПРАВИЛО 3 (ФОРМАТУВАННЯ): Пояснюй покроково, кожен крок з нового рядка. Тільки чистий, акуратний і зрозумілий текст. "
            "ПРАВИЛО 4 (СИМВОЛИ): Виключно юнікод для степенів (², ³), заборонено використовувати '^'."
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


@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id) 
    balance = get_balance(user_id)
    lang = get_language(user_id)
    texts = {
        'en': f"💰 Your balance: {balance} $STUD",
        'ru': f"💰 Твой баланс: {balance} $STUD",
        'ua': f"💰 Твій баланс: {balance} $STUD"
    }
    await message.answer(texts.get(lang, texts['en']))

@dp.message(Command("rules"))
async def cmd_rules(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    texts = {
        'en': "📚 *How to earn $STUD:*\n1. Send a math problem.\n2. I give the theory and formula.\n3. YOU calculate the final answer.\n4. If correct, you get +5 $STUD!",
        'ru': "📚 *Как заработать $STUD:*\n1. Отправь мне задачу.\n2. Я распишу теорию и формулу.\n3. ТЫ считаешь финальный ответ.\n4. Если ответ верный, получаешь +5 $STUD!",
        'ua': "📚 *Як заробити $STUD:*\n1. Відправ мені задачу.\n2. Я розпишу теорію та формулу.\n3. ТИ рахуєш фінальну відповідь.\n4. Якщо відповідь правильна, отримуєш +5 $STUD!"
    }
    await message.answer(texts.get(lang, texts['en']), parse_mode="Markdown")

@dp.message(Command("wallet"))
async def cmd_wallet(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    texts = {
        'en': "🔗 Web3 integration with Autheo V2 network is currently in development. Stay tuned!",
        'ru': "🔗 Интеграция Web3 с сетью Autheo V2 находится в разработке. Ожидайте!",
        'ua': "🔗 Інтеграція Web3 з мережею Autheo V2 знаходиться в розробці. Очікуйте!"
    }
    await message.answer(texts.get(lang, texts['en']))

@dp.message(Command("language"))
async def cmd_language(message: types.Message):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="Українська 🇺🇦", callback_data="lang_ua")]
    ])
    await message.answer("Select your language / Выберите язык / Оберіть мову:", reply_markup=kb)



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
    user_sessions[user_id] = [user_sessions[user_id][0]] + user_sessions[user_id][-10:]

    wait_texts = {'en': "⏳ Thinking...", 'ru': "⏳ Думаю...", 'ua': "⏳ Думаю..."}
    wait_msg = await message.answer(wait_texts[lang])

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_sessions[user_id]
        )
        
        bot_reply = response.choices[0].message.content.strip()
        
        
        if not bot_reply:
            if wait_msg: await wait_msg.delete()
            await message.answer("⚠️ Я не смог сгенерировать ответ. Пожалуйста, повторите снова!")
            return 
           
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
    asyncio.run(main())ad_dotenv(ENV_PATH, override=True)

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
            "You are a friendly, lively, and experienced AI tutor. You can greet the user naturally, chat, and discuss what subject they want to learn. "
            "RULE 1 (TEACHING): When the user gives you a specific problem to solve, NEVER give the final answer. Explain the core concept, write the initial formulas or reactions, do the first steps, and STOP. Ask the user a question so they finish the calculation or logic themselves. "
            "RULE 2 (SUCCESS): If the user answers correctly, praise them warmly and EXACTLY append [SUCCESS] at the very end of your message. "
            "RULE 3 (FORMATTING): Give step-by-step explanations with each step on a new line. Just clean, readable text. "
            "RULE 4 (SYMBOLS): Use Unicode exclusively for exponents (e.g., x², 2³), never use ^."
        ),
        'ru': (
            "Ты дружелюбный, живой и опытный ИИ-репетитор. Ты можешь естественно общаться, здороваться и обсуждать со студентом, какой предмет он хочет учить. "
            "ПРАВИЛО 1 (ОБУЧЕНИЕ): Когда студент дает конкретную задачу, НИКОГДА не пиши финальный ответ. Объясни суть, напиши начальную формулу или реакцию, сделай первые шаги и ОСТАНОВИСЬ. Задай вопрос, чтобы студент сам закончил расчет или сделал вывод. "
            "ПРАВИЛО 2 (SUCCESS): Если студент отвечает правильно, тепло похвали его и ОБЯЗАТЕЛЬНО добавь тег [SUCCESS] в самый конец сообщения. "
            "ПРАВИЛО 3 (ФОРМАТИРОВАНИЕ): Объясняй пошагово, каждый шаг с новой строки. Только чистый, аккуратный и понятный текст. "
            "ПРАВИЛО 4 (СИМВОЛЫ): Исключительно юникод для степеней (², ³), запрещено использовать '^'."
        ),
        'ua': (
            "Ти доброзичливий, живий і досвідчений ШІ-репетитор. Ти можеш природно спілкуватися, вітатися та обговорювати зі студентом, який предмет він хоче вчити. "
            "ПРАВИЛО 1 (НАВЧАННЯ): Коли студент дає конкретну задачу, НІКОЛИ не пиши фінальну відповідь. Поясни суть, напиши початкову формулу або реакцію, зроби перші кроки і ЗУПИНИСЬ. Постав запитання, щоб студент сам закінчив розрахунок або зробив висновок. "
            "ПРАВИЛО 2 (SUCCESS): Якщо студент відповідає правильно, тепло похвали його і ОБОВ'ЯЗКОВО додай тег [SUCCESS] у самий кінець повідомлення. "
            "ПРАВИЛО 3 (ФОРМАТУВАННЯ): Пояснюй покроково, кожен крок з нового рядка. Тільки чистий, акуратний і зрозумілий текст. "
            "ПРАВИЛО 4 (СИМВОЛИ): Виключно юнікод для степенів (², ³), заборонено використовувати '^'."
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


@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id) 
    balance = get_balance(user_id)
    lang = get_language(user_id)
    texts = {
        'en': f"💰 Your balance: {balance} $STUD",
        'ru': f"💰 Твой баланс: {balance} $STUD",
        'ua': f"💰 Твій баланс: {balance} $STUD"
    }
    await message.answer(texts.get(lang, texts['en']))

@dp.message(Command("rules"))
async def cmd_rules(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    texts = {
        'en': "📚 *How to earn $STUD:*\n1. Send a math problem.\n2. I give the theory and formula.\n3. YOU calculate the final answer.\n4. If correct, you get +5 $STUD!",
        'ru': "📚 *Как заработать $STUD:*\n1. Отправь мне задачу.\n2. Я распишу теорию и формулу.\n3. ТЫ считаешь финальный ответ.\n4. Если ответ верный, получаешь +5 $STUD!",
        'ua': "📚 *Як заробити $STUD:*\n1. Відправ мені задачу.\n2. Я розпишу теорію та формулу.\n3. ТИ рахуєш фінальну відповідь.\n4. Якщо відповідь правильна, отримуєш +5 $STUD!"
    }
    await message.answer(texts.get(lang, texts['en']), parse_mode="Markdown")

@dp.message(Command("wallet"))
async def cmd_wallet(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    texts = {
        'en': "🔗 Web3 integration with Autheo V2 network is currently in development. Stay tuned!",
        'ru': "🔗 Интеграция Web3 с сетью Autheo V2 находится в разработке. Ожидайте!",
        'ua': "🔗 Інтеграція Web3 з мережею Autheo V2 знаходиться в розробці. Очікуйте!"
    }
    await message.answer(texts.get(lang, texts['en']))

@dp.message(Command("language"))
async def cmd_language(message: types.Message):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="Українська 🇺🇦", callback_data="lang_ua")]
    ])
    await message.answer("Select your language / Выберите язык / Оберіть мову:", reply_markup=kb)



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
    user_sessions[user_id] = [user_sessions[user_id][0]] + user_sessions[user_id][-10:]

    wait_texts = {'en': "⏳ Thinking...", 'ru': "⏳ Думаю...", 'ua': "⏳ Думаю..."}
    wait_msg = await message.answer(wait_texts[lang])

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_sessions[user_id]
        )
        
        bot_reply = response.choices[0].message.content.strip()
        
        
        if not bot_reply:
            if wait_msg: await wait_msg.delete()
            await message.answer("⚠️ Я не смог сгенерировать ответ. Пожалуйста, повторите снова!")
            return 
           
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
