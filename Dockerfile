FROM python:3.12-slim
RUN groupadd -r fastapi && useradd -r -g fastapi userfastapi
WORKDIR /app
COPY requirements.txt . 
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=userfastapi:fastapi . .
COPY --chown=userfastapi:fastapi docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
USER userfastapi
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]