import requests

class JudicialChatbot:
    def __init__(self):
        self.api_url = "https://your-vercel-deployment-url.vercel.app/generate"

    def generate_response(self, input_text):
        response = requests.post(self.api_url, json={"text": input_text})
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Sorry, I couldn't generate a response at this time."

chatbot = JudicialChatbot()