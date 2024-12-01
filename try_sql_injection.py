from uuid import uuid4
import requests

# Адрес приложения
url = "http://localhost:8081/register/"


def registration(username: str, password: str):
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=payload)
    print(f"Response: {response.status_code}, {response.text}")
    return response.status_code


sql_injections = [
    "user1', '-'); DELETE FROM users; --",
    "user2', '-'); INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
    "user3', '-'); INSERT INTO users (username, password) VALUES ('admin', 'password'); --",
    "user4', '-'); UPDATE users SET password = 'newpassword' WHERE username = 'admin'; --",
    "user5', '-'); SELECT pg_sleep(5); --",
    "user6', '-'); UPDATE users SET username = 'users_in_the_table: ' || (SELECT COUNT(1) FROM users) WHERE username = 'user6'; --",
]
normal_usernames = [
    "someuser",
    "213421",
    "asdfsadf",
    "SELECTED_USER",
    "DROP TABLE",
    "INSERT admin_user",
]
def try_sql_injections():
    for injection in sql_injections:
        status = registration(username=injection, password='password')
        if status == 200:
            print('SQL-injection passed!!')
            print(injection)
        print()
    for username in normal_usernames:
        status = registration(username=username, password='password')
        if status == 400:
            print('Username rejected!!')
            print(username)
        print()


if __name__ == '__main__':
    # registration(username=str(uuid4()), password='password')
    try_sql_injections()
