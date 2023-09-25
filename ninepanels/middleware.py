import json

from starlette.responses import JSONResponse
from starlette.responses import StreamingResponse
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .pydmodels import WrappedResponse
from .config import monitors

class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):


        response = await call_next(request)

        path = request.scope.get("path")
        unwrapped_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
        ]


        referer = request.headers.get('referer')

        if referer:
            if '/docs' in referer:
                unwrapped_paths.append("/token")

        if path in unwrapped_paths:
            return response

        wrapped_response = WrappedResponse(
            data = {},
            status_code=200,
            is_error=False,
            error_message=None,
            meta=None
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
                wrapped_response.error_message = original_json['detail']
            except KeyError:
                wrapped_response.error_message = "Not found"
            return JSONResponse(wrapped_response.model_dump(), status_code=response.status_code)

        if response.status_code >= 400:
            wrapped_response.data = original_json
            wrapped_response.is_error = True
            wrapped_response.status_code = response.status_code
            try:
                if response.status_code == 422:
                    wrapped_response.error_message = original_json['detail'][0]['msg']
                else:
                    wrapped_response.error_message = original_json['detail']
            except KeyError:
                wrapped_response.error_message = "No error detail provided"
            return JSONResponse(wrapped_response.model_dump(), status_code=response.status_code)

        else:
            wrapped_response.data = original_json
            wrapped_response.is_error = False
            wrapped_response.status_code = response.status_code

        return JSONResponse(wrapped_response.model_dump(), status_code=response.status_code)

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pass