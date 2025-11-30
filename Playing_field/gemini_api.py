import os
from google import genai
from google.genai import types


def connect_and_generate_code(user_prompt: str):
    """
    Connects to the Gemini API using an environment variable and generates content.

    The script attempts to use the GEMINI_API_KEY set in PyCharm's Run Configuration.
    """

    # 1. Retrieve the API Key from the environment variables
    # The client will automatically look for the GEMINI_API_KEY environment variable.
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not found.")
        return

    try:
        # 2. Initialize the client
        client = genai.Client()

        # 3. Configure the model request
        config = types.GenerateContentConfig(
            system_instruction="You are a senior data analyst.",
        )

        print(f"--- Sending Prompt to Model ---\nPrompt: {user_prompt}\n")

        # 4. Call the model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=config,
        )

        # 5. Print the generated content
        print("--- Model Response (Python Code) ---")
        print(response.text)

    except Exception as e:
        print(f"\nAn error occurred during API call: {e}")
        print("Ensure your API key is correct and the Google GenAI SDK is installed (`pip install google-genai`).")
