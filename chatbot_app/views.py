# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.http import StreamingHttpResponse, HttpRequest
# from drf_spectacular.utils import extend_schema
# from .serializers import ChatbotInputSerializer
# import openai
# import os
# from dotenv import load_dotenv
# import logging
# from .services import ChatService

# # Setup logging
# logger = logging.getLogger(__name__)

# # # Configure OpenAI
# load_dotenv()
# openai.api_key = os.getenv('OPENAI_API_KEY')
# chat_service = ChatService(openai.Client())


# @extend_schema(
#     request=ChatbotInputSerializer,
#     responses={200: None},  # Streaming response can't be represented in OpenAPI
#     description="Streams a chat response from OpenAI API"
# )
# @api_view(['POST'])
# def chatbot(request: HttpRequest) -> StreamingHttpResponse:
#     """
#     Handle incoming chat requests and stream responses from OpenAI.

#     Args:
#         request: HTTP request object containing chat messages in the format:
#                 {"messages": [{"role": "user", "content": "Hello"}]}

#     Returns:
#         StreamingHttpResponse: A streaming response containing either:
#             - Text chunks from OpenAI's response
#             - JSON error message if something goes wrong
#             - 400 status with error message if no messages provided

#     Example:
#         POST /api/chat/
#         {"messages": [{"role": "user", "content": "Tell me a joke"}]}
#     """
#     logger.info(f"Received chatbot request from {request.META.get('REMOTE_ADDR')}")
    
#     # Get chat message from incoming request
#     messages = request.data.get('messages', [])
    
#     if not messages:
#         logger.warning("Received request with no messages")
#         return Response({"error": "Messages are required"}, status=400)
    
#     logger.info(f"Processing chat with {len(messages)} messages")
    
#     # Get LLM response and stream it back to the UI
#     return StreamingHttpResponse(
#         chat_service.stream_response(messages),
#         content_type="text/event-stream",
#         charset='utf-8' 
#     )


from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.http import StreamingHttpResponse, HttpRequest
from drf_spectacular.utils import extend_schema
from .serializers import ChatbotInputSerializer
import openai
import os
from dotenv import load_dotenv
import logging
from .services import ChatService, VoiceToTextService

# Setup logging
logger = logging.getLogger(__name__)

# Configure OpenAI
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.Client()
chat_service = ChatService(client)
voice_service = VoiceToTextService(client)

@extend_schema(
    request=ChatbotInputSerializer,
    responses={200: None},  # Streaming response can't be represented in OpenAPI
    description="Streams a chat response from OpenAI API"
)
@api_view(['POST'])
def chatbot(request: HttpRequest) -> StreamingHttpResponse:
    """
    Handle incoming chat requests and stream responses from OpenAI.

    Args:
        request: HTTP request object containing chat messages in the format:
                {"messages": [{"role": "user", "content": "Hello"}]}

    Returns:
        StreamingHttpResponse: A streaming response containing either:
            - Text chunks from OpenAI's response
            - JSON error message if something goes wrong
            - 400 status with error message if no messages provided

    Example:
        POST /api/chat/
        {"messages": [{"role": "user", "content": "Tell me a joke"}]}
    """
    logger.info(f"Received chatbot request from {request.META.get('REMOTE_ADDR')}")
    
    # Get chat message from incoming request
    messages = request.data.get('messages', [])
    
    if not messages:
        logger.warning("Received request with no messages")
        return Response({"error": "Messages are required"}, status=400)
    
    logger.info(f"Processing chat with {len(messages)} messages")
    
    # Get LLM response and stream it back to the UI
    return StreamingHttpResponse(
        chat_service.stream_response(messages),
        content_type="text/event-stream",
        charset='utf-8' 
    )

@extend_schema(
    description="Converts audio file to text using OpenAI Whisper",
    request={'multipart/form-data': {'audio': bytes}},
    responses={200: {'type': 'object', 'properties': {'transcript': {'type': 'string'}}}}
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
def voice_to_text(request: HttpRequest) -> Response:
    """
    Handle audio file upload and convert to text using OpenAI Whisper.

    Args:
        request: HTTP request object containing audio file in multipart/form-data

    Returns:
        Response: A JSON response containing either:
            - The transcript of the audio
            - Error message if something goes wrong
            - 400 status if no audio file provided

    Example:
        POST /api/voice-to-text/
        Content-Type: multipart/form-data
        Form Data: audio=@recording.wav
    """
    logger.info(f"Received voice-to-text request from {request.META.get('REMOTE_ADDR')}")

    if 'audio' not in request.FILES:
        logger.warning("Received request with no audio file")
        return Response({"error": "Audio file is required"}, status=400)

    audio_file = request.FILES['audio']
    logger.info(f"Processing audio file: {audio_file.name}")

    # Process the audio file and get the transcript
    result = voice_service.transcribe_audio(audio_file)

    if 'error' in result:
        logger.error(f"Error processing audio: {result['error']}")
        return Response(result, status=500)

    logger.info("Successfully transcribed audio")
    return Response(result, status=200)


