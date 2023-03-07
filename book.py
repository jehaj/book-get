"""This module turns a web-book into an epub book."""

import os
import random
import shutil
import time
from pathlib import Path

import requests
from lxml import etree
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from readability import Document

disable_warnings(InsecureRequestWarning)


def get_chapters(html_parser) -> list[str]:
    for_url = "https://www.forgottenconqueror.com/book-three/"
    webpage = requests.get(for_url, verify=False)
    book_tree = etree.fromstring(webpage.text, parser=html_parser)
    book_xpath = "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div/p[z]/a[x]"
    broken_chapters = len(book_tree.xpath(
        "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div")[0])
    chapters_url = []
    for j in range(1, broken_chapters+1):
        chapters = len(book_tree.xpath(
            "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div/p[z]".replace('z', str(j)))[0])
        for i in range(1, chapters+1):
            elem = book_tree.xpath(book_xpath.replace(
                'x', str(i)).replace('z', str(j)))
            if len(elem) > 0 and elem[0].tag == "a":
                chapters_url.append(elem[0].get("href"))
    return chapters_url


def url_to_txt(html_parser, chapters, folder_name="chapters", should_sleep=True) -> list[str]:
    filepaths = []
    # for each chapter get the text
    if Path.exists(Path(folder_name)):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)
    for C_URL in chapters:
        cur_webpage = requests.get(C_URL, verify=False)
        doc = Document(cur_webpage)
        cur_page = etree.fromstring(doc.summary(), parser=html_parser())
        # cur_page = etree.fromstring(cur_webpage.text, parser=html_parser)
        # cur_page = etree.parse(C_URL, parser=html_parser)

        text_holder_xpath = "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div"
        text_holder = cur_page.xpath(text_holder_xpath)[0]

        text_fields = len(text_holder)
        text_field_xpath = "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div/p[x]"
        chapter_number = str(chapters.index(C_URL)).zfill(2)
        filepath = f"{folder_name}/chapter{chapter_number}.txt"
        filepaths.append(filepath)
        with open(filepath, 'w', encoding="utf-8") as f:
            title_field = cur_page.xpath(
                "/html/body/div[1]/div/div[1]/main/article/header/h1")[0]
            title = title_field.text
            f.write(f"# {title}")
            f.write("\n\n")
            for i in range(1, text_fields):
                text_field = cur_page.xpath(
                    text_field_xpath.replace('x', str(i)))[0]
                text = text_field.text
                if text is not None:
                    f.write(text)
                    if i < text_fields-1:
                        f.write("\n\n")
                else:
                    if text_field[0].tag == "em":
                        if text_field[0].text is not None and text_field[0].tail is not None:
                            f.write(f"*{text_field[0].text.strip()}* ")
                            f.write(text_field[0].tail.strip('\n '))
                            f.write("\n\n")
        if should_sleep:
            time.sleep(random.randint(40, 70)/10)
    return filepaths


def to_epub(book_path: str, filenames: list[str]):
    cmd_string = f"pandoc -o {book_path} .\\book-title.txt " + \
        " ".join(filenames)
    os.system(cmd_string)


def main(html_parser):
    print("Doing all")
    print("  1. Getting chapter URLs.")
    chapters = get_chapters(html_parser)
    print("     Done with getting chapter URLs.")

    print("  2. Chapter URL to txt file.")
    filepaths = url_to_txt(html_parser, chapters, "book3-chapters")
    print("     Done with all chapters.")

    print("  3. Compiling to book.")
    to_epub("Forgotten_Conqueror_-_Book_3.epub", filepaths)
    print("     Done with compilation.")


if __name__ == "__main__":
    HTML_PARSER = etree.HTMLParser()
    main(HTML_PARSER)
    # url_to_txt(HTML_PARSER, ["b1c1.htm"], False)
