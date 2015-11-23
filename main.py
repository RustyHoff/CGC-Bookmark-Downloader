#!/usr/bin/env python3
# coding=utf-8

import logging
import os

import requests
from bs4 import BeautifulSoup

# ***************************   Variables and Definitions    *************************** #
#  Log-in Data
USERNAME = "UserName"
PASSWORD = "P4$$w02D"

#  Folder to download courses to. Relative to this file
download_path = r"../CG_Cookie/"

# Logging info
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s -%(levelname)s - %(message)s')
logging.disable(logging.INFO)


def find_bookmarks():
    link_number = 0
    global bookmark_title
    global bookmark_href
    bookmark_title = []
    bookmark_href = []
    url = r"https://cgcookie.com/activity/#bookmarks"
    source_code = r.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")
    print("Gathering Bookmarks...")
    for link in soup.findAll("h5", {"class": "module--track__heading"}):
        title = link.string
        print("Found bookmark for " + title)
        bookmark_title.append(title)

    for link in soup.findAll("a", {"class": "module--track__outer-link"}):
        href = link.get("href")
        link_number += 1
        # print("Found Bookmark #" + str(link_number) + ":\n" + href)
        bookmark_href.append(href)

    print("Number of bookmarks found: " + str(link_number))


def get_course_files(max_pages=None):
    if max_pages is None:
        max_pages = len(bookmark_href)
    print("Number of bookmarks selected: " + str(max_pages) + "/" + str(len(bookmark_href)))
    bookmark_number = 1
    zip_number = 0

    while len(bookmark_href) > 0 and bookmark_number <= max_pages:
        lesson_number = 1
        url = bookmark_href.pop(0)
        title = bookmark_title.pop(0)
        title = title[:-1]  # Must remove extra spaces
        title = title.replace(":", "")
        title = title.replace("–", "-")
        print("\nNavigating to bookmark " + title)
        source_code = r.get(url + "#files")
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "html.parser")
        path = download_path + title
        try:
            os.mkdir(path)
        except FileNotFoundError:
            os.mkdir(download_path)
            os.mkdir(path)
        except FileExistsError:
            pass

        for link in soup.findAll("a", {"data-post-type": "cgc_lessons"}) or soup.findAll("a", {"data-post-type": "cgc_archive"}):
            zip_file = link.get("href")
            file_name = link.get("data-title")
            file_name = file_name.replace(":", "")
            file_name = file_name.replace("–", "-")
            file_name = str(lesson_number).zfill(3) + " " + file_name
            if file_name.endswith(".zip"):
                pass
            else:
                file_name += ".zip"
            # print(file_name)
            # print(zip_file)
            if os.path.isfile(path + "/" + file_name):
                print("File " + file_name + " already exists...\n" + "Moving to next file.\n")
            else:
                print("Downloading " + str(file_name) + " ...")
                download_file = requests.get(zip_file)
                with open(path + "/" + file_name, "wb") as file_output:
                    file_output.write(download_file.content)
                    zip_number += 1
            lesson_number += 1
        bookmark_number += 1
    print("Zip files downloaded: " + str(zip_number))


# ***************************   Beginning of Program    *************************** #

# ***************************   Start Login Session    *************************** #

with requests.session() as r:
    logged_in = False
    login_url = "https://cgcookie.com/wp-login.php"
    r.get(login_url)
    login_data = dict(log=USERNAME, pwd=PASSWORD)
    print("Logging in user " + USERNAME + "...")
    r.post(login_url, data=login_data)
    page = r.get("https://cgcookie.com/login/")
    # print(page.text) #  Shows HTML
    if "You are logged in." in page.text:
        logged_in = True
        print("Successfully logged in!")
        # print(logged_in)
        logging.debug(r.cookies)
    else:
        logging.error("Failed to log in.")
        if page.status_code == requests.codes.ok:
            logging.warning("Please check Username and Password.")
            exit()
        else:
            page.raise_for_status()  # Exits with Error response
            exit()
# ***************************   Other Functions    *************************** #

    find_bookmarks()
    get_course_files()  # Blank gets all course files. Put number for number of courses to download, starting from Top Left
