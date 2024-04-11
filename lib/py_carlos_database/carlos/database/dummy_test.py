from sqlalchemy.ext.asyncio import AsyncConnection


def test_dummy(async_carlos_db_connection: AsyncConnection):
    assert True
