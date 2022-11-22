# Чат-бот для викторин.

Чатбот для месенджера Telegram и социальной сети Вконтакте для проведения викторин.

Тестовые боты:

* [TG](https://t.me/dvmn_verbs_game_support_bot)
* [VK](https://vk.com/im?sel=-215997139)

Пример работы VK:

![](https://github.com/Ykyki4/devman-quiz/blob/main/media/examination_tg.gif)

Пример работы TG:

![](https://github.com/Ykyki4/devman-quiz/blob/main/media/examination_vk.gif)

## Установка:

Для начала, скачайте репозиторий в .zip или клонируйте его, изолируйте проект с помощью venv и установите зависимости командой:

```
pip install -r requirements.txt
```

Далее, создайте файл .env и установите следующие переменные окружения в формате ПЕРЕМЕННАЯ=значение:

* TG_BOT_TOKEN - Бот в телеграмме для викторин. Зарегистрировать нового бота можно [тут](https://telegram.me/BotFather).
* VK_GROUP_TOKEN - Токен вашей группы в вк. Вот где его [найти](https://dvmn.org/media/filer_public/2f/11/2f11a34a-1de3-4acc-838d-d1be37bd6828/screenshot_from_2019-04-29_20-10-16.png).
* DB_HOST
* DB_PASSWORD
* DB_PORT

Для получения данных о вашей базе данных, зайдите на [сайт](https://redis.com/), и создайте там новую базу данных.

Для запуска бота, введите в терминал команду:

```
python vk_bot.py/tg_bot.py
```

Также, бот берёт вопросы из папки questions, если вы хотите добавить свои вопросы, поместите .txt файл с вопросами в вышеупомянутую папку, и обязательно форматуйте всё под вид:

```
Вопрос: "сам вопрос"


Ответ: "сам ответ"
```

Если формат текста не будет таковым, бот скопирует ответы и вопросы неверно.
