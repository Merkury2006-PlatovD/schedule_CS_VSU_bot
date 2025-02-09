import os
import sqlite3


class DBController:
    cursor = None
    conn = None

    @classmethod
    def start_db_control(cls, db_path):
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        # подключение к БД
        cls.conn = sqlite3.connect(db_path, check_same_thread=False)
        cls.cursor = cls.conn.cursor()

        cls.init_tables_if_not_exists()

    @classmethod
    def init_tables_if_not_exists(cls):
        # создание таблицы в БД при первом включении
        cls.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            course INTEGER,
            group_num INTEGER,
            subgroup INTEGER
        );
        """)

        # Создаем таблицу, где ключ - это название переменной
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,  -- Название переменной (ключ)
                value TEXT             -- Значение переменной
            );
        """)

        cls.cursor.execute("""
               INSERT OR IGNORE INTO config (key, value) VALUES (?, ?);
           """, ("week_type", 0))
        cls.conn.commit()

    @classmethod
    def end_db_control(cls):
        """Закрывает соединение с БД."""
        if cls.conn:
            cls.conn.close()
            cls.conn = None
            cls.cursor = None

    @classmethod
    def user_exists(cls, user_id: int) -> bool:
        """
        Проверяет существование пользователя в БД.

        Args:
            user_id: tg id пользователя.

        Returns:
            bool: факт существования данного пользователя в БД.
        """
        cls.cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id=?)", (user_id,))
        return cls.cursor.fetchone()[0]

    @classmethod
    def add_user(cls, user_id):
        """
        Добавляет в БД запись с pk = user_id.

        Args:
            user_id: tg id пользователя.
        """
        cls.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        cls.conn.commit()

    @classmethod
    def update_user(cls, user_id, column, value):
        """
        Обновляет значение определенного поля зарегестрированного пользователя

        Args:
            user_id: tg id пользователя.
            column: поле, которое нужно изменить.
            value: новое значение изменяемого поля.
        """
        cls.cursor.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
        cls.conn.commit()

    @classmethod
    def get_user_data(cls, user_id):
        """
        Получает данные пользователя из БД.

        Args:
            user_id: tg id пользователя.

        Returns:
            tuple: номер курса, группы и подгруппы пользователя.
        """
        cls.cursor.execute("SELECT course, group_num, subgroup FROM users WHERE user_id = ?", (user_id,))
        return cls.cursor.fetchone()

    @classmethod
    def get_current_week_type(cls):
        cls.cursor.execute("SELECT value FROM config WHERE key = ?", ("week_type",))
        return int(cls.cursor.fetchone()[0])

    @classmethod
    def update_current_week_type(cls, new_week_type):
        cls.cursor.execute("UPDATE config SET value = ? WHERE key = ?", (str(new_week_type), "week_type"))
        cls.conn.commit()
