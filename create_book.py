"""This module is used to create a book from already downloaded txt files."""

import book

filepaths = []
for i in range(0, 19+1):
    CHAPTER_NUMBER = str(i).zfill(2)
    filepath = f"book3-chapters/chapter{CHAPTER_NUMBER}.txt"
    filepaths.append(filepath)

book.to_epub("for3-correct.epub", filepaths)
