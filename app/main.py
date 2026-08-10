from fastapi import FastAPI

from app.core.errors import AppError, app_error_handler, error_handler

app = FastAPI(title="Veda", version="1.0")
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, error_handler)
