# suvvy.ai Telegram бот

![python v3.10+](https://img.shields.io/badge/python-v3.10%2B-blue)
![aiogram v3.0.0b7](https://img.shields.io/badge/aiogram-v3.0.0b7-orange)
[![suvvy.ai](https://img.shields.io/badge/suvvy.ai-best%20AI%20website-blue)](https://suvvy.ai)

### Это бот, который использует aiogram и suvvy.ai API, чтобы общаться с пользователями!
##### А также в нём можно рекламировать свои ТГ каналы!

## ❓ Как установить?
Вводите данные команды по одной:
```shell
git clone https://github.com/barabum0/suvvyai-telegram-subscribe
cd suvvyai-telegram-subscribe
python -m venv venv  # если хотите отделить бота с помощью виртуального окружения
```

Для запуска используйте:
```shell
source venv/bin/activate  # "подключение" к виртуальному окружению
python main.py
```

## ⚙️ Как настроить?
В файл `.env` вводим токен от вашего телеграм бота и бота suvvy.ai.

В файл `telegram.yaml` вводим нужные вам телеграм каналы. Бот обязательно должен быть администратором этих каналов!

Пример файла `telegram.yaml`:
```yaml
channels:
  0:  # <--- это значение ни на что не влияет, но должно быть уникальным
    name: Канал 1
    id: ID канала 1
    link: https://t.me/ссылка на канал 1
  1:  # <--- это значение ни на что не влияет, но должно быть уникальным
    name: Канал 2
    id: ID канала 2
    link: https://t.me/ссылка на канал 2
```

Таким образом можно внести сколько угодно каналов!
