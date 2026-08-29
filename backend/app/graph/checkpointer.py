from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import get_settings

_saver_ctx = None
_saver: AsyncPostgresSaver | None = None


async def init_checkpointer() -> AsyncPostgresSaver:
    global _saver, _saver_ctx
    if _saver is None:
        settings = get_settings()
        _saver_ctx = AsyncPostgresSaver.from_conn_string(settings.langgraph_db_url)
        _saver = await _saver_ctx.__aenter__()
        await _saver.setup()  # creates checkpoint tables if they don't exist — idempotent
    return _saver


async def close_checkpointer() -> None:
    global _saver, _saver_ctx
    if _saver_ctx is not None:
        await _saver_ctx.__aexit__(None, None, None)
        _saver = None
        _saver_ctx = None


def get_checkpointer() -> AsyncPostgresSaver:
    if _saver is None:
        raise RuntimeError("Checkpointer not initialized — call init_checkpointer() at app startup")
    return _saver