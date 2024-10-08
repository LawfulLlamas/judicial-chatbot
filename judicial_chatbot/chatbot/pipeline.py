import dspy
from rank_bm25 import BM25Okapi
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate
from textparsing import parse_data
from unsloth import FastLanguageModel
import torch

class ChatbotSignature(dspy.Signature):
    """Answer questions related to the Department of Justice website."""
    question = dspy.InputField(desc="User's question about the website")
    answer = dspy.OutputField(desc="Answer to the user's question")

# Define a custom LLM class for Unsloth's Fast Llama
class UnslothLlama(dspy.LM):
    def __init__(self, model_name='unsloth/Meta-Llama-3.1-8B-bnb-4bit'):
        super().__init__()
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name,
            max_seq_len=2048,
            dtype=Nonek,
            load_in_4bit=True,
        )

    def basic_request(self, prompt, **kwargs):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=100, **kwargs)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

# Use the Unsloth Fast Llama
llama = UnslothLlama()

# The rest of your code remains the same
class LocalRetriever(dspy.Module):
    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset
        self.index = self.build_index()

    def build_index(self):
        documents = [f"{example.webpage}\n{example.link}\n{example.text}" for example in self.dataset]
        tokenized_corpus = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        return documents

    def forward(self, query):
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
        retrieved_docs = [self.dataset[i].text for i in top_n]
        return dspy.Prediction(passages=retrieved_docs)

# Configure DSPy to use our Unsloth LLM and local retriever
dataset = parse_data('chatbot/train.txt')
local_retriever = LocalRetriever(dataset)
dspy.settings.configure(lm=llama, rm=local_retriever)

class DOJChatbot(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(ChatbotSignature)

    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)

# Define a simple evaluation metric
def validate_answer(example, pred):
    return len(pred.answer.strip()) > 0

# Initialize the evaluator
evaluate = Evaluate(devset=dataset[:10], metric=validate_answer, num_threads=1, display_progress=True)

# Initialize the chatbot
chatbot = DOJChatbot()

# Initialize the teleprompter
teleprompter = BootstrapFewShot(metric=validate_answer)

# Compile the chatbot
compiled_rag = teleprompter.compile(chatbot, trainset=dataset[:50])

# Evaluate the chatbot
evaluation_result = evaluate(compiled_rag)
print(evaluation_result)

# Example usage
example_question = "What is the vision of the Department of Justice?"
result = compiled_rag(question=example_question)
print(f"Question: {example_question}")
print(f"Answer: {result.answer}")