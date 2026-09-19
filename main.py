import telebot
import sqlite3
import json
import requests
from datetime import datetime
from config import api_key, admin_id
from telebot import types

bot = telebot.TeleBot(api_key)


@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton('Перейти к котикам 😸', callback_data='work')
    author = types.InlineKeyboardButton('Посетить сайт автора 😪', url='https://wadeneff.github.io/')

    id_ = message.from_user.id
    name = message.from_user.first_name
    date = datetime.now().strftime('%d.%m.%Y %H:%M')

    if message.from_user.username:
        username = message.from_user.username
    else:
        username = "нет_тега"
    
    conn = sqlite3.connect('database.sql')
    cur = conn.cursor()

    conn.execute('create table if not exists users(id int primary key, name varchar(50), username varchar(50), date varchar(50))')
    conn.commit()
    cur.execute(
    'insert or replace into users (id, name, username, date) values (?, ?, ?, ?)',
    (id_, name, username, date)
    )
    conn.commit()

    cur.close()
    conn.close()

    markup.row(back)
    markup.row(author)
    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup)


@bot.message_handler(commands=['admin'])
def admin(message):
    markup = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton('Назад ☁️', callback_data='work')
    see = types.InlineKeyboardButton('Вывести список пользователей', callback_data='users')

    if message.chat.id != admin_id:
        markup.row(back)
        bot.send_message(message.chat.id, 'Отказано ❌', reply_markup=markup)
    else:
        markup.row(see)
        markup.row(back)
        bot.send_message(message.chat.id, '...', reply_markup=markup)   

@bot.callback_query_handler(func=lambda callback:True)
def lookUp(callback):
    bot.answer_callback_query(callback.id)

    markup = types.InlineKeyboardMarkup()
    kitten = types.InlineKeyboardButton('На какого? 👀', callback_data='kitten')
    newKitten = types.InlineKeyboardButton('Покажи ещё котика! 👀', callback_data='kitten')
    ifYes = types.InlineKeyboardButton('Это я! 😽', callback_data='is_me')
    ifNot = types.InlineKeyboardButton('Это не я 😿', callback_data='not_me')
    back = types.InlineKeyboardButton('Назад ☁️', callback_data='work')
    backAdmin = types.InlineKeyboardButton('Назад ☁️', callback_data='back_admin')

    res = requests.get('https://api.thecatapi.com/v1/images/search')
    data = json.loads(res.text)
    img = data[0]['url']

    if callback.data == 'users':
        conn = sqlite3.connect('database.sql')
        cur = conn.cursor()
    
        cur.execute('select * from users')
        users = cur.fetchall()

        info = ''
        for i in users:
            info += f'Тег: @{i[2]}\nИмя: {i[1]}\nID: {i[0]}\nПоследний /start: {i[3]}\n{'-~-~' * 5}\n'
    
        cur.close()
        conn.close()
        
        markup.row(back)
        if not info.strip():
            bot.edit_message_text(text='В базе данных нет пользователей.', chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)
            bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id-1)
        else:
            bot.edit_message_text(text=info, chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)
            bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id-1)

    elif callback.data == 'back_admin':
        markup.row(kitten)
        bot.delete_message(chat_id=callback.chat.id, message_id=callback.message.message_id-1)
        bot.edit_message_text(text='А ты знаешь, на какого котика ты похож(а)?? ', chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)
    elif callback.data == 'work':
        markup.row(kitten)
        bot.edit_message_text(text='А ты знаешь, на какого котика ты похож(а)?? ', chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)
    elif callback.data == 'kitten':
        caption_text = 'Ты похож(а) на... Этого котика!'
        markup.row(ifYes, ifNot)
        bot.send_photo(chat_id=callback.message.chat.id, photo=img, caption=caption_text, reply_markup=markup)
    elif callback.data == 'is_me':
        markup.row(newKitten)
        bot.send_message(callback.message.chat.id, 'Ура!!', reply_markup=markup)
    elif callback.data == 'not_me':
        caption_text = 'Может, тогда ты похож(а) на этого котика??'
        markup.row(ifYes, ifNot)
        bot.send_photo(chat_id=callback.message.chat.id, photo=img, caption=caption_text, reply_markup=markup)
    elif callback.data == 'del':
        bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id-1)

@bot.message_handler(commands=['id'])
def getId(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Удалить', callback_data='del')
    markup.row(btn)
    bot.reply_to(message, message.from_user.id, reply_markup=markup)

bot.polling(non_stop=True)