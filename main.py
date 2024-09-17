from telethon import TelegramClient, events
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import asyncio
from openai import OpenAI
import json
from emails import *  # Импортируйте список email

# Загрузка использованных слов
def load_used_words():
    try:
        with open('used_words.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

# Сохранение использованных слов в файл
def save_used_words():
    with open('used_words.json', 'w') as f:
        json.dump(list(used_words), f)

used_words = load_used_words()

import atexit
atexit.register(save_used_words)

# Инициализация клиента OpenAI
clientAI = OpenAI(api_key="3PBVFay6iJzUdBxKwQ05uVYYTD8vtEZ4", base_url="https://api.deepinfra.com/v1/openai")

def generate_response_from_api(prompt: str):
    response = clientAI.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct",
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.8,
        max_tokens=300
    )
    if response.choices:
        return response.choices[0].message.content
    return None

# Конфигурация Telegram
API_ID = '18722935'
API_HASH = '09f2b2156abdc9276eb52e173036311a'
BOT_TOKEN = '7163780616:AAHOvYDuloy3x4JY9V8d5U0RQMlvSyGXsWU'
NAMES_IDS = [
    '@mari_vakansii', '@dnative_job', '@algoritm_schools', '@normrabota', '@polyaluzjob',
    '@digital_rabota', '@workindesign', '@designer_ru', '@workasap',
    '@jun_hi_vacancies', '@Vakansi_Rus', '@Visionisland', '@designizer', '@zakaz_design',
    '@vakanser_digital_smm', '@the_pomogator', '@workk_on', '@naudalenkebro', '@INFOGRAPHIKAQ',
    '@infografika_dizaynz', '@MPdesigns', '@distantsiya', '@vakansii_infobiz', '@vakansii_dizaynerov',
    '@vakansii_design', '@freelancetaverna', '@dl_marketplace', '@desinger_vacancies', '@uvetrovoi',
    '@workfordesigner', '@Designs_job', '@dsgn_vacancies', '@vakansii_design', '@Designs_squad',
    '@Vakansi_Rus', '@design_freevacancies'
]


# Инициализация клиента Telegram
clientTg = TelegramClient('main', API_ID, API_HASH)
bot = Bot(token=BOT_TOKEN)

welcome_message = '''привет! 🗽

это — бот для сбора заказов от команды SO DESIGN. принцип его работы очень простой:

он сканирует большое количество каналов и чатов для фрилансеров, собирает из них заказы, связанные с дизайном, и отправляет сюда. его задача - помочь тебе и сэкономить время, которое тебе пришлось бы тратить на то, чтобы мониторить все эти каналы вручную.
'''

second_message = '''📍А сейчас — давай пройдемся по самым важным моментам:

1. перед тем, как начать откликаться на вакансии и заявки — обязательно посмотри модуль по поиску клиентов и продажам на нашей платформе обучения. там мы подробно разобрали, как лучше писать отклики на вакансии и общаться с заказчиками.

2. наш бот собирает заявки из чатов автоматически, и мы не можем их полностью отфильтровать. и так как иногда в каналах для фрилансеров обитают мошенники — они иногда могут попадать и в нашего бота.

мошенники могуть попасться везде, и ваша задача быть максимально бдительными и аккуратными, чтобы не попадаться на их уловки.

мы подготовили статью, где подробно разобрали основные виды мошенничества и главные правила, которым нужно следовать, чтобы на них не попасть. обязательно изучите ее перед тем, как начать пользоваться ботом:

https://teletype.in/@sosomak/safe

Когда внимательно изучишь всю информацию выше и будешь готов(а) к использованию бота - нажми на кнопку ниже и он начнет отправлять тебе вакансии.'''

# Словарь для отслеживания состояния пользователей
user_states = {}
user_chat_ids = []

VALID_WORDS = emails

def is_valid_word(word: str) -> bool:
    return word in VALID_WORDS and word not in used_words

async def start(update: Update, context):
    image_pathw = 'welcome.jpg'
    chat_id = update.message.chat_id
    
    if chat_id not in user_chat_ids:
        await context.bot.send_message(chat_id=chat_id, text='Пожалуйста, введи свою почту, которую ты использовал(а) при обучении на курсе.')
        return
    else:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=open(image_pathw, 'rb'),
            caption=welcome_message,
            parse_mode='HTML'
        )
        button = InlineKeyboardButton("Я всё изучил(а)", callback_data="confirm")
        keyboard = InlineKeyboardMarkup([[button]])
        await context.bot.send_message(chat_id, text=second_message, reply_markup=keyboard)

async def button_callback(update: Update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == "confirm":
        await query.answer("Спасибо за подтверждение!")
        user_states[chat_id] = True
        await context.bot.send_message(chat_id, text="Отлично! Теперь я начну присылать тебе вакансии.")

async def message_passes_filter(message_text):
    keywords = [
        '#дизайнер', '#графическийдизайнер', '#лендинг', '#вебдизайн', '#веб-дизайн',
        '#вебдизайнер', '#вебдизайнера', '#веб-дизайнер', '#веб-дизайнера',
        '#дизайнера', 'инфографика', 'карточка', 'сайт', 'таплинк',
        'taplink', 'презентация', 'презентацию', 'карточку', 'инфографику',
        'оформление', 'инфографики', 'карточек', 'тильда', 'тильде', 'tilda', '#дизайнер',
        '#графическийдизайнер', '#лендинг', '#вебдизайн', '#веб-дизайн',
        '#вебдизайнер', '#вебдизайнера', '#веб-дизайнер', '#веб-дизайнера',
        '#дизайнера', 'сайтолог', 'сайтолога', 'инфографике', 'сайты', '#разработкалейдинга',
        '#куратор', '#UX', '#UI', 'рилсмейкер', 'работа'
    ]

    exclude_keywords = ['пом']

    message_lower = message_text.lower()
    if not any(word in message_lower for word in keywords):
        return False
    if any(word in message_lower for word in exclude_keywords):
        return False
    return True

async def handle_new_message(event):
    message = event.message
    chat_id = message.chat_id

    # Проверяем, нужно ли отправлять сообщение
    if chat_id in user_states and user_states[chat_id]:
        print(message.text)
        if message.text and message_passes_filter(message.text):
            print(message.text)
            system_prompt = f"This message is in Russian: '{message.text}'. I need to sort this message, YOU MUST only reply to me with 'True' or 'False'. 'True' if in this message a person is looking for a designer freelancer for an order, exactly an order (not a vacancy). 'False' in any other case."
            
            is_order =  asyncio.to_thread(generate_response_from_api, system_prompt)
            
            if is_order == 'True':
                link = f"<a href='https://t.me/{event.chat.username}/{message.id}'>Ссылка</a>"
                caption_text = f'📝 <b> текст заявки: </b> \n\n {message.text}. \n\n 📲 <b> ссылка на заявку: </b> \n\n {link}'
                
                for chat_id in user_chat_ids:
                    try:
                        image_path = 'botcover.jpg' 
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=open(image_path, 'rb'),  
                            caption=caption_text, 
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения: {e}")

async def handle_text_message(update: Update, context):
    chat_id = update.message.chat_id
    message_text = update.message.text

    if is_valid_word(message_text):
        if chat_id not in user_chat_ids:
            user_chat_ids.append(chat_id)
            used_words.add(message_text)
            await context.bot.send_message(chat_id, text='Почта подтверждена! Можешь приступать к работе.')
            await start(update, context)
    else:
        await context.bot.send_message(chat_id, text='Почта уже использована или введена неправильно. Попробуй ещё раз.')

async def run_telethon_client():
    async with clientTg:
        for channel_id in NAMES_IDS:
            try:
                entity = await clientTg.get_entity(channel_id)
                print(f"joined to the channel: {entity.title}")
                clientTg.add_event_handler(handle_new_message, events.NewMessage(chats=entity))
            except Exception as e:
                print(f"Ошибка при подключении к {channel_id}: {e}")
        await clientTg.run_until_disconnected()

async def run_telegram_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    await application.initialize()  # Инициализация приложения
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    await application.start()  # Запуск бота
    await application.updater.start_polling()

async def main():
    await asyncio.gather(run_telegram_bot(), run_telethon_client())

if __name__ == "__main__":
    asyncio.run(main())
