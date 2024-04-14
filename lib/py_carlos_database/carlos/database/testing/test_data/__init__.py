from pathlib import Path

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

TEST_DATA_PATH = Path(__file__).parent


def is_sql_file(file: Path) -> bool:
    """Returns true if the path is a .sql file."""
    return file.is_file() and file.suffix.lower() == ".sql"


async def insert_carlos_database_test_data(connection: AsyncConnection):
    """Inserts the test data into the database."""
    for sql_file in sorted(filter(is_sql_file, TEST_DATA_PATH.iterdir())):
        logger.info(f"Inserting test data from {sql_file.relative_to(TEST_DATA_PATH)}")
        await connection.execute(text(sql_file.read_text()))
    await connection.commit()
