# HackHub — MVP на Django

Простой старт для веб-приложения по автоматизации организации хакатонов.

## Что реализовано



## Запуск

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

##После запуска:
- сайт: http://127.0.0.1:8000/
 codex/create-web-app-for-hackathon-automation-8v2i6vv
- вход: http://127.0.0.1:8000/login/
- регистрация: http://127.0.0.1:8000/signup/
- админка: http://127.0.0.1:8000/admin/

> После входа пользователь перенаправляется в `/dashboard/` (исправлен 404 `/accounts/profile/`).

## Как создать хакатон

1. Войдите под пользователем с ролью **организатор** (или под superuser/staff).
2. Откройте `/hackathons/`.
3. Нажмите **«Создать хакатон»**.
4. Заполните форму и сохраните.

## Если в admin нельзя редактировать хакатоны/пользователей/группы

Проверьте:

1. Применены ли миграции (`python3 manage.py migrate`).
2. Вход выполнен под `superuser` (`python3 manage.py createsuperuser`).
3. Нет ли merge-конфликтов в шаблонах (`<<<<<<<`, `>>>>>>>`) и двойного `{% extends %}`.


Дополнительно: добавлены безопасные fallback-шаблоны `templates/admin/change_list.html` и `templates/admin/change_form.html`, которые не используют проблемные admin template tags (`change_list_object_tools`, `search_form`, `change_form_object_tools`) в вашем окружении.

Быстрая проверка:

```bash
python3 manage.py test
```

## Что добавить дальше

- email-уведомления;
- экспорт списков участников/команд (CSV);
- публичная страница проектов команд.
=======
- админка: http://127.0.0.1:8000/admin/

## Что добавить дальше

- регистрация и авторизация участников;
- роли (организатор/участник/ментор);
- команды и заявки на участие;
- расписание и публикация результатов.

