FROM python:3.12-slim
WORKDIR /app/agents
COPY . .
RUN pip install --no-cache-dir .
EXPOSE 8090
CMD ["python", "-m", "keel_agents.host"]
