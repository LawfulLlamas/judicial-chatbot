import dspy
import re

def parse_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into sections
    sections = re.split(r'\n(?=\[Webpage:)', content)

    dataset = []
    for section in sections:
        # Extract webpage info
        webpage_match = re.match(r'\[Webpage: (.*?) \((.*?)\)\]', section)
        if webpage_match:
            name = webpage_match.group(1)
            link = webpage_match.group(2)
            
            # Extract text (everything after the webpage info)
            text = section[webpage_match.end():].strip()
            
            # Create Example object
            example = dspy.Example(webpage=name, link=link, text=text).with_inputs('webpage', 'link')
            dataset.append(example)

    return dataset

# Use the function
dataset = parse_data('chatbot/train.txt')

# Print the first few examples to verify
for example in dataset[:3]:
    print(f"Webpage: {example.webpage}")
    print(f"Link: {example.link}")
    print(f"Text: {example.text}...")  # Print first 100 characters of text
    print("\n")