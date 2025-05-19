FROM python:3.12

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD sh -c "echo '⏳ מחכה ל-MySQL...' && sleep 10 && echo '🚀 מפעיל את Flask' && python3 app.py"

EXPOSE 5000