FROM python:3.11-slim

WORKDIR /app

COPY GZ-INVESTS.py .

EXPOSE 8080

CMD ["python", "-u", "GZ-INVESTS.py"]
