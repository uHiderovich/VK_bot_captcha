FROM python:3.12.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get upgrade -y && \
  pip install --no-cache-dir -r requirements.txt

# --------------

FROM python:3.12.11-slim
WORKDIR /app
COPY --from=builder /app /app

# ENV GROUP_ID=123456
# ENV TOKEN_GOD=your_token_here

CMD ["python", "-u", "main.py"]