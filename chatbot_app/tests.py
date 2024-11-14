from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
import json

class ChatbotTests(APITestCase):

   @patch('chatbot_app.views.client')  # Patch the OpenAI client instance in views.py
   def test_successful_chat(self, mock_client):
       """Test successful chat interaction with mocked OpenAI response"""
       # Create a fake OpenAI response chunk that mimics the structure:
       # chunk.choices[0].delta.content
       mock_chunk = type('MockChunk', (), {
           'choices': [
               type('Choice', (), {
                   'delta': type('Delta', (), {'content': 'Hello tester!!'})
               })
           ]
       })
       
       # Configure the mock client to return this fake chunk when called
       mock_client.chat.completions.create.return_value = [mock_chunk]
       
       # Create test message data that matches what frontend would send
       data = {
           "messages": [
               {"role": "user", "content": "Testing testing..."}
           ]
       }
       
       # Make POST request to the chatbot endpoint
       response = self.client.post('/api/chat/', data, format='json')
       
       # Check response status is OK (200)
       self.assertEqual(response.status_code, status.HTTP_200_OK)
       
       # Get content from streaming response and check it matches the mock
       content = b''.join(response.streaming_content).decode('utf-8')
       self.assertEqual(content, 'Hello tester!!')

   @patch('chatbot_app.views.client')  # Patch the OpenAI client instance in views.py
   def test_openai_error_handling(self, mock_client):
       """Test handling of OpenAI API errors"""
       # Configure mock to raise an exception when called
       mock_client.chat.completions.create.side_effect = Exception("API Error")

       # Create test message data
       data = {
           "messages": [
               {"role": "user", "content": "Testing testing..."}
           ]
       }
       
       # Make POST request to the chatbot endpoint 
       response = self.client.post('/api/chat/', data, format='json')
       
       # Check response status is still OK since we handle errors gracefully
       self.assertEqual(response.status_code, status.HTTP_200_OK)
       
       # Get content from streaming response and parse JSON
       content = b''.join(response.streaming_content).decode('utf-8')
       error_response = json.loads(content)
       
       # Verify error message matches what we expect
       self.assertEqual(error_response, {"error": "API Error"})