FROM python:3.12.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests

COPY . /app

# ENV GROUP_ID=123456
# ENV TOKEN_GOD=your_token_here

CMD ["python", "-u", "main.py"]