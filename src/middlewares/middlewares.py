import sys
import time
import inspect

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class ProcessTime(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = round(time.time() - start_time, 4)
        response.headers["X-Process-Time"] = str(process_time)
        return response


def init_middlewares(app):
    middlewares = inspect.getmembers(
        sys.modules[__name__], lambda member: inspect.isclass(member) and member.__module__ == __name__ and inspect.isclass
    )

    for middleware in middlewares:
        app.add_middleware(middleware[1])
