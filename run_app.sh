docker compose up db -d
docker compose build web
docker compose up -d
docker compose exec web python manage.py migrate --noinput