import os
import json
import random
import logging

import redis
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from questions_utils import load_questions


logger = logging.getLogger("BotLogger")


def start(event, vk_api, keyboard, db):
    user_id = event.user_id
    user_data = {'question': None, 'counter': 0}
    db.set(user_id, json.dumps(user_data))
  
    vk_api.messages.send(
        user_id=event.user_id,
        message='Привет, я бот для викторин!',
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )


def handle_new_question_request(event, vk_api, questions, db):
    user_id = event.user_id
    user_data = json.loads(db.get(user_id))
    
    question, answer = random.choice(list(questions.items()))
    user_data['question'] = question
    db.set(user_id, json.dumps(user_data))
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=get_random_id()
    )


def handle_solution_attempt(event, vk_api, questions, db):
    user_id = event.user_id
  
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    
    user_answer = event.text.lower()
    correct_answer = questions[user_question].lower()
    if user_answer in correct_answer:
      message = ' Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
      user_data['question'] = None
      user_data['counter'] += 1 
    else:
      message = 'Неправильно... Правильный ответ: '+correct_answer
      user_data['question'] = None
      
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=get_random_id()
    )
    db.set(user_id, json.dumps(user_data))


def handle_surrender_request(event, vk_api, questions, db):
    user_id = event.user_id
    user_data = json.loads(db.get(user_id))
    user_question = user_data['question']
    user_data['question'] = None
    correct_answer = questions[user_question].lower()
    vk_api.messages.send(
        user_id=event.user_id,
        message='Правильный ответ: '+correct_answer,
        random_id=get_random_id()
    )
    handle_new_question_request(event, vk_api, questions, db)


def handle_get_counter_request(event, vk_api, db):
    user_id = event.user_id
    user_data = json.loads(db.get(user_id))
    counter = user_data['counter']
    vk_api.messages.send(
        user_id=event.user_id,
        message='Ваш счёт: '+str(counter),
        random_id=get_random_id()
    )


def main():

    db_host = os.environ['DB_HOST']
    db_port = os.environ['DB_PORT']
    db_password = os.environ['DB_PASSWORD']
    vk_group_token = os.environ['VK_GROUP_TOKEN']
  
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    db = redis.Redis(
                host=db_host,
                port=db_port,
                password=db_password,
                db=0)

    questions = load_questions("questions")
  
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт')

    longpoll = VkLongPoll(vk_session)

    logger.info('VK bot started')
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.text == 'Начать':
                        start(event, vk_api, keyboard, db)
                    elif event.text == 'Новый вопрос':
                        handle_new_question_request(event, vk_api, questions, db)
                    elif event.text == 'Сдаться':
                        handle_surrender_request(event, vk_api, questions, db)
                    elif event.text == 'Мой счёт':
                        handle_get_counter_request(event, vk_api, db)
                    else:
                        handle_solution_attempt(event, vk_api, questions, db)
        except Exception as exception:
            logger.error(msg="VK bot get an error:", exc_info=exception)


if __name__ == "__main__":
    main()
