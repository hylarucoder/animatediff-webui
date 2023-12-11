import json
import time

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from animatediff.exceptions import ApiException, UnicornException, unicorn_exception_handler


def setup_error_handlers(app: FastAPI):
    app.add_exception_handler(UnicornException, unicorn_exception_handler)

    async def validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "message": "参数错误",
                "errors": exc.errors(),
            },
        )

    app.add_exception_handler(ValidationError, validation_handler)

    app.add_exception_handler(ApiException, lambda request, err: err.to_result())

    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    app.add_exception_handler(HTTPException, http_exception_handler)

    def handle_exc(request: Request, exc):
        raise exc

    app.add_exception_handler(Exception, handle_exc)


def create_bp(dependencies: list = None) -> FastAPI:
    if not dependencies:
        dependencies = []
    app = FastAPI(dependencies=dependencies)
    setup_error_handlers(app)
    return app


def setup_routers(app: FastAPI):
    create_bp()
    from animatediff.apps.file_explorer.views import bp as bp_file_explorer
    from animatediff.apps.user.views import bp as bp_user

    app.include_router(bp_user)
    app.include_router(bp_file_explorer)


def setup_cli(app: FastAPI):
    pass


def setup_logging(app: FastAPI):
    pass


def setup_middleware(app: FastAPI):
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_static_files(app: FastAPI):
    ...
    # static_files_app = StaticFiles(directory="static")
    # app.mount(path="static", app=static_files_app, name="static")


def create_app():
    app = FastAPI(
        debug=True,
        title="Animatediff WebUI",
        description="Animatediff WebUI Description",
    )
    app.add_exception_handler(
        ApiException, lambda req, e: Response(status_code=e.status_code, content=json.dumps({"message": e.detail}))
    )
    setup_routers(app)
    setup_static_files(app)
    setup_middleware(app)
    setup_logging(app)
    return app


current_app = create_app()
