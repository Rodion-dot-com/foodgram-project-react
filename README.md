# praktikum_new_diplom
![workflow](https://github.com/Rodion-dot-com/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg) 

## О проекте foodgram:
- Foodgram - сайт «Продуктовый помощник». На этом сервисе пользователи 
  могут публиковать рецепты, подписываться на публикации других 
  пользователей, добавлять понравившиеся рецепты в список «Избранное», а 
  перед походом в магазин скачивать сводный список продуктов, необходимых 
  для приготовления одного или нескольких выбранных блюд. 
- Основой проекта является веб-фраемворки Django и Django REST Framework;
- Авторы проекта: Родион Прошляков(proshlyakovrodion@yandex.ru)
- Фронтенд для проекта предоставил Яндекс Практикум
## Инфраструктура:
- Проект работает с СУБД PostgreSQL
- Проект запущен на сервере в Яндекс.Облаке в трёх контейнерах: nginx, PostgreSQL и Django+Gunicorn
## Инструкция для локального запуска проекта
### Создайте файл .env с переменными окружения в корне проекта:
Шаблон наполнения env-файла
```
SECRET_KEY=some-kind-of-key # установите ваш секретный ключ 
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
### Находясь в корне проекта выполните следующее команды:
- Перенесите файлы с директории infra в корень проекта
```
mv infra/* .
```
- Соберите контейнеры и запустите их
```
docker-compose up -d --build 
```
- Выполните по очереди команды
```
docker-compose exec web python manage.py migrate
```
```
docker-compose exec web python manage.py createsuperuser
```
```
docker-compose exec web python manage.py collectstatic --no-input
```
- Выполните команду для заполнения базы данными
```
docker-compose exec web python manage.py upload_ingredients
```
- Основной функционал готов, проверить работу можно через [админку](http://localhost/admin/) 
- Чтобы остановить и удалить контейнеры выполните команду
```
docker-compose down -v
```
