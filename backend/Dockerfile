FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ENV VIRTUAL_ENV=/app/venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH" 

COPY requirements.txt /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-cache -r /app/requirements.txt
    
COPY ./app /app/app

EXPOSE 8000

CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "app/main.py"]
