import os
import json

from mongoengine.errors import NotUniqueError

from models import Author, Quote


current_dir = os.path.dirname(os.path.abspath(__file__))
file_path_authors = os.path.join(current_dir, "authors.json")
file_path_qoutes = os.path.join(current_dir, "qoutes.json")

if __name__ == "__main__":
    with open(file_path_authors, encoding="utf-8") as fd:
        data = json.load(fd)
        for el in data:
            try:
                author = Author(
                    fullname=el.get("fullname"),
                    born_date=el.get("born_date"),
                    born_location=el.get("born_location"),
                    description=el.get("description"),
                )
                author.save()
            except NotUniqueError:
                print(f"Автор вже існує {el.get('fullname')}")

    with open(file_path_qoutes, encoding="utf-8") as fd:
        data = json.load(fd)
        for el in data:
            author, *_ = Author.objects(fullname=el.get("author"))
            quote = Quote(quote=el.get("quote"), tags=el.get("tags"), author=author)
            quote.save()
