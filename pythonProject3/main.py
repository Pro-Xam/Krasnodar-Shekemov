import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import sqlite3


starting = False
command_list = ['00000000it_is_new00000000', '00000000it_is_edit00000000', '00000000it_is_help00000000',
                '00000000it_is_show00000000', '00000000it_is_delete00000000']
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/start'],
                  ['/help'],
                  ['/new', '/edit'],
                  ['/show', '/delete']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

a = {}


async def start(update, context):
    global a, starting
    starting = True
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
    res = cur.execute(f"""SELECT name FROM mytable WHERE user = '{user_id}'""")
    c = []
    for i in list(res):
        c.append(i[0])

    if b in c:
        a[user_id].append('00000000locked_name00000000')
        print('ln')
    else:
        try:
            cur.execute(f"""INSERT INTO mytable (name,text,user) VALUES ('{b}','{text}','{str(user_id)}')""").fetchall()
            con.commit()
            a[user_id].append('00000000successful00000000')
            print('s')
        except Exception:
            print('er')
            a[user_id].append('00000000error00000000')
    con.close()


def edit01(user_id, text):
    global a
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    res = cur.execute(f"""SELECT name FROM mytable WHERE user = '{str(user_id)}'""").fetchall()
    new_res = []
    for i in (list(res)):
        new_res.append(list(i)[0])
    if text in new_res:
        a[user_id].append(['00000000it_is_edit_new00000000', text])
    else:
        a[user_id].append('00000000locked_name000000000')
    con.close()


def edit02(user_id, text1, text2):
    global a
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    try:
        text3 = text2.split('\n')[0]
        print('text1', text1)
        print('text2', text2)
        print('text3', text3)
        cur.execute(f"""UPDATE mytable SET text = '{text2}' WHERE name = '{text1}' and user = '{user_id}'""").fetchall()
        cur.execute(f"""UPDATE mytable SET name = '{text3}' WHERE name = '{text1}' and user = '{user_id}'""").fetchall()
        con.commit()
        a[user_id].append('00000000successful00000000')
    except Exception:
        a[user_id].append('00000000error00000000')
    con.close()


def delete01(user_id, text):
    global a
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    try:
        cur.execute(f"""DELETE FROM mytable WHERE name = '{text}' and user = {user_id}""").fetchall()
        con.commit()
        a[user_id].append('00000000successful00000000')
    except Exception:
        a[user_id].append('00000000error00000000')
    con.close()


async def help_command(update, context):
    global starting
    if starting:
        return None
    await update.message.reply_text(f"Команда /new отвечает за создание новой заметки. Текст до превого enter'а я буду"
                                    f" считать названием. Использовать кавычки в тексте не рекомендуется (может "
                                    f"привести к ошибке). Как и создание заметок с одинаковыми назаванями (причина"
                                    f" та же)\n"
                                    f"Команда /edit позволит редактировать уже существующую заметку.\n"
                                    f"Команда /show выведет все существующие заметки\n"
                                    f"Команда /delete удаляет заметку с выбранным именем")


def check(user_id):
    global a, command_list
    if len(a[user_id]) > 3:
        a[user_id] = a[user_id][-3:].copy()
    print('check')
    if len(a[user_id]) >= 2:
        if a[user_id][-2] == '00000000it_is_new00000000' and a[user_id][-1] not in command_list:
            print(1)
            new01(user_id, a[user_id][-1])
        elif a[user_id][-2] == '00000000it_is_edit_start00000000' and a[user_id][-1] not in command_list:
            print(21)
            edit01(user_id, a[user_id][-1])
        elif a[user_id][-2] == '00000000it_is_delete00000000' and a[user_id][-1] not in command_list:
            print(3)
            delete01(user_id, a[user_id][-1])
        elif type(a[user_id][-2]) is list:
            if a[user_id][-2][0] == '00000000it_is_edit_new00000000' and a[user_id][-1] not in command_list:
                print(22)
                edit02(user_id, a[user_id][-2][1], a[user_id][-1])


async def last_massage(update, context):
    global a
    user_id = update.message.chat_id
    a[user_id].append(update.message.text)
    check(user_id)
    if a[user_id][-1] == '00000000successful00000000':
        await context.bot.send_message(text='Успешно', chat_id=user_id)
    elif a[user_id][-1] == '00000000locked_name00000000':
        await context.bot.send_message(text='Ошибка названия', chat_id=user_id)
    elif a[user_id][-1] == '00000000error00000000':
        await context.bot.send_message(text='Ошибка', chat_id=user_id)
    elif a[user_id][-1][0] == '00000000it_is_edit_new00000000':
        print(1)
        await context.bot.send_message(text='Старый текст:', chat_id=user_id)
        cur = sqlite3.connect("mydata (2).sqlite").cursor()
        res = cur.execute(f"""SELECT text FROM mytable WHERE user = '{str(user_id)}' and name
         = '{a[user_id][-1][1]}'""").fetchall()[0][0]
        await context.bot.send_message(text=res, chat_id=user_id)
        await context.bot.send_message(text='Введите откорректированный текст:', chat_id=user_id)


async def new(update, context):
    global a, starting
    if starting:
        return None
    user_id = update.message.chat_id
    a[user_id].append('00000000it_is_new00000000')
    await context.bot.send_message(chat_id=user_id, text='Введите текст:')


async def edit(update, context):
    global a, starting
    if starting:
        return None
    user_id = update.message.chat_id
    a[user_id].append('00000000it_is_edit_start00000000')
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    res = cur.execute(f"""SELECT name FROM mytable WHERE user = '{str(user_id)}'""").fetchall()
    con.close()
    for i in list(res):
        await context.bot.send_message(chat_id=user_id, text=i[0])
    await context.bot.send_message(chat_id=user_id, text='Введите название заметки:')


async def delete(update, context):
    global a, starting
    if starting:
        return None
    print('это делит')
    user_id = update.message.chat_id
    a[user_id].append('00000000it_is_delete00000000')
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    res = cur.execute(f"""SELECT name FROM mytable WHERE user = '{str(user_id)}'""").fetchall()
    con.close()
    for i in list(res):
        await context.bot.send_message(chat_id=user_id, text=i[0])
    await context.bot.send_message(chat_id=user_id, text='Введите название заметки:')


async def show(update, context):
    global starting
    if starting:
        return None
    user_id = update.message.chat_id
    [user_id].append('00000000it_is_show00000000')
    con = sqlite3.connect("mydata (2).sqlite")
    cur = con.cursor()
    res = cur.execute(f"""SELECT text FROM mytable WHERE user = '{str(user_id)}'""").fetchall()
    con.close()
    for i in res:
        await context.bot.send_message(text=i[0], chat_id=user_id)


def main():
    application = Application.builder().token("6777765425:AAFbW0556l2sXbP-rZyQBeX5Yw6UbHq-CMs").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new", new))
    application.add_handler(CommandHandler("edit", edit))
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("delete", delete))

    text_handler1 = MessageHandler(filters.TEXT, last_massage)
    application.add_handler(text_handler1)

    application.run_polling()


if __name__ == '__main__':
    main()
