import json
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

def get_all_code_files(directory) -> list[str]:
    code_files = []

    for root, dirs, files in os.walk(directory):
        # 移除 .git 文件夹
        i = 0
        while i < len(dirs):
            if dirs[i] == '.git':
                del dirs[i]
            else:
                i += 1

        for file in files:
            name = str(os.path.join(root, file))
            if file.endswith('.cj'):
                code_files.append(name)

    return code_files

splitter = RecursiveCharacterTextSplitter.from_language(language=Language.SWIFT, chunk_size=1950, chunk_overlap=512)

if __name__ == '__main__':
    markdown_dir = "md"
    markdown_files = []
    for f in os.listdir(markdown_dir):
        if f.endswith('.md'):
            markdown_files.append(os.path.join(markdown_dir, f))

    datas = []
    for file_path in markdown_files:
        print(f"Processing {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        data = {
            "text": f"{content}"
        }
        datas.append(data)

        print(f"Processed {file_path}.")

    code_files = get_all_code_files('code')
    for code_file in code_files:
        print(f"Processing {code_file}...")

        try:
            with open(code_file, 'r', encoding='utf-8') as infile:
                code_content = infile.read()
        except UnicodeDecodeError:
            print(f"Error reading {code_file}, skipping...")
            continue

        splits = splitter.split_text(code_content)
        for split_content in splits:
            datas.append({
                "text": split_content
            })

        print(f"Processed {len(splits)} splits for {code_file}.")

    with open("manual.json", 'w', encoding='utf-8') as file:
        json.dump(datas, file, ensure_ascii=False, indent=2)

