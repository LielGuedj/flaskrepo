import requests
import time

BASE_URL = "http://todo_flask:5000"

def wait_for_app():
    for i in range(15):
        try:
            r = requests.get(BASE_URL)
            if r.status_code == 200:
                print("🟢 Flask app is up")
                return
        except requests.exceptions.ConnectionError:
            pass
        print("⏳ Waiting for Flask app...")
        time.sleep(2)
    raise Exception("❌ Flask app not responding")

def test_add_todo_and_get_joke():
    wait_for_app()

    # הוספת טודו
    r = requests.post(f"{BASE_URL}/add", data={"title": "mission"})
    assert r.status_code == 200 or r.status_code == 302

    # בדיקה שהתוכן מופיע בדף הבית (כולל בדיחה)
    r = requests.get(BASE_URL)
    assert r.status_code == 200
    assert b"mission" in r.content
    assert b"Chuck Norris" in r.content or b"joke" in r.content or b"Error fetching joke" in r.content
