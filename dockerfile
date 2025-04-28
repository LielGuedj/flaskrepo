FROM python:latest
WORKDIR /app
COPY . .
RUN pip install -r requirments.txt
CMD ["python", "app.py"]
EXPOSE 5000

