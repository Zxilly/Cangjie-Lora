import json
import os
import re
import magic
from markdownify import markdownify as md


def convert_html_to_markdown(html_content):
    return md(html_content)


def get_all_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return sorted(html_files)


def split_content(content, max_length=100000):
    parts = []
    while len(content) > max_length:
        split_index = content.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(content[:split_index])
        content = content[split_index:].lstrip()
    parts.append(content)
    return parts


def get_all_code_files(directory) -> list[str]:
    code_files = []
    m = magic.Magic(mime=True)

    for root, dirs, files in os.walk(directory):
        # 移除 .git 文件夹
        i = 0
        while i < len(dirs):
            if dirs[i] == '.git':
                del dirs[i]
            else:
                i += 1

        for file in files:
            name = os.path.join(root, file)
            r = m.from_file(name)
            if r.startswith('text/'):
                if name.endswith('.json'):
                    continue
                if name.endswith('.yaml'):
                    continue
                if name.find('cjcov') != -1:
                    continue
                if name.endswith('.html'):
                    continue
                if name.endswith('.lock'):
                    continue

                code_files.append(name)
                print(name, r)
    return code_files


m = re.compile(r'\n{3,}')

# 去除无意义的连续换行
def clean(s: str) -> str:
    return re.sub(m, '\n\n', s)

def main():
    docs_dir = 'docs'
    output_file = 'cangjie.json'
    
    html_files = get_all_html_files(docs_dir)

    data = []

    # code_files = get_all_code_files('code')
    # for code_file in code_files:
    #     print(f"Processing {code_file}...")
        
    #     try:
    #         with open(code_file, 'r', encoding='utf-8') as infile:
    #             code_content = infile.read()
    #     except UnicodeDecodeError:
    #         print(f"Error reading {code_file}, skipping...")
    #         continue
        
    #     relative_path = os.path.relpath(code_file, 'code')
    #     markdown_content = f"# {relative_path}\n\n```\n{code_content}\n```"
        
    #     content_parts = split_content(markdown_content)
        
    #     for part in content_parts:
    #         part_data = {
    #             "text": part,
    #         }
    #         data.append(part_data)
    
    for html_file in html_files:
        print(f"Processing {html_file}...")
        
        with open(html_file, 'r', encoding='utf-8') as infile:
            html_content = infile.read()

        # 移除 <main></main> 以外的内容
        html_content = re.search(r'<main>(.*)</main>', html_content, re.S).group(1)
        
        markdown_content = convert_html_to_markdown(html_content)
        markdown_content = clean(markdown_content)
        
        relative_path = os.path.relpath(html_file, docs_dir)\
        
        relative_path = relative_path.replace('.html', '')
        relative_path = relative_path.replace('\\', '-')
        relative_path = relative_path.replace('/', '-')
        
        with open(f'./md/{relative_path}.md', 'w', encoding='utf-8') as outfile:
            outfile.write(markdown_content)

    # with open(output_file, 'w', encoding='utf-8') as outfile:
    #     json.dump(data, outfile, ensure_ascii=False, indent=2)
    
    print(f"All HTML files have been converted and combined into {output_file}")

if __name__ == "__main__":
    main()