import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import AzureOpenAI
from pydantic import BaseModel, RootModel

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

if not endpoint:
    raise ValueError("Please set the AZURE_OPENAI_ENDPOINT environment variable")
if not api_key:
    raise ValueError("Please set the AZURE_OPENAI_API_KEY environment variable")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-08-01-preview"
)


def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


class AlphcaItem(BaseModel):
    input: str
    output: str


class Alphca(BaseModel):
    conversation: list[AlphcaItem]

class AlphcaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.dict()
        return super().default(obj)


def generate_alpaca_dialogue(content):
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": """You are an AI assistant tasked with converting documentation of standard library for a new programming language 仓颉 into a dialogue-based dataset suitable for supervised fine-tuning (SFT) of large language models. Your goal is to create natural, informative conversations that cover all the important information from the original Markdown document.
1. Read the provided Markdown document thoroughly.
2. Identify the main topics, subtopics, and key information points in the document.
3. Create a series of dialogues between a human and an AI assistant that cover all the identified information.
4. Ensure that the dialogues are natural, engaging, and diverse in structure.
5. Include a mix of question types: open-ended, specific, clarification requests, and follow-ups.
6. Incorporate relevant examples, explanations, and elaborations in the AI's responses.
7. Use appropriate Markdown formatting in the AI's responses when necessary (e.g., code blocks, lists, emphasis).
8. Maintain a consistent tone and level of expertise throughout the dialogues.
9. Ensure that each dialogue exchange is self-contained and coherent.
10. Always prioritize clarity, correctness, and completeness of information.
11. Use Chinese for the dialogue.
12. The document is for programming language 仓颉."""},
            {"role": "user", "content": f"{content}"}
        ],
        response_format=Alphca
    )
    return response.choices[0].message.parsed.conversation


def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2, cls=AlphcaEncoder)


def process_file(file_path, output_dir):
    print(f"Processing {file_path}...")

    content = read_markdown_file(file_path)
    dialogue = generate_alpaca_dialogue(content)

    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.json")
    save_json(dialogue, output_file)

    print(f"Processed {file_path}. Output saved to {output_file}")

    return output_file


def merge_json_files(json_files, output_file):
    merged_data = []
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            merged_data.extend(data)

    save_json(merged_data, output_file)


def main(markdown_dir, output_dir, final_output):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    markdown_files = [os.path.join(markdown_dir, f) for f in os.listdir(markdown_dir) if f.endswith('.md')]

    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(process_file, file, output_dir): file for file in markdown_files}
        json_files = []
        for future in as_completed(future_to_file):
            json_files.append(future.result())

    merge_json_files(json_files, final_output)
    print(f"Processing complete. Final output saved to {final_output}")


if __name__ == "__main__":
    markdown_dir = "tmd"
    output_dir = "dataset"
    final_output = "final_alpaca_dataset.json"
    main(markdown_dir, output_dir, final_output)
