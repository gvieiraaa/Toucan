FROM python:3.11.4-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

COPY . /app

CMD ["python3", "main.py"]