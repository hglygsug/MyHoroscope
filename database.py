import psycopg2
from hashlib import md5


def get_connection():
    return psycopg2.connect(
        dbname="horoscope",
        user="postgres",
        password="admin",
        host="localhost"
    )


def register_user(username, password, birth_date):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_password = md5(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password, birth_date) VALUES (%s, %s, %s)",
            (username, hashed_password, birth_date)
        )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False
    finally:
        conn.close()


def check_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, birth_date, about FROM users WHERE username = %s",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        hashed_password = md5(password.encode()).hexdigest()
        if hashed_password == result[0]:
            return True, {
                "birth_date": result[1],
                "about": result[2] if result[2] else ""
            }
    return False, None


def update_user_info(username, about_text):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET about = %s WHERE username = %s",
            (about_text, username)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, birth_date, about FROM users")
    users = []
    for row in cursor.fetchall():
        users.append({
            "username": row[0],
            "birth_date": row[1],
            "about": row[2] if row[2] else ""
        })
    conn.close()
    return users


def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        return cursor.rowcount > 0
    except:
        return False
    finally:
        conn.close()


def update_user(username, birth_date, about):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET birth_date = %s, about = %s WHERE username = %s",
            (birth_date, about, username)
        )
        conn.commit()
        return cursor.rowcount > 0
    except:
        return False
    finally:
        conn.close()


def get_all_predictions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT zodiac_sign, week_start, prediction FROM predictions")
    predictions = []
    for row in cursor.fetchall():
        predictions.append({
            "zodiac_sign": row[0],
            "week_start": row[1],
            "prediction": row[2]
        })
    conn.close()
    return predictions


def update_prediction(zodiac_sign, week_start, prediction):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE predictions SET prediction = %s WHERE zodiac_sign = %s AND week_start = %s",
            (prediction, zodiac_sign, week_start)
        )
        conn.commit()
        return cursor.rowcount > 0
    except:
        return False
    finally:
        conn.close()


def add_prediction(zodiac_sign, week_start, prediction):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO predictions (zodiac_sign, week_start, prediction) VALUES (%s, %s, %s)",
            (zodiac_sign, week_start, prediction)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def get_prediction(zodiac_sign, week_start):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT prediction FROM predictions WHERE zodiac_sign = %s AND week_start = %s",
        (zodiac_sign, week_start)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Гороскоп пока не готов!"