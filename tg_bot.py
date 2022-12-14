import logging
import os
from functools import partial
import random
import json
import enum

import redis
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from questions_utils import load_questions


logger = logging.getLogger("BotLogger")


class DialogStates(enum.Enum):
    USER_CHOICE = 0


def start(update, context, db):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    user_id = update.message.chat_id
    user_data = {'question': None, 'counter': 0}
    db.set(user_id, json.dumps(user_data))

    update.message.reply_text('Привет! Я бот для викторин!', reply_markup=reply_markup)

    return DialogStates.USER_CHOICE


def handle_new_question_request(update, context, questions, db):
    user_id = update.message.chat_id
    user_data = json.loads(db.get(user_id))

    question, answer = random.choice(list(questions.items()))
    user_data['question'] = question
    db.set(user_id, json.dumps(user_data))
    update.message.reply_text(question)
    return DialogStates.USER_CHOICE


def handle_solution_attempt(update, context, questions, db):
    user_id = update.message.chat_id

    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']

    user_answer = update.message.text.lower()
    correct_answer = questions[user_question].lower()
    if user_answer in correct_answer:
        message = ' Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        user_data['question'] = None
        user_data['counter'] += 1
    else:
        message = 'Неправильно... Правильный ответ: ' + correct_answer
        user_data['question'] = None

    update.message.reply_text(message)

    db.set(user_id, json.dumps(user_data))


def handle_surrender_request(update, context, questions, db):
    user_id = update.message.chat_id
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    user_data['question'] = None
    correct_answer = questions[user_question].lower()
    update.message.reply_text('Правильный ответ: ' + correct_answer)
    handle_new_question_request(update, context, questions, db)


def handle_get_counter_request(update, context, db):
    user_id = update.message.chat_id
    user_data = json.loads(db.get(user_id))
    counter = user_data['counter']
    update.message.reply_text('Ваш счёт: ' + str(counter))


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':

    tg_bot_token = os.environ['TG_BOT_TOKEN']
    db_host = os.environ['DB_HOST']
    db_port = os.environ['DB_PORT']
    db_password = os.environ['DB_PASSWORD']

    updater = Updater(tg_bot_token)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    db = redis.Redis(
        host=db_host,
        port=db_port,
        password=db_password,
        db=0)

    questions = load_questions("questions")

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',
                                     partial(start,
                                             db=db))],

        states={
            DialogStates.USER_CHOICE: [
                MessageHandler(Filters.regex('^Новый вопрос$'),
                               partial(handle_new_question_request,
                                       questions=questions,
                                       db=db)),
                MessageHandler(Filters.regex('^Сдаться$'),
                               partial(handle_surrender_request,
                                       questions=questions,
                                       db=db)),
                MessageHandler(Filters.regex('^Мой счёт$'),
                               partial(handle_get_counter_request,
                                       db=db)),
                MessageHandler(Filters.text,
                               partial(handle_solution_attempt,
                                       questions=questions,
                                       db=db))
            ]
        },
        fallbacks=[ConversationHandler.END]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    logger.info('TG bot started')
    updater.idle()
