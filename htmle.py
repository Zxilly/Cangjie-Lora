import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import markdownify
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language


def convert_html_to_markdown(html_content):
    return markdownify.markdownify(html_content)


m = re.compile(r'\n{3,}')


def clean(s: str) -> str:
    return re.sub(m, '\n\n', s)


mds = RecursiveCharacterTextSplitter.get_separators_for_language(Language.MARKDOWN)
zhs = [
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200b",  # Zero-width space
    "\uff0c",  # Fullwidth comma
    "\u3001",  # Ideographic comma
    "\uff0e",  # Fullwidth full stop
    "\u3002",  # Ideographic full stop
    "",
]
seps = []
seps.extend(mds)
seps.extend(zhs)

splitter = RecursiveCharacterTextSplitter(chunk_size=1950, chunk_overlap=512, length_function=len, separators=seps)


def process_html_file(html_file, docs_dir):
    try:
        relative_path = os.path.relpath(html_file, docs_dir)

        if relative_path.endswith('print.html') or relative_path.endswith('404.html'):
            print(f"Skipping {html_file}...")
            return

        with open(html_file, 'r', encoding='utf-8') as infile:
            html_content = infile.read()

        relative_path = relative_path.replace('.html', '')

        main_content = re.search(r'<main>(.*)</main>', html_content, re.S).group(1)
        title_content = re.search(r'<title>(.*)</title>', html_content, re.S).group(1)
        markdown_content = convert_html_to_markdown(main_content)
        markdown_content = clean(markdown_content)

        ar = relative_path

        def add_title(m):
            return f"# {title_content}\n\n文件路径：{ar}\n\n{m}"

        relative_path = relative_path.replace('\\', '-').replace('/', '-')

        splits = splitter.split_text(markdown_content)

        for i, split_content in enumerate(splits):
            split_filename = f'./md/{relative_path}-part{i + 1}.md'
            with open(split_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(add_title(split_content))

        print(f"Wrote {len(splits)} files for {relative_path}")

    except Exception as e:
        print(f"Error processing {html_file}: {e}")


def main(html_files, docs_dir, max_workers=24):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_html_file = {executor.submit(process_html_file, html_file, docs_dir): html_file for html_file in
                               html_files}

        for future in as_completed(future_to_html_file):
            html_file = future_to_html_file[future]
            try:
                future.result()  # Raises an exception if the thread failed
            except Exception as exc:
                print(f"Error occurred during processing {html_file}: {exc}")

    print("All HTML files have been converted.")


def get_all_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return sorted(html_files)


if __name__ == '__main__':
    docs_dir = 'docs/cjnative'
    html_files = get_all_html_files(docs_dir)
    main(html_files, docs_dir)
