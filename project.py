import random
import sqlite3

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None
    MySQLError = Exception


CATEGORIES = {
    1: "Countries and their capitals",
    2: "Countries and their currencies",
    3: "Indian States and their capitals",
}

# Original scoring scheme: +4 for correct, -1 for incorrect.
CORRECT_SCORE = 4
WRONG_SCORE = -1
QUESTIONS_PER_ATTEMPT = 10


def get_connection(db_type="sqlite", db_path="quiz.db", mysql_config=None):
    """Create a database connection for either SQLite or MySQL."""
    try:
        if db_type.lower() == "sqlite":
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

        if db_type.lower() == "mysql":
            if mysql is None:
                raise RuntimeError(
                    "mysql-connector-python is not installed. "
                    "Run: pip install mysql-connector-python"
                )
            config = mysql_config or {
                "host": "localhost",
                "user": "root",
                "password": "root",
                "database": "quiz_app",
            }
            return mysql.connector.connect(**config)

        raise ValueError("Database type must be 'sqlite' or 'mysql'.")

    except Exception as exc:
        raise ConnectionError(f"Could not connect to {db_type} database: {exc}") from exc


def create_schema(conn):
    """Create a normalized schema: categories, questions and options."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        )
    """)

    # SQLite accepts AUTOINCREMENT; MySQL needs AUTO_INCREMENT.
    # This function is primarily used by SQLite. MySQL schema is in database_mysql.sql.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            question_text VARCHAR(255) NOT NULL,
            correct_option INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS options (
            option_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            option_number INTEGER NOT NULL,
            option_text VARCHAR(100) NOT NULL,
            UNIQUE(question_id, option_number),
            FOREIGN KEY (question_id) REFERENCES questions(question_id)
                ON DELETE CASCADE
        )
    """)

    for category_id, name in CATEGORIES.items():
        cursor.execute(
            "INSERT OR IGNORE INTO categories(category_id, name) VALUES (?, ?)",
            (category_id, name),
        )

    conn.commit()
    cursor.close()


def seed_sqlite(conn):
    """Populate SQLite with the original quiz content."""
    data = [
        (1, "What is the capital of Cuba?", ["Havana", "Beijing", "Sierraleone", "Ulaanbaatar"], 1),
        (1, "What is the capital of Denmark?", ["Helsinki", "Tokyo", "Copenhagen", "New Delhi"], 3),
        (1, "What is the capital of Niger?", ["Havana", "Niamey", "Capetown", "Seoul"], 2),
        (1, "What is the capital of Italy?", ["Istanbul", "Rome", "Huyana", "Berlin"], 2),
        (1, "What is the capital of Germany?", ["Tokyo", "Berlin", "Castries", "Ulaanbaatar"], 2),
        (1, "What is the capital of Switzerland?", ["Sydney", "Rio", "Pyongyang", "Bern"], 4),
        (1, "What is the capital of North Korea?", ["Pyongyang", "Newyork", "London", "Paris"], 1),
        (1, "What is the capital of Argentina?", ["Montevideo", "BuenosAires", "Rio", "Asunción"], 2),
        (1, "What is the capital of Sri Lanka?", ["Chennai", "Kandy", "Colombo", "Male"], 3),
        (1, "What is the capital of Ethiopia?", ["Juba", "Khartoum", "Mogadishu", "AddisAbaba"], 4),
        (1, "What is the capital of Mexico?", ["MexicoCity", "Montreal", "Tegucigalpa", "Ulaanbaatar"], 1),
        (1, "What is the capital of Belgium?", ["Amsterdam", "Brussels", "Paris", "Luxembourg"], 2),
        (1, "What is the capital of Nigeria?", ["Havana", "Niamey", "Abuja", "Khartoum"], 3),
        (1, "What is the capital of China?", ["Hangzhou", "Tianjin", "Chengdu", "Beijing"], 4),
        (1, "What is the capital of France?", ["Paris", "Berlin", "Brussels", "London"], 1),
        (1, "What is the capital of Ghana?", ["Obuasi", "Accra", "Kumasi", "Sunyani"], 2),

        (2, "What is the Currency of Cuba?", ["Peso", "Dollar", "Yuan", "Euro"], 1),
        (2, "What is the Currency of Denmark?", ["Riyal", "Krone", "Mark", "Rupee"], 2),
        (2, "What is the Currency of Niger?", ["Manat", "Tenge", "Franc", "Spesmilo"], 3),
        (2, "What is the Currency of Italy?", ["Manat", "Dollar", "Sheqel", "Euro"], 4),
        (2, "What is the Currency of Germany?", ["Euro", "Tenge", "Dollar", "Franc"], 1),
        (2, "What is the Currency of Switzerland?", ["Euro", "Franc", "Dollar", "Riyal"], 2),
        (2, "What is the Currency of North Korea?", ["Yuan", "Ruble", "Won", "Yen"], 3),
        (2, "What is the Currency of Argentina?", ["Euro", "Rupee", "Dollar", "Peso"], 4),
        (2, "What is the Currency of Sri Lanka?", ["Rupee", "Rufiyaa", "Taka", "Peso"], 1),
        (2, "What is the Currency of Ethiopia?", ["Franc", "Birr", "Naira", "Pound"], 2),
        (2, "What is the Currency of Mexico?", ["Pound", "Euro", "Peso", "Dollar"], 3),
        (2, "What is the Currency of Belgium?", ["Peso", "Franc", "Dollar", "Euro"], 4),
        (2, "What is the Currency of Nigeria?", ["Naira", "Niamey", "Dollar", "Euro"], 1),
        (2, "What is the Currency of China?", ["Yen", "Yuan", "Dong", "Won"], 2),
        (2, "What is the Currency of France?", ["Pound", "Franc", "Euro", "Dollar"], 3),
        (2, "What is the Currency of Ghana?", ["Franc", "Naira", "Tenge", "Cedi"], 4),

        (3, "What is the capital of Chattisgarh?", ["Raipur", "Korba", "Bhilai", "Bilaspur"], 1),
        (3, "What is the capital of Assam?", ["Haflong", "Tezpur", "Dispur", "Guwahati"], 3),
        (3, "What is the capital of Uttar Pradesh?", ["Prayagraj", "Lucknow", "Kanpur", "Varanasi"], 2),
        (3, "What is the capital of Bihar?", ["Gaya", "Patna", "Bhagalpur", "Darbhanga"], 2),
        (3, "What is the capital of Goa?", ["Mapusa", "Panaji", "Castries", "Ponda"], 2),
        (3, "What is the capital of Sikkim?", ["Mangan", "Soreng", "Pakyong", "Gangtok"], 4),
        (3, "What is the capital of Nagaland?", ["Kohima", "Dimapur", "Mokokchung", "Phek"], 1),
        (3, "What is the capital of Arunachal Pradesh?", ["Seppa", "Itanagar", "Wakro", "Gandhigram"], 2),
        (3, "What is the capital of Mizoram?", ["Kolasib", "Champhai", "Aizawl", "Mamit"], 3),
        (3, "What is the capital of Gujarat?", ["Surat", "Bhuj", "Ahmedabad", "Gandhinagar"], 4),
        (3, "What is the capital of Tamil Nadu?", ["Chennai", "Coimbatore", "Vellore", "Madurai"], 1),
        (3, "What is the capital of Kerala?", ["Kozhikode", "Kochi", "Kannur", "Thiruvananthapuram"], 4),
        (3, "What is the capital of Himachal Pradesh?", ["Manali", "Shimla", "Chamba", "Solan"], 2),
        (3, "What is the capital of Meghalaya?", ["Bhagmara", "Jowai", "Shillong", "Mairang"], 3),
    ]

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] > 0:
        cursor.close()
        return

    for category_id, question_text, options, correct_option in data:
        cursor.execute(
            "INSERT INTO questions(category_id, question_text, correct_option) VALUES (?, ?, ?)",
            (category_id, question_text, correct_option),
        )
        question_id = cursor.lastrowid
        for number, option_text in enumerate(options, 1):
            cursor.execute(
                "INSERT INTO options(question_id, option_number, option_text) VALUES (?, ?, ?)",
                (question_id, number, option_text),
            )

    conn.commit()
    cursor.close()


def fetch_questions(conn, category_id):
    """Fetch all questions for a category using a normalized schema."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.question_id, q.question_text, q.correct_option,
               o.option_number, o.option_text
        FROM questions q
        JOIN options o ON q.question_id = o.question_id
        WHERE q.category_id = ?
        ORDER BY q.question_id, o.option_number
    """, (category_id,))

    rows = cursor.fetchall()
    cursor.close()

    questions = {}
    for question_id, text, correct, number, option_text in rows:
        if question_id not in questions:
            questions[question_id] = {
                "question": text,
                "options": [],
                "correct": correct,
            }
        questions[question_id]["options"].append(option_text)

    return list(questions.values())


def calculate_score(answers, correct_answers):
    """Calculate score using +4/-1 scoring."""
    return sum(
        CORRECT_SCORE if answer == correct else WRONG_SCORE
        for answer, correct in zip(answers, correct_answers)
    )


def run_quiz(conn, category_id, question_count=QUESTIONS_PER_ATTEMPT, input_fn=input):
    questions = fetch_questions(conn, category_id)
    if not questions:
        raise ValueError("No questions found for the selected category.")

    random.shuffle(questions)
    selected = questions[:min(question_count, len(questions))]

    answers = []
    correct_answers = []

    for number, item in enumerate(selected, 1):
        print(f"\nQuestion {number}: {item['question']}")
        for index, option in enumerate(item["options"], 1):
            print(f"{index}. {option}")

        while True:
            try:
                choice = int(input_fn("Enter the preferred option (1-4): "))
                if choice not in range(1, 5):
                    raise ValueError
                break
            except (ValueError, TypeError):
                print("Invalid input. Please enter a number from 1 to 4.")

        answers.append(choice)
        correct_answers.append(item["correct"])

    score = calculate_score(answers, correct_answers)
    print("\nFinal Score -->", score)
    return score


def start():
    print("*" * 100)
    print("""QUIZ
PREPARED BY
1. Saket Kumar Pandey
2. Priyanshu Kumar Singh
3. Mohd.Arqum""")
    print("""
The Quiz consists of a single round:
For every correct answer: 4 points will be rewarded.
For every incorrect answer: 1 point will be deducted.
""")
    print("*" * 100)


def initialize_sqlite(db_path="quiz.db"):
    conn = get_connection("sqlite", db_path=db_path)
    create_schema(conn)
    seed_sqlite(conn)
    return conn


def exec_quiz(db_type="sqlite", db_path="quiz.db", mysql_config=None, input_fn=input):
    start()
    print("""There are 3 types of quiz available here
1) Countries and their capitals
2) Countries and their currencies
3) Indian States and their capitals""")

    while True:
        try:
            choice = int(input_fn("Enter the no of quiz you want to play: "))
            if choice not in CATEGORIES:
                print("Wrong choice. Please select 1, 2 or 3.")
                continue
            break
        except (ValueError, TypeError):
            print("Invalid input. Please enter 1, 2 or 3.")

    conn = None
    try:
        conn = get_connection(db_type, db_path, mysql_config)
        if db_type.lower() == "sqlite":
            create_schema(conn)
            seed_sqlite(conn)
        return run_quiz(conn, choice, input_fn=input_fn)
    except (ConnectionError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        return None
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    while True:
        exec_quiz()
        again = input("If you want to reattempt the quiz press y: ")
        if again.strip().upper() != "Y":
            print("Thank You for attempting the quiz")
            break
