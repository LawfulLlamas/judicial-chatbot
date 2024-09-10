import dspy
from rank_bm25 import BM25Okapi
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate
from textparsing import parse_data

class ChatbotSignature(dspy.Signature):
    """Answer questions related to the Department of Justice website."""
    question = dspy.InputField(desc="User's question about the website")
    answer = dspy.OutputField(desc="Answer to the user's question")

# Use a local LLM. Adjust the model name as needed.
llama = dspy.LLM(model='llama-13b-chat')

# Create a custom BM25 retriever for our local dataset
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

# Configure DSPy to use our local LLM and retriever
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
    # For simplicity, we're just checking if the answer is not empty
    # In a real scenario, you'd want a more sophisticated validation
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
