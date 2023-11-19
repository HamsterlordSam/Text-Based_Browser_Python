import re
from collections import deque
from os import access, getcwd, F_OK, mkdir
from sys import argv
from re import search
import requests
from bs4 import BeautifulSoup
from colorama import Fore, init


def check_url_format(url):
    if '.' not in url:
        print('Invalid URL')
        return 0
    elif url.startswith('https://'):
        return url
    else:
        return 'https://' + url


def prune_tab_name(url):
    pattern = r'(?<=\.).+$'
    suffix = '.' + search(pattern, url).group()
    prefix = 'https://'
    url = url.removesuffix(suffix)
    url = url.removeprefix(prefix)
    return url


def print_tab_file(path):
    if access(path, F_OK):
        with open(path, 'r', encoding='utf-8') as tab:
            for p in tab:
                print(p, end='')
        return 1
    return -1


tabs_list = []
history = deque()


if __name__ == '__main__':
    # check script parameters
    cur_dir = getcwd()
    if len(argv) == 2:
        folder = argv[1]
    else:
        exit(0)
    # check folder if it exists
    if not access(folder, F_OK):
        mkdir(cur_dir + "/" + folder)
    cur_dir = cur_dir + "/" + folder
    cur_page = ''
    # browser loop
    init()
    while (user_input := input()) != 'exit':
        if user_input == 'back':
            if len(history) > 1:
                page = history.pop()
                if cur_page != page:
                    tab_path = cur_dir + '/' + page
                    print_tab_file(tab_path)
                else:
                    page = history.pop()
                    tab_path = cur_dir + '/' + page
                    print_tab_file(tab_path)
            continue
        user_input = check_url_format(user_input)
        if user_input:
            r = requests.get(user_input)
            if r:
                print('Connected')
            else:
                print('Error connecting!')
                continue
            pruned_url = prune_tab_name(user_input)
            tab_path = cur_dir + '/' + pruned_url
            if pruned_url not in tabs_list:
                soup = BeautifulSoup(r.content, 'html.parser')
                with open(tab_path, 'w', encoding='utf-8') as file:
                    for tag in soup.find_all(re.compile(r'(^p)|(^a)|(^li)|(^h[1-6])')):
                        if tag.name != 'a' and len(tag.contents) == 1:
                            if tag.contents[0].name == 'a':
                                continue
                        elif tag.name == 'a':
                            print(Fore.BLUE, end='')
                            file.write(Fore.BLUE)
                        elif re.match(r'(^(\n*)|(\r*)|(\s*))$', tag.text) is not None:
                            continue
                        else:
                            print(Fore.RESET, end='')
                            file.write(Fore.RESET)
                        print(tag.text.strip("\n "))
                        file.write(tag.text.strip("\n ")+'\n')
                tabs_list.append(pruned_url)
                history.append(pruned_url)
                cur_page = pruned_url
            else:
                with open(tab_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        print(line)
        else:
            continue
