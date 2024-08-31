import requests

class JudicialChatbot:
    def __init__(self):
        self.api_url = "https://04c2-34-19-49-181.ngrok-free.app/predict"

    def generate_response(self, input_text):
        response = requests.post(self.api_url, json={"instruction": input_text})
        if response.status_code == 200:
            print(response.json())
            return response.json().get('response', "No response received.")
        else:
            return "Sorry, I couldn't generate a response at this time."

chatbot = JudicialChatbot()
