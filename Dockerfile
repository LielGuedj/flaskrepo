FROM python:3.11-slim

WORKDIR /app

# העתקת כל הקבצים פנימה
COPY . .

# התקנת תלויות
RUN pip install --no-cache-dir -r requirements.txt

# חשיפת פורט (לא חובה אבל עוזר לתיעוד / קונסולות ניהול)
EXPOSE 5000

# הפעלת האפליקציה
CMD ["python", "app.py"]
