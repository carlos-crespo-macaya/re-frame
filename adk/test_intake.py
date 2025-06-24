#!/usr/bin/env python3
"""Direct test of intake agent behavior."""

import os
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', '')

from google.adk.agents import Agent as LlmAgent
from google.genai import Client, types

# Test just the intake agent instructions
test_prompt = """You are AURA, a warm counselor.

CRITICAL RULES:
1. ONLY respond to the CURRENT user message
2. Ask ONE question at a time and WAIT
3. Do NOT extract information from the initial message
4. Have a turn-based conversation

User just said: "I feel stupid after that meeting"

What is your response?"""

client = Client(api_key=os.environ['GOOGLE_API_KEY'])
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=test_prompt
)

print("Agent response:")
print(response.text)