from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppBaseException(Exception):
    status_code = 400


class PaymentNotFoundError(AppBaseException):
    status_code = 404


class PaymentAlreadyExistsError(AppBaseException):
    status_code = 409


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppBaseException)
    async def base_app_handler(request: Request, exc: AppBaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": [{"msg": str(exc), "type": exc.__class__.__name__}]
            },
        )
