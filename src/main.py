import uvicorn

from fastapi import FastAPI
from api import api_router
from utils.logger import logger
from middlewares.middlewares import init_middlewares
from utils.env import API_PORT, API_HOST,  API_VERSION_STR, PROJECT_NAME

app = FastAPI(
    title=PROJECT_NAME
)

app.include_router(api_router, prefix=API_VERSION_STR)
init_middlewares(app)

if __name__ == '__main__':
    logger.info('Starting server...')
    uvicorn.run(app, host=API_HOST, port=API_PORT)
