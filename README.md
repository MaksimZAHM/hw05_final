# Yatube
>Учебный проект в рамках курса __Backend-developer__ на платформе __Яндекс.Практикум__

### Описание
Yatube - проект социальной сети в которой можно публиковать свои записи и комментировать чужие, подписываться на любимых авторов и ставить лайки.

Проект реализован на MVT-архитектуре (архитектурный паттерн Model-View-Template), реализована система регистрации новых пользователей, настройка пользовательского профиля, восстановление паролей пользователей через почту, система тестирования проекта на unittest, пагинация постов и кэширование страниц.

### Системные требования
- Python 3.7+
- Works on Linux, Windows, macOS

### Стек технологий:
- Python 3.7
- Django 3.2
- SQLite3
- Bootstrap 4

### Запуск проекта 
Клонировать репозиторий и перейти в него в командной строке. Создать и активировать виртуальное окружение c учетом версии Python 3.7:

```
git clone https://github.com/MaksimZAHM/Yatube.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```
```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Разработчик проекта

Автор: Maksim Zamyatin  
E-mail: [mm.zamyatin@gmail.com](mailto:mm.zamyatin@gmail.com)
