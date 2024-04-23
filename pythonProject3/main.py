import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import sqlite3


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/new'],
                  ['/edit'],
                  ['/show']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

a = {}


async def start(update, context):
    global a
    await update.message.reply_text(
        "Вас приветствует бот-библиотекарь. Я сохраню любой текст, который вы передадите мне.",
        reply_markup=markup

    )
    f = list(a.keys())
    user_id = update.message.chat_id
    if user_id not in f:
        a[user_id] = []


def new01(user_id, text):
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    b = text.split('\n')[0]
    print(b, text, user_id)

    cur.execute(f"""INSERT INTO mytable (name,text,user) VALUES ('{b}','{text}','{str(user_id)}')""").fetchall()

    con.commit()
    con.close()


def edit01(user_id, text):
    pass


async def help_command(update, context):
    await update.message.reply_text(f"Команда /new отвечает за создание новой заметки."
                                    f"Текст до превого enter'а я буду считать названием\n"
                                    f"Команда /edit позволит редактировать уже существующую заметку.\n"
                                    f"Команда /show выведет все существующие заметки\n"
                                    f"Команда /instuction выведет инструкцию по использованию команд")


def check(user_id, update):
    global a
    print(0)
    if len(a[user_id]) > 2:
        a[user_id] = a[user_id][-2:].copy()
    print(1)
    if len(a[user_id]) == 2:
        if a[user_id][0] == '00000000it_is_new00000000' and a[user_id][1] != '00000000it_is_new00000000':
            print(31)
            new01(user_id, a[user_id][1])
        elif a[user_id][0] == '00000000it_is_edit00000000' and a[user_id][1] != '00000000it_is_edit00000000':
            print(32)
            edit01(user_id, a[user_id][1])


async def last_massage(update, context):
    global a
    user_id = update.message.chat_id
    a[user_id].append(update.message.text)
    check(user_id, update)
    print(a)


async def instruction(update, context):
    pass


async def new(update, context):
    global a
    user_id = update.message.chat_id
    a[user_id].append('00000000it_is_new00000000')
    await context.bot.send_message(chat_id=user_id, text='Введите текст:')


async def edit(update, context):
    global a
    user_id = update.message.chat_id
    a[user_id].append('00000000it_is_edit00000000')
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    print(str(user_id))
    print(f"""SELECT name FROM mytable
    WHERE user == '{str(user_id)}'""")
    res = cur.execute(f"""SELECT name FROM mytable'
    WHERE user == '{str(user_id)}'""").fetchall()
    con.close()
    for i in res:
        await context.bot.send_message(chat_id=user_id, text=i)
    await context.bot.send_message(chat_id=user_id, text='Введите обновленный текст:')


async def show(update, context):
    pass


def main():
    application = Application.builder().token("6777765425:AAFbW0556l2sXbP-rZyQBeX5Yw6UbHq-CMs").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new", new))
    application.add_handler(CommandHandler("edit", edit))
    application.add_handler(CommandHandler("show", show))

    text_handler1 = MessageHandler(filters.TEXT, last_massage)
    application.add_handler(text_handler1)

    application.run_polling()


'''
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
        },)

    application.add_handler(conv_handler)

    application.run_polling()
'''


if __name__ == '__main__':
    main()
