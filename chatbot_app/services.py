from typing import Generator, List
import logging
import json
import openai
from openai.types.chat import ChatCompletionMessageParam
import os
from django.core.files.uploadedfile import UploadedFile
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, client: openai.Client):
        self.client = client

    def stream_response(self, messages: List[ChatCompletionMessageParam]) -> Generator[str, None, None]:
        """
        Stream responses from OpenAI's chat completion API.

        Args:
            messages: List of message objects containing role and content.
                     Example: [{"role": "user", "content": "Hello"}]

        Yields:
            str: Either content chunks from OpenAI's response or a JSON error message.

        Raises:
            No exceptions are raised as errors are caught and yielded as JSON strings.
        """
        try:
            logger.info(f"Making OpenAI API call with messages: {messages}")
            
            # Get the LLM response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True
            )
            
            # Loop over the stream and yield back the chunks to the UI (streaming)
            logger.debug("Started receiving OpenAI stream response")
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    logger.debug(f"Streaming chunk: {content}")
                    yield content
                    
        except Exception as e:
            logger.error(f"Error in OpenAI stream: {str(e)}", exc_info=True)
            yield json.dumps({"error": str(e)})


class VoiceToTextService:
    def __init__(self, client: openai.Client):
        self.client = client
        
    def transcribe_audio(self, audio_file: UploadedFile) -> Dict[str, Optional[str]]:
        """
        Transcribe audio file using OpenAI's Whisper model.
        
        Args:
            audio_file: Django UploadedFile object containing the audio to transcribe
            
        Returns:
            Dict containing either the transcript or error message
            
        Example:
            {"transcript": "Hello world"} or {"error": "Error message"}
        """
        try:
            # Create temporary file path
            tmp_file_path = os.path.join("/tmp", str(audio_file.name))
            
            # Write uploaded file to temporary location
            with open(tmp_file_path, 'wb') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
            
            # Transcribe the audio file
            with open(tmp_file_path, 'rb') as audio_data:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data,
                    response_format="text"
                )
            
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
                
            return {"transcript": transcript}
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
            return {"error": str(e)}