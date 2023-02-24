from query import search, load_dict


def main():
    load_dict()
    x = -1
    while x != "":
        x = input ("Query (Enter \"\" to exit): ").strip()
        search(x)


if __name__ == '__main__':
    main()