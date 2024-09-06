import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import AzureOpenAI
from pydantic import BaseModel
from tqdm import tqdm

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
             "content": """你是一位专门研究新编程语言"仓颉"的专家。你的任务是将一份关于仓颉语言的 Markdown 文档转换成 Alphca 格式的对话集合，用于训练大型语言模型。请严格遵循以下步骤，并确保所有输出均使用简体中文：
1. 仔细阅读整个 Markdown 文档，理解其结构和内容。
2. 将文档分割成逻辑单元。每个单元可以是一个章节、一个概念解释、一段代码示例或其他独立的信息块。
3. 创建一个主要对话，其中必须包含完整的逻辑单元。这个对话应该是这样的：
   - 人类问一个总体性的问题
   - AI 助手的回答必须包含整个分割后的逻辑单元文档内容，保持原有的结构和详细程度。这份完整文档是必需的，不可省略。
4. 在主要对话之后，基于其中的信息创建多个补充对话。每个补充对话应该：
   - 聚焦于文档中的特定主题或概念
   - 包含更具体的问题和更详细的解答
   - 可能包含假设的场景或实际应用案例
5. 对于包含仓颉语言代码的部分：
   - 创建专门的对话来讨论和解释代码
   - 在对话中提供代码的具体应用场景和可能的变化
   - 对于 Markdown 代码块，永远使用 cangjie 语言标识符
6. 确保生成的对话覆盖文档中的所有重要信息，包括：
   - 仓颉语言的基本概念和原理
   - 语法规则和特性
   - 代码结构和组织方式
   - 常见用例和最佳实践
   - 与其他编程语言的比较（如果有）
7. 使用多样化的对话类型，如：
   - 概念解释对话
   - 代码分析对话
   - 比较讨论
   - 问题解决对话
   - 项目规划对话
8. 在对话中加入一些拟人化的元素，如：
   - 表达好奇或困惑
   - 请求进一步解释或举例
   - 提出假设性问题
9. 确保对话的语言风格专业且易懂，适合作为教学材料。
10. 文档是关于编程语言仓颉的，文档中的代码也全部是仓颉语言的代码。
11. 返回一个对象，包含一个 conversation 属性，其值是一个包含多个对话项的列表。每个对话项包含一个 input 属性和一个 output 属性（对话内容）。对话应该有多组。""",},
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

    markdown_files = []
    for f in os.listdir(markdown_dir):
        if f.endswith('.md'):
            output = os.path.join(output_dir, f"{os.path.splitext(f)[0]}.json")
            if os.path.exists(output):
                print(f"Skipping {f} as output file already exists...")
                continue

            markdown_files.append(os.path.join(markdown_dir, f))

    with ThreadPoolExecutor(max_workers=75) as executor:
        future_to_file = {executor.submit(process_file, file, output_dir): file for file in markdown_files}
        json_files = []
        for future in tqdm(as_completed(future_to_file), total=len(markdown_files), desc="Processing files"):
            json_files.append(future.result())

    merge_json_files(json_files, final_output)
    print(f"Processing complete. Final output saved to {final_output}")


if __name__ == "__main__":
    markdown_dir = "md"
    output_dir = "dataset"
    final_output = "gpt4o.json"
    main(markdown_dir, output_dir, final_output)
