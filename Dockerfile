FROM python:3.9-slim

WORKDIR /app

# System deps for Kivy (SDL2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py game_utils.py config.json ./

ENV KIVY_NO_ARGS=1

CMD ["python", "main.py"]
