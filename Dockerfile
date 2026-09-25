FROM python:3.11-slim

# Tizim paketlarini va FFmpegni o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Ishchi papkani yaratish
WORKDIR /app

# Talab qilingan kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini nusxalash
COPY . .

# Render kutadigan standart port
ENV PORT=8080
EXPOSE 8080

# Botni ishga tushirish
CMD ["python", "bot.py"]
