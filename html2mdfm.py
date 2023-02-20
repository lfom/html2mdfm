import json
import os
import bs4
from bs4 import BeautifulSoup
from rich.console import Console
from rich.theme import Theme
from markdownify import markdownify

custom_theme = Theme({
    "line_style": "bright_yellow b",
    "warn": "bright_yellow",
    "att": "bright_red",
    "val": "bright_magenta",
    "sep": "bright_cyan",
    "var": "yellow",
})
console = Console(theme=custom_theme)


def get_current_time() -> str:
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


export_path = console.input(f"{get_current_time()} Enter the path to the export folder\n")
is_export_path_correct = os.path.exists(export_path)
if is_export_path_correct:
    filenames = []
    try:
        with open(f"{export_path}/index.html") as fp:
            soup = BeautifulSoup(fp, "html.parser")

            for li in soup.find_all("li"):
                li: bs4.element.Tag = li
                filenames.append(li.find("a").get("href"))

    except NotADirectoryError:
        console.print(f'{get_current_time()} [att][b]ERROR:[/b] The path must point to a folder, not a file')
        exit()
    except FileNotFoundError:
        console.print(f'{get_current_time()} [att][b]ERROR:[/b] Folder does not contain index.html file')
        exit()
    filedatas = []
    for index, filename in enumerate(filenames):
        try:
            with open(f"{export_path}/{filename}") as fp:
                soup = BeautifulSoup(fp, "html.parser")
                filedatas.append(
                    {"title": soup.find("title").text})

                dirty_data: dict[str, str] = json.loads(soup.find("body").get("data-notebook"))

                dirty_full_created_date = dirty_data["created_date"].split("T")
                created_date = dirty_full_created_date[0]
                created_time = dirty_full_created_date[1].split("-")[0]
                filedatas[index]["created"] = created_date + " " + created_time + "Z"

                dirty_full_updated_date = dirty_data["modified_date"].split("T")
                updated_date = dirty_full_updated_date[0]
                updated_time = dirty_full_updated_date[1].split("-")[0]
                filedatas[index]["updated"] = updated_date + " " + updated_time + "Z"

                filedatas[index]["completed?"] = "no"
                filedatas[index]["folder_name"] = dirty_data["name"]

                today = console.get_datetime()
                year = str(today.year)
                match = str(today.month)
                day = str(today.day)
                hour = str(today.hour)
                minute = str(today.minute)
                second = str(today.second)
                if len(match) == 1:
                    match = "0" + match
                if len(day) == 1:
                    day = "0" + day
                if len(hour) == 1:
                    hour = "0" + hour
                if len(minute) == 1:
                    minute = "0" + minute
                if len(second) == 1:
                    second = "0" + second
                filedatas[index]["due"] = f"{year}-{match}-{day} {hour}:{minute}:{second}Z"

                dirty_content = str(soup.html)
                filedatas[index]["content"] = markdownify(dirty_content)

        except NotADirectoryError:
            console.print(f'{get_current_time()} [att][b]ERROR:[/b] The path does not exist')
        except FileNotFoundError:
            console.print(f'{get_current_time()} [att][b]ERROR:[/b] The folder does not contain {filename}')
    save_path = console.input(f"{get_current_time()} Enter the path where to save the data\n")
    is_save_path_correct = os.path.exists(save_path)
    if is_save_path_correct:
        try:
            os.mkdir(f"{save_path}/export_data")
        except:
            pass
        for index, filedata in enumerate(filedatas):
            try:
                os.mkdir(f'{save_path}/export_data/{filedata["folder_name"]}')
            except:
                pass
            content = [f'---\n',
                       f'title: {filedata["title"]}\n',
                       f'created: {filedata["created"]}\n',
                       f'updated: {filedata["updated"]}\n',
                       f'completed?: {filedata["completed?"]}\n',
                       f'due: {filedata["due"]}\n',
                       f'---\n',
                       f'\n',
                       f'{filedata["content"]}\n']

            with open(f'{save_path}/export_data/{filedata["folder_name"]}/{filedata["title"]} {index}.md', "w") as f:
                f.writelines(content)
    else:
        console.print(f'{get_current_time()} [att][b]ERROR:[/b] The path does not exist')
else:
    console.print(f'{get_current_time()} [att][b]ERROR:[/b] The path does not exist')
