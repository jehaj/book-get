"""This module is used to create a book from already downloaded txt files."""

import book

filepaths = []
for i in range(0, 64+1):
    CHAPTER_NUMBER = str(i).zfill(2)
    filepath = f"book2-chapters/chapter{CHAPTER_NUMBER}.txt"
    filepaths.append(filepath)

book.to_epub("for2-correct.epub", filepaths)
