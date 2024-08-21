import requests

# Replace with your actual ngrok endpoint
api_url = "https://b462-34-75-22-103.ngrok-free.app/predict"

def get_response(instruction):
    try:
        # JSON body containing the instruction
        payload = {
            "instruction": instruction
        }

        # Send POST request to Flask API
        response = requests.post(api_url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            return data.get('response', 'No response found.')
        else:
            return f"Error: Received status code {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

if __name__ == "__main__":
    while True:
        # Take input from the user
        user_input = input("Enter your instruction (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        
        # Get response from the Flask API
        response = get_response(user_input)
        print("Chatbot response:", response)
