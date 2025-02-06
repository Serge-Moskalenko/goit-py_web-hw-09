import pickle

import redis
from redis_lru import RedisLRU

from models import Author, Quote

class CustomRedisLRU(RedisLRU):

    def _decorator_key(
        self,
        *args,
    ):
        return "_".join(str(a) for a in args)


client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = CustomRedisLRU(client)


@cache
def find_by_tag(tag):

    cache.get(tag)
    
    quotes = Quote.objects(tags__iregex=tag)
    return [q.quote for q in quotes]

def find_by_tags(tags):

    key = f"tags:{','.join(tags)}"
    cache.get(key)
 
    quotes_qs = Quote.objects(tags__in=tags)

    result_list = [q.quote for q in quotes_qs]

    cache.set(key, pickle.dumps(result_list))
    return result_list


@cache
def find_by_author(author):

    cache.get(author)

    authors = Author.objects(fullname__iregex=author)
    result = {}
    for a in authors:
        quotes = Quote.objects(author=a)
        result[a.fullname] = [q.quote for q in quotes]
    return result


def main():
    while True:
        user_input = input(
            "Enter command (tag:<tag>, name:<author>, tags:<list>, exit): "
        )
        user_input = user_input.strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if user_input.startswith("name:"):
            name = user_input[len("name:") :].strip()
            quotes = find_by_author(name)
            for q in quotes:
                print(q.encode("utf-8", errors="ignore").decode("utf-8"))

        elif user_input.startswith("tag:"):
            tag_name = user_input[len("tag:") :].strip()
            quotes = find_by_tag(tag_name)
            for q in quotes:
                print(q.encode("utf-8", errors="ignore").decode("utf-8"))

        elif user_input.startswith("tags:"):
            tags_str = user_input[len("tags:") :].strip()
            tags_list = [t.strip() for t in tags_str.split(",")]
            quotes = find_by_tags(tags_list)
            for q in quotes:
                print(q.encode("utf-8", errors="ignore").decode("utf-8"))
        else:
            print("Unknown command, try again.")

if __name__ == "__main__":
    main()
