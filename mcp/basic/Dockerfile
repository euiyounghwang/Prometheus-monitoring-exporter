FROM python:3.13-slim

# pip 업그레이드
# RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "server.py"]