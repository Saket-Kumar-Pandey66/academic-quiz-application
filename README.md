# Academic Quiz Application

## Features
- Python CLI application
- SQLite and MySQL database support
- Normalized relational schema using categories, questions and options
- Randomized question sampling
- 10 questions per attempt
- +4 for a correct answer and -1 for an incorrect answer
- Input validation and structured exception handling
- Unit tests using Python unittest

## Run with SQLite
```bash
python project.py
```

SQLite is created automatically as `quiz.db`.

## Run tests
```bash
python -m unittest test_project.py -v
```

## MySQL
Install the connector:
```bash
pip install mysql-connector-python
```

The MySQL schema is provided in `database_mysql.sql`.

For MySQL execution, import the schema/data into the `quiz_app` database and call:
```python
exec_quiz(
    db_type="mysql",
    mysql_config={
        "host": "localhost",
        "user": "root",
        "password": "root",
        "database": "quiz_app"
    }
)
```
