import json
import os

if __name__ == '__main__':
    # 遍历 md 目录下的所有 md 文件
    markdown_dir = "md"
    markdown_files = []
    for f in os.listdir(markdown_dir):
        if f.endswith('.md'):
            markdown_files.append(os.path.join(markdown_dir, f))

    dialogues = []
    for file_path in markdown_files:
        print(f"Processing {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        filename = os.path.splitext(os.path.basename(file_path))[0]
        filename = filename.replace('-', '/')
        dialogue = {
            "input": f"请给我提供{filename}的内容。",
            "output": f"{content}"
        }
        dialogues.append(dialogue)

        print(f"Processed {file_path}.")

    with open("gpt4o.json", 'r', encoding='utf-8') as file:
        final_alpaca_dataset = json.load(file)

    # dialogues.extend(final_alpaca_dataset)

    # 保存对话到 json 文件
    with open("manual.json", 'w', encoding='utf-8') as file:
        json.dump(dialogues, file, ensure_ascii=False, indent=2)

