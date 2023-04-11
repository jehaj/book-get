"""This module turns a web-book into an epub book."""

import os
import random
import time
from pathlib import Path

import requests
from lxml import html, etree
from readability import Document


def get_chapters(for_url, html_parser) -> list[str]:
    """Read Table of Contents and get links to every chapter"""
    if ".com" in for_url:
        webpage = requests.get(for_url, verify=False, timeout=30)
        text = webpage.text
    else:
        with open(for_url, encoding="utf-8") as file:
            text = file.read()
    overview_tree = html.fromstring(text, parser=html_parser)
    chapters = len(overview_tree.xpath(
        "/html/body/div[5]/div/div/div/div[1]/div/div[2]/div/div[2]/div[5]/div[2]/table/tbody")[0])
    print(chapters)
    chapter_xpath = "/html/body/div[5]/div/div/div/div[1]/div/div[2]/div/div[2]/div[5]/div[2]/table/tbody/tr[x]/td[1]/a"
    chapters_url = []
    for j in range(1, chapters+1):
        elem = overview_tree.xpath(chapter_xpath.replace("x", str(j)))
        if elem[0].tag == "a":
            chapters_url.append(
                "https://web.archive.org" + elem[0].get("href"))
    return chapters_url


def url_to_txt(chapters, folder_name="out", should_sleep=True) -> list[str]:
    """Take a list of URLs write the HTML response to file,
       Also writes the readability HTML to another file.
       They will be in <folder_name>/chapter_html and
       <folder_name>/chapter_readability respectively."""
    filepaths = []
    # for each chapter get the text
    for c_url in chapters:
        cur_webpage = requests.get(c_url, timeout=30)
        title = c_url[c_url.rfind("/"):]
        with open(folder_name + "/chapter-html" + title + ".html", "w", encoding="utf-8") as file:
            file.write(cur_webpage.text)
        doc = Document(cur_webpage.text)
        txt_path = folder_name + "/chapter-readability" + title + ".html"
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write(doc.summary())
        filepaths.append(txt_path)
        if should_sleep:
            time.sleep(random.randint(40, 70)/10)
    return filepaths


def to_epub(book_path: str, filenames: list[str]):
    cmd_string = f"pandoc -o {book_path} .\\booktitle.txt " + \
        " ".join(filenames)
    os.system(cmd_string)


def main(html_parser):
    print("Doing all")
    print("  1. Getting chapter URLs.")
    chapters = get_chapters("in/overview-old.htm", html_parser)
    print("     Done with getting chapter URLs.")

    print("  2. Chapter URL to txt file.")
    filepaths = url_to_txt(chapters, "out")
    print("     Done with all chapters.")

    print("  3. Compiling to book.")
    to_epub("Beware of Chicken - Volume 1".replace(" ", "_"), filepaths)
    print("     Done with compilation.")


if __name__ == "__main__":
    HTML_PARSER = etree.HTMLParser()
    # main(HTML_PARSER)

    dirpath = "out/chapter-readability"
    files = sorted(Path(dirpath).iterdir(), key=os.path.getmtime)
    files = list(map(str, files))
    print(files)
    to_epub("out/volume1.pdf", files)
