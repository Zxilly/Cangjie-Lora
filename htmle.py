import os
import re
import markdownify
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


def convert_html_to_markdown(html_content):
    return markdownify.markdownify(html_content)

m = re.compile(r'\n{3,}')


def clean(s: str) -> str:
    return re.sub(m, '\n\n', s)


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

        def add_title(m):
            return f"# {title_content}\n\n{relative_path}\n\n{m}"

        relative_path = relative_path.replace('\\', '-').replace('/', '-')

        # Split the markdown content using MarkdownHeaderTextSplitter
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
            ],
            strip_headers=False
        )
        header_splits = header_splitter.split_text(markdown_content)

        # Further split each segment if it's over 50,000 characters
        char_splitter = RecursiveCharacterTextSplitter(chunk_size=50000, chunk_overlap=200)

        final_splits = []
        for split in header_splits:
            if len(split.page_content) > 50000:
                sub_splits = char_splitter.split_text(split.page_content)
                final_splits.extend(sub_splits)
            else:
                final_splits.append(split.page_content)

        for i, split_content in enumerate(final_splits):
            split_filename = f'./md/{relative_path}-part{i + 1}.md'
            with open(split_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(add_title(split_content))

        print(f"Wrote {len(final_splits)} files for {relative_path}")

    except Exception as e:
        print(f"Error processing {html_file}: {e}")

def main(html_files, docs_dir, max_workers=24):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_html_file = {executor.submit(process_html_file, html_file, docs_dir): html_file for html_file in html_files}

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