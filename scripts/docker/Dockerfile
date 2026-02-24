FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
CMD ["python", "-m", "qticket.cli", "run-node", "--role", "anchor", "--port", "8001"]
