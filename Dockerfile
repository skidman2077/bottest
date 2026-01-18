FROM python:3.10-slim

# Cài đặt Lua 5.1
RUN apt-get update && apt-get install -y \
    lua5.1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Clone WeAreDevs-Deobfuscator repository
RUN git clone https://github.com/hutaoshusband/WeAreDevs-Deobfuscator.git /app/deobfuscator

# Copy bot code
COPY bot.py /app/
COPY requirements.txt /app/

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Chạy bot
CMD ["python", "bot.py"]
