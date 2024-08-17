from transformers import AutoTokenizer, AutoModelForCausalLM

class JudicialChatbot:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/JudgeLM-33B-v1.0")
        self.model = AutoModelForCausalLM.from_pretrained("BAAI/JudgeLM-33B-v1.0")

    def generate_response(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=100)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

chatbot = JudicialChatbot()