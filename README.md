# Yatube - социальная сеть, блог

## Описание

- Проект позволяет создать собственную страницу на которой можно оставлять посты.
- Пользователи могут заходить на чужие страницы, коментировать посты, подписываться на любимых авторов.
- Авторы могут делится своими записями в сообществах.

## Пользователькие роли

| Функционал                                                                            | Неавторизованные пользователи |  Авторизованные пользователи | Администратор  |
|:--------------------------------------------------------------------------------------|:---------:|:---------:|:---------:|
| Доступ к главное странице                                                             | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Возможность просматривать посты                                                       | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Возможноть просмотреть список групп                                                   | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Просмотр коментарий под постом                                                        | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Создание и редактирование постов                                                      | :x: | :heavy_check_mark: | :heavy_check_mark: |
| Просмотр подписок текущего пользователя                                               | :x: | :heavy_check_mark: | :heavy_check_mark: |
| Просмотр всех постов избранных авторов                                                | :x: | :heavy_check_mark: | :heavy_check_mark: |
| Создание сообществ                                                                    | :x: | :x: | :heavy_check_mark: |
| Просмотр всех пользователей                                                           | :x: | :x: | :heavy_check_mark: |

## Запуск проекта

- Клонировать репозиторий https://github.com/SurfimChilim/yatube_final

- Установить и активировать виртуальное окружение    
```
Для пользователей Windows:
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
```
- Установить зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Перейти в каталог с файлом manage.py выполнить команды:

Выполнить миграции:
```
python manage.py migrate
```
Создать супер-пользователя:
```
python manage.py createsuperuser
```
Собрать статику:
```
python manage.py collectstatic
```
Запуск проекта:
```
python manage.py runserver
```

## Используемые технологии

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)

## Об авторе

- Начинающий разработчик Евгений Бузуев. С моими другими работами вы можете ознакомится по ссылке: https://github.com/SurfimChilim