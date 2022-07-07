import config
import telebot
from telebot import types
from database import Database

db = Database('db.db')
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    search_conservation_button = types.KeyboardButton('📢 Поиск собеседника 📢')
    markup.add(search_conservation_button)

    bot.send_message(message.chat.id,
                     'Привет, {0.first_name}! Я Кермит и это анонимный чат. Жми кнопку для поиска собеседника'.format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button = types.KeyboardButton('📢 Поиск собеседника 📢')
    markup.add(menu_button)

    bot.send_message(message.chat.id, '📃 Меню 📃'.format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['stop'])
def stop(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.remove_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        exit_button = types.KeyboardButton('📢 Поиск собеседника 📢')
        markup.add(exit_button)

        bot.send_message(chat_info[1], '❌ Собеседник покинул чат ❌', reply_markup=markup)
        bot.send_message(message.chat.id, '❌ Вы вышли из чата ❌', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вы не начали чат❗️')


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == '📢 Поиск собеседника 📢':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            stop_search_button = types.KeyboardButton('❌ Остановить поиск ❌')
            markup.add(stop_search_button)

            chat_two = db.get_chat()  # Берем собеседника, который стоит в очереди первым

            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_in_queue(message.chat.id)
                bot.send_message(message.chat.id, '📡 Поиск собеседника 📡', reply_markup=markup)
            else:
                status_message = 'Собеседник найден! Чтобы прекратить общение, нажмите /stop'
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                stop_dialog_button = types.KeyboardButton('/stop')
                markup.add(stop_dialog_button)

                bot.send_message(message.chat.id, status_message, reply_markup=markup)
                bot.send_message(chat_two, status_message, reply_markup=markup)



        elif message.text == '❌ Остановить поиск ❌':
            db.delete_from_queue(message.chat.id)
            bot.send_message(message.chat.id, '❌ Поиск остановлен ❌\n Введите /menu')
        else:
            chat_info = db.get_active_chat(message.chat.id)
            bot.send_message(chat_info[1], message.text)


bot.polling(none_stop=True)
