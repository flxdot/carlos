from fastapi import FastAPI

from .logging_patch import setup_logging

setup_logging()

app = FastAPI()
