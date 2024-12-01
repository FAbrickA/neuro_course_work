import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score, f1_score
from sklearn.naive_bayes import GaussianNB
import joblib


def train_model():
    df = pd.read_csv("Modified_SQL_Dataset.csv")
    X = df['Query']
    y = df['Label']

    vectorizer = CountVectorizer(min_df=2, max_df=0.8)
    X = vectorizer.fit_transform(X.values.astype('U')).toarray()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=45)
    print(X_train.shape)
    print(y_train.shape)
    print(X_test.shape)
    print(y_test.shape)

    model = GaussianNB()

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(y_pred)

    print(f"Accuracy of Naive Bayes on test set : {accuracy_score(y_pred, y_test)}")
    print(f"F1 Score of Naive Bayes on test set : {f1_score(y_pred, y_test)}")

    # Сохранение модели
    joblib.dump(model, "./app/prediction_model.pkl")

    # Сохранение векторизатора
    joblib.dump(vectorizer, "./app/count_vectorizer.pkl")


def test_model():
    model = joblib.load("prediction_model.pkl")
    vectorizer = joblib.load("count_vectorizer.pkl")

    new_queries = [
        "SELECT * FROM users WHERE username = 'admin' OR '1'='1';",  # Пример инъекции
        "SELECT id, name FROM employees WHERE age > 30;",  # Пример безопасного запроса
        "DROP TABLE users; --",  # Пример инъекции
        "SELECT * FROM products WHERE product_id = 101;",  # Пример безопасного запроса
        "admin' OR '1'='1'; --",  # Пример инъекции
        "user1', '-'); DELETE FROM users; --",  # Пример инъекции
        "user2', '-'); INSERT INTO users (username, password) VALUES ('hacker', 'password'); --", # Пример инъекции
        "user3', '-'); INSERT INTO users (username, password) VALUES ('admin', 'password'); --", # Пример инъекции
        "user4', '-'); UPDATE users SET password = 'newpassword' WHERE username = 'admin'; --", # Пример инъекции
        "user5', '-'); SELECT pg_sleep(5); --", # Пример инъекции
        "user6', '-'); UPDATE users SET username = 'users_in_the_table: ' || (SELECT COUNT(1) FROM users) WHERE username " # Пример инъекции
        "= 'user6'; --", # Пример инъекции
    ]

    new_queries_transformed = vectorizer.transform(new_queries).toarray()

    predictions = model.predict(new_queries_transformed)

    for query, prediction in zip(new_queries, predictions):
        label = "SQL Injection" if prediction == 1 else "Safe Query"
        print(f"Query: {query}\nPrediction: {label}\n")


if __name__ == "__main__":
    train_model()
    test_model()