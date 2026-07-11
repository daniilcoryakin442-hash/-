import aiosqlite

DB_PATH = "diet_bot.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    gender TEXT,
    age INTEGER,
    height REAL,
    weight REAL,
    activity TEXT,
    goal TEXT,
    calories REAL,
    protein REAL,
    fat REAL,
    carbs REAL
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_user(user_id: int, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await get_user(user_id)
        if existing:
            fields = ", ".join(f"{k} = ?" for k in data.keys())
            values = list(data.values()) + [user_id]
            await db.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
        else:
            data["user_id"] = user_id
            keys = ", ".join(data.keys())
            placeholders = ", ".join("?" for _ in data)
            await db.execute(
                f"INSERT INTO users ({keys}) VALUES ({placeholders})",
                list(data.values()),
            )
        await db.commit()


async def update_field(user_id: int, field: str, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()


async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()
