import json
import os
import re


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


m = re.compile(r'\n{3,}')

# 去除无意义的连续换行
def main():
    output_file = 'cangjie-code.json'

    data = []

    code_files = get_all_code_files('code')
    for code_file in code_files:
        print(f"Processing {code_file}...")
        
        try:
            with open(code_file, 'r', encoding='utf-8') as infile:
                code_content = infile.read()
        except UnicodeDecodeError:
            print(f"Error reading {code_file}, skipping...")
            continue
        
        relative_path = os.path.relpath(code_file, 'code')
        markdown_content = f"# 文件路径：{relative_path}\n\n```cangjie\n{code_content}\n```"
        data.append({
            "input": f"请给我提供{relative_path}的内容。",
            "output": markdown_content
        })

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(code_files)} code files. Output saved to {output_file}")

if __name__ == "__main__":
    main()