import logging

from django.http import StreamingHttpResponse

logger = logging.getLogger(__name__)

class ResponseLoggingMiddleware:
    """
    For debugging streaming response. Logs the outgoing chunks
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, StreamingHttpResponse):
            # If it's a streaming response, wrap the streaming generator
            original_content = response.streaming_content

            def wrapped_content():
                for chunk in original_content:
                    logger.debug(f"Middleware streaming chunk: {chunk}")
                    yield chunk

            response.streaming_content = wrapped_content()
        return response
