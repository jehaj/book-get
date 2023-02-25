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

disable_warnings(InsecureRequestWarning)


def get_chapters(html_parser) -> list[str]:
    FOR_URL = "https://www.forgottenconqueror.com/book-two/"
    # FOR_PATH = "Book One - Forgotten Conqueror.htm"
    WEBPAGE = requests.get(FOR_URL, verify=False)
    BOOKTREE = etree.fromstring(WEBPAGE.text, parser=html_parser)
    # frontpage = etree.parse(FOR_PATH, parser=HTML_PARSER)
    BOOK_XPATH = "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div/p[1]/a[x]"
    CHAPTERS = len(BOOKTREE.xpath(
        "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div/p[1]")[0])
    chapters = []

    for i in range(1, CHAPTERS+1):
        ELEM = BOOKTREE.xpath(BOOK_XPATH.replace('x', str(i)))
        if len(ELEM) > 0 and ELEM[0].tag == "a":
            chapters.append(ELEM[0].get("href"))
    return chapters


def url_to_txt(html_parser, chapters, foldername="chapters", should_sleep=True) -> list[str]:
    filepaths = []
    # for each chapter get the text
    if Path.exists(Path(foldername)):
        shutil.rmtree(foldername)
    os.mkdir(foldername)
    for C_URL in chapters:
        CUR_WEBPAGE = requests.get(C_URL, verify=False)
        CUR_PAGE = etree.fromstring(CUR_WEBPAGE.text, parser=html_parser)
        # CUR_PAGE = etree.parse(C_URL, parser=html_parser)

        TEXT_HOLDER_XPATH = "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div"
        TEXT_HOLDER = CUR_PAGE.xpath(TEXT_HOLDER_XPATH)[0]

        TEXT_FIELDS = len(TEXT_HOLDER)
        TEXT_FIELD_XPATH = "/html/body/div[1]/div/div[1]/main/article/div/div/div/div/div/p[x]"
        CHAPTER_NUMBER = str(chapters.index(C_URL)).zfill(2)
        FILEPATH = f"{foldername}/chapter{CHAPTER_NUMBER}.txt"
        filepaths.append(FILEPATH)
        with open(FILEPATH, 'w', encoding="utf-8") as f:
            TITLE_FIELD = CUR_PAGE.xpath(
                "/html/body/div[1]/div/div[1]/main/article/header/h1")[0]
            TITLE = TITLE_FIELD.text
            f.write(f"# {TITLE}")
            f.write("\n\n")
            for i in range(1, TEXT_FIELDS):
                TEXT_FIELD = CUR_PAGE.xpath(
                    TEXT_FIELD_XPATH.replace('x', str(i)))[0]
                TEXT = TEXT_FIELD.text
                if TEXT is not None:
                    f.write(TEXT)
                    if i < TEXT_FIELDS-1:
                        f.write("\n\n")
                else:
                    if TEXT_FIELD[0].tag == "em":
                        if TEXT_FIELD[0].text is not None and TEXT_FIELD[0].tail is not None:
                            f.write(f"*{TEXT_FIELD[0].text.strip()}* ")
                            f.write(TEXT_FIELD[0].tail.strip('\n '))
                            f.write("\n\n")
        if should_sleep:
            time.sleep(random.randint(40, 70)/10)
    return filepaths


def to_epub(bookpath: str, filenames: list[str]):
    CMD_STRING = f"pandoc -o {bookpath} .\\booktitle.txt " + \
        " ".join(filenames)
    os.system(CMD_STRING)


def main(html_parser):
    print("Doing all")
    print("  1. Getting chapter URLs.")
    chapters = get_chapters(html_parser)
    print("     Done with getting chapter URLs.")

    print("  2. Chapter URL to txt file.")
    filepaths = url_to_txt(html_parser, chapters, "book2-chapters")
    print("     Done with all chapters.")

    print("  3. Compiling to book.")
    to_epub("for2.epub", filepaths)
    print("     Done with compilation.")


if __name__ == "__main__":
    HTML_PARSER = etree.HTMLParser()
    main(HTML_PARSER)
    # url_to_txt(HTML_PARSER, ["b1c1.htm"], False)
