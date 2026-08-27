FROM python:3.11-slim

RUN useradd --create-home --uid 1000 tingle
WORKDIR /app

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
RUN chown -R tingle:tingle /app
USER tingle

CMD ["pytest"]
