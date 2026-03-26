#!/bin/sh
set -e

echo "Применяем миграции"
alembic upgrade head
echo "Миграции применены"

echo "Запускаем приложение"
exec "$@"