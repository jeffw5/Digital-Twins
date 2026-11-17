FROM python:3.12-slim
WORKDIR /app/keel-gateway
COPY . .
RUN pip install --no-cache-dir .
EXPOSE 8080
CMD ["python", "-m", "keel_gateway.server"]
