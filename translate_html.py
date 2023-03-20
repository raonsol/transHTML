import os
import openai
import shutil
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)


def translate_html(content: str):
    try:
        msg = [
            {
                "role": "system",
                "content": "You are a translator, that translate content inside HTML code from Korean to English. You must translate only content inside, not the code area such as tags or class names.",
            },  # 챗봇의 정체성 설정
            {"role": "user", "content": content},
        ]

        translated_content = (
            openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=msg)
            .choices[0]
            .message.content
        )
    except openai.error.OpenAIError as e:
        print("OpenAI Error: ", e)

    return translated_content


def process_html(src_path, dest_path):
    with open(src_path, "r", encoding="utf-8") as f:
        html_str = f.read()
    if len(html_str) > 4000:  # HTML 크기가 너무 크면 split
        html_parts = [html_str[i : i + 4000] for i in range(0, len(html_str), 4000)]
        translated_parts = [translate_html(part) for part in html_parts]
        translated_html_str = "".join(translated_parts)
    else:
        translated_html_str = translate_html(html_str)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(translated_html_str)


def get_file_list(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_list.append(os.path.join(root, file))

    return file_list


def process_dir(src_dir, dest_dir):
    file_count = 0

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    src_path_list = get_file_list(src_dir)

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        MofNCompleteColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        taskbar = progress.add_task("[blue]Starting...", total=len(src_path_list))
        for src_file_path in src_path_list:
            file_count += 1
            dest_file_path=src_file_path.replace(src_dir, dest_dir, 1)
            dest_file_dir = os.path.dirname(dest_file_path)
            if not os.path.exists(dest_file_dir):
                os.makedirs(dest_file_dir)

            src_file_name = os.path.basename(src_file_path)
            if src_file_name.endswith(".html"):
                try:
                    progress.update(
                        taskbar, description=f"[blue]Translating {src_file_name}"
                    )
                    process_html(src_file_path, dest_file_path)
                    progress.update(taskbar, advance=1)
                except ValueError as e:
                    print(e)

            else:
                progress.update(taskbar, description=f"[green]Copying {src_file_name}")
                shutil.copyfile(src_file_path, dest_file_path)
                progress.update(taskbar, advance=1)


openai.api_key = "YOUR_API_KEY"
SRC_DIR = "C:\\test"
DEST_DIR = "C:\\test_dest"
process_dir(SRC_DIR, DEST_DIR)
