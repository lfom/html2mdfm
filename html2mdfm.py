#!/usr/bin/env python3
import os, json, bs4, re, argparse, shutil
from bs4 import BeautifulSoup
from rich.console import Console
from rich.theme import Theme
from markdownify import markdownify as md
from pathlib import Path
from datetime import datetime, timezone

SAVE_FOLDER = "export_data"

def set_console():
    custom_theme = Theme({
        "line_style": "bright_yellow b",
        "warn": "bright_yellow",
        "att": "bright_red",
        "val": "bright_magenta",
        "sep": "bright_cyan",
        "var": "yellow",
    })
    return Console(theme=custom_theme)

def get_time() -> str:
    today = console.get_datetime()
    hour = str(today.hour)
    minute = str(today.minute)
    second = str(today.second)
    if len(hour) == 1:
        hour = "0" + hour
    if len(minute) == 1:
        minute = "0" + minute
    if len(second) == 1:
        second = "0" + second
    return f'[b][[bright_green]{hour}:{minute}:{second}[/bright_green]][/b]'

def format_time(value) -> str:
    pattern = r'^(\+|\-)\d{4}$'
    tz = value[-5:]
    date = value
    if bool(re.match(pattern, tz)):
        date = value[:-2] + ":" + value[-2:]
    date_tz = datetime.fromisoformat(date)
    date = str(date_tz.astimezone(timezone.utc).isoformat())
    time = date.split("T")
    formatted_date = time[0]
    formatted_time = time[1].split('+')[0]
    return formatted_date + " " + formatted_time + "Z"

def replace_illegal(value, full = True) -> str:
    replaced = value
    if full:
        illegal_chars = '\/:*?"<>|'
        replacement = ' '
    else:
        illegal_chars = ':<>|'
        replacement = ''

    for c in illegal_chars:
        replaced = replaced.replace(c, replacement)
    return replaced

def filter_content(value, line_breaks):
    filters = ['<input type="checkbox"/><span>', '<input checked="true" type="checkbox"/><span>']
    checkbox_start = ['- [ ] ', '- [x] ']
    end = '</span>'
    filtered = value
    is_todo = False
    for c, start in enumerate(filters):
        start_index = filtered.find(start)
        while start_index > -1:
            end_index = filtered.find(end)
            if end_index > -1:
                end_index += 7
                subs = filtered[start_index : end_index]
                checkbox_item = subs.replace(start, checkbox_start[c])
                checkbox_item = checkbox_item.replace(end, '')
                filtered = filtered.replace(subs, checkbox_item)
                start_index = filtered.find(start)
                is_todo = True
            else:
                start_index = -1
    if line_breaks:
        filtered = filtered.replace('</div><div>', '</div><br/></div>')
    return (is_todo, filtered)

def find_attachments(value):
    starts = ['<img src="', '<a href="']
    ends = ['"/>', '">']
    attachments = []
    for c, start in enumerate(starts):
        subs = value
        start_index = subs.find(start)
        while start_index > -1:
            if start_index > 1:
                remove = subs[0 : start_index]
                subs = subs.replace(remove, '')
            else:
                subs = subs[1:]
            end_index = subs.find(ends[c])
            if end_index > -1:
                attachment_start = len(start)
                attachment = subs[attachment_start : end_index]
                end_index += len(ends[c])
                remove = subs[0 : end_index]
                attachments.append(attachment)
                subs = subs.replace(remove, '')
                start_index = subs.find(start)
            else:
                start_index = -1

    if value.find('style="-evernote-webclip:true"') > -1:
        attachments.append('**evernote-webclip**')
    return attachments

def move_attachments(attachments, source_dir, destination_dir):
    if attachments:
        for attachment in attachments:
            for f_name in os.listdir(source_dir):
                if attachment == str(f_name):
                    src = source_dir / attachment
                    dst = destination_dir / attachment
                    try:
                        shutil.copy(src, dst)
                    except:
                        console.print(f'{get_time()} [att][b]ERROR:[/b] Could not copy {attachment}')

# Instantiate the parser
parser = argparse.ArgumentParser(description='Convert Zoho Notebook HTML export to (Markdown + Front Matter) that can be imported to Joplin')

# Required argument
parser.add_argument('infolder', type=str, help='input folder that contains the exported HTML files')

# Optional positional argument
parser.add_argument('outfolder', type=str, nargs='?', help='output folder [if not provided, the current folder will be used]')

# Switch
parser.add_argument('--nolinebreaks', action='store_false', help='disable adding line breaks between divs (text lines may get merged into blocks)')

# Version
parser.add_argument('--version', action='version', version='1.0')

args = parser.parse_args()

export_path = Path(os.path.abspath(args.infolder))

if args.outfolder:
    save_path = Path(os.path.abspath(args.outfolder))
else:
    save_path = Path(os.path.abspath(os.getcwd()))
tmp_path = save_path / SAVE_FOLDER

line_breaks = args.nolinebreaks

console = set_console()

console.print(f'{get_time()} HTML files from {export_path}')
console.print(f'{get_time()} will be exported to {tmp_path}')
console.print(f'{get_time()} Line breaks between <div>\'s: {line_breaks}')
console.print(f'{get_time()} Do you want to continue (y/N)?')
if not input().lower().strip()[:1] == "y": exit()

if os.path.exists(export_path):
    filenames = []
    try:
        index_file = export_path / "index.html"
        with open(index_file) as fp:
            soup = BeautifulSoup(fp, "html.parser")

            for li in soup.find_all("li"):
                li: bs4.element.Tag = li
                filenames.append(li.find("a").get("href"))

    except NotADirectoryError:
        console.print(f'{get_time()} [att][b]ERROR:[/b] The path must point to a folder, not a file')
        exit()
    except FileNotFoundError:
        console.print(f'{get_time()} [att][b]ERROR:[/b] Folder does not contain index.html file')
        exit()
    filedatas = []
    for index, filename in enumerate(filenames):
        try:
            open_file = export_path / filename
            with open(open_file) as fp:
                soup = BeautifulSoup(fp, "html.parser")
                filedatas.append({"title": soup.find("title").text})

                json_data = soup.find("body").get("data-notebook")
                dirty_data: dict[str, str] = json.loads(json_data)

                filedatas[index]["folder_name"] = dirty_data["name"]

                filedatas[index]["created"] = format_time(dirty_data["created_date"])

                filedatas[index]["updated"] = format_time(dirty_data["modified_date"])

                dirty_content = str(soup.body)
                is_todo, filtered_content = filter_content(dirty_content, line_breaks)

                filedatas[index]["is_todo"] = is_todo
                if is_todo:
                    filedatas[index]["completed?"] = "no"
                    filedatas[index]["due"] = ''

                json_data = soup.find("body").get("data-remainder")
                if json_data and len(json_data) > 1:
                    json_data = json_data[1 : len(json_data)-1]
                    dirty_rem: dict[str, str] = json.loads(json_data)
                    if dirty_rem["type"].find("reminder") > -1:
                        filedatas[index]["is_todo"] = True
                        if dirty_rem["is-completed"]:
                            filedatas[index]["completed?"] = "yes" if dirty_rem["is-completed"] == 1 else "no"
                        if dirty_rem["ZReminderTime"]:
                            filedatas[index]["due"] = format_time(dirty_rem["ZReminderTime"])

                attachments = find_attachments(filtered_content)
                filedatas[index]["attachments"] = attachments

                filedatas[index]["content"] = md(
                    filtered_content, heading_style="ATX", keep_inline_images_in=['td']
                    )

                attachment_list = ''
                if attachments:
                    for attachment in attachments:
                        if attachment.startswith('http') or attachment.find('webclip') > -1:
                            attachment_list += attachment + '  \n'
                if attachment_list:
                    filedatas[index]["content"] += f'  \n{attachment_list}'

        except NotADirectoryError:
            console.print(f'{get_time()} [att][b]ERROR:[/b] The path does not exist')
        except FileNotFoundError:
            console.print(f'{get_time()} [att][b]ERROR:[/b] File {filename} not found')

    if os.path.exists(save_path):
        try:
            tmp_path.mkdir(exist_ok=True)
        except:
            console.print(f'{get_time()} [att][b]ERROR:[/b] Could not create {tmp_path}')
            exit()
        for index, filedata in enumerate(filedatas):
            save_folder = tmp_path / replace_illegal(filedata["folder_name"])
            try:
                save_folder.mkdir(exist_ok=True)
            except:
                console.print(f'{get_time()} [att][b]ERROR:[/b] Could not create {save_folder}')
                exit()

            content = [f'---\n',
                       f'title: {replace_illegal(filedata["title"], False)}\n',
                       f'created: {filedata["created"]}\n',
                       f'updated: {filedata["updated"]}\n']

            if filedata["is_todo"]:
                content += [f'completed?: {filedata["completed?"]}\n']
                if filedata["due"]:
                       content += [f'due: {filedata["due"]}\n']

            content += [f'---\n',
                       f'\n',
                       f'{filedata["content"]}\n']

            file_name = f'{replace_illegal(filedata["title"])} {index}.md'
            save_file = save_folder / file_name
            with open(save_file, "w") as f:
                f.writelines(content)

            move_attachments(filedata["attachments"], export_path, save_folder)

    else:
        console.print(f'{get_time()} [att][b]ERROR:[/b] The path does not exist')
else:
    console.print(f'{get_time()} [att][b]ERROR:[/b] The path does not exist')
