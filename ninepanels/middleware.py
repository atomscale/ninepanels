import json
import logging
import uuid

from starlette.responses import JSONResponse
from starlette.responses import StreamingResponse
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

from . import pydmodels as pyd
from . import config
from . import timing


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        path = request.scope.get("path")
        unwrapped_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

        referer = request.headers.get("referer")

        if referer:
            if "/docs" in referer:
                unwrapped_paths.append("/token")

        if path in unwrapped_paths:
            return response

        wrapped_response = pyd.WrappedResponse(
            data={}, status_code=200, is_error=False, error_message=None, meta=None
        )

        # TODO when would it ever be a non-streaming response type?
        if isinstance(response, StreamingResponse):
            body_content = b""
            async for chunk in response.body_iterator:
                body_content += chunk

            original_content = body_content.decode()
            try:
                original_json = json.loads(original_content)
            except json.JSONDecodeError:
                original_json = original_content

        if response.status_code == 404:
            wrapped_response.is_error = True
            wrapped_response.status_code = response.status_code
            try:
                wrapped_response.error_message = original_json["detail"]
            except KeyError:
                wrapped_response.error_message = "Not found"
            return JSONResponse(
                wrapped_response.model_dump(), status_code=response.status_code
            )

        if response.status_code >= 400:
            wrapped_response.data = original_json
            wrapped_response.is_error = True
            wrapped_response.status_code = response.status_code
            try:
                if response.status_code == 422:
                    wrapped_response.error_message = original_json["detail"][0]["msg"]
                else:
                    wrapped_response.error_message = original_json["detail"]
            except KeyError:
                wrapped_response.error_message = "No error detail provided"
            return JSONResponse(
                wrapped_response.model_dump(), status_code=response.status_code
            )

        else:
            wrapped_response.data = original_json
            wrapped_response.is_error = False
            wrapped_response.status_code = response.status_code

        return JSONResponse(
            wrapped_response.model_dump(), status_code=response.status_code
        )


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        route_timer = None
        request_id = str(uuid.uuid4())
        path = "no_path"
        headers = request.headers

        try:
            request_id = headers["X-Request-ID"]
        except KeyError as e:
            logging.warn("no request id (probably /docs calling)")

        try:
            path = request.url.path
        except Exception as e:
            logging.warn("no path")

        try:
            method = request.method
        except Exception as e:
            logging.warn("no method")

        try:
            route_timer = timing.Timer(
                method=method,
                request_id=request_id,
                path=path,
            )
            route_timer.start()
        except Exception as e:
            msg = pyd.LogMessage(level="warn", detail="issue with route timer at start call")
            logging.warn(msg)
        response = await call_next(request)

        try:
            if route_timer:
                await route_timer.stop()

        except Exception as e:
            msg = pyd.LogMessage(level="warn", detail="issue with route timer at stop call")
            logging.warn(msg)

        return response