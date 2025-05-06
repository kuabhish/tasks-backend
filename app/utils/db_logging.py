# app/utils/db_logging.py
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging
from flask import current_app

# Use the existing rtime_logger
from .logger import rtime_logger

def setup_db_logging(db):
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.perf_counter())

    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        query_time_ms = (time.perf_counter() - conn.info['query_start_time'].pop()) * 1000
        statement_truncated = (statement[:100] + '...') if len(statement) > 100 else statement
        rtime_logger.info(
            f"Query: {statement_truncated}, "
            f"QueryTimeMs: {query_time_ms:.2f}, "
            f"Parameters: {parameters}"
        )

    # Defer event listener attachment until the engine is available
    def attach_listeners():
        with current_app.app_context():  # Ensure app context
            if db.engine:  # Check if engine is initialized
                event.listen(db.engine, "before_cursor_execute", before_cursor_execute)
                event.listen(db.engine, "after_cursor_execute", after_cursor_execute)
            else:
                rtime_logger.error("Database engine not initialized")

    # Schedule listener attachment after app is fully initialized
    with current_app.app_context():
        attach_listeners()