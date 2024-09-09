import markdown
from bs4 import BeautifulSoup
import csv
from rich import print
import requests
import datetime
import os
from dotenv import load_dotenv # type: ignore
from rich.traceback import install
# install(show_locals=True)

load_dotenv()  # take environment variables from .env.

GH_PAT = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")


def get_links_and_names(soup):
  data = []
  for link_element in soup.find_all('a'):
    repository = link_element.get('href')
    name = link_element.string
    maintainer_url = repository[:repository.rfind('/')]
    element = {
      "repository": repository,
      "maintainer_url": maintainer_url,
      "plugin_name": name
    }
    data.append(element)
  return data


def get_last_update_date(soup):
  last_commit = soup.find_all("h3")[0].string
  last_commit = str(last_commit).replace("Commits on ", "")
  months = {
    "Jan": "01", "Feb": "02", "Mar": "03",
    "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09",
    "Oct": "10", "Nov": "12", "Dec": "12",
  }
  year = last_commit[-4:]
  month = last_commit[:3]
  month = months[last_commit[:3]]
  day = last_commit[4:6]
  iso_date = f"{year}-{month}-{day}"
  return iso_date


def get_development_status(iso_date):
  year = iso_date[:4]
  month = iso_date[5:7]
  day = iso_date[:2]
  last_update_date_object = datetime.date(year=int(year),
                month=int(month),
                day=int(day))
  todays_date = datetime.date.today()

  difference = todays_date - last_update_date_object
  diff_days = difference.days

  development_status = ""
  if diff_days > 365:
    development_status = "abandoned"
  if diff_days > 182 and diff_days <= 365:
    development_status = "stale"
  if diff_days <= 182:
    development_status = "active"
  return development_status


def aggregate_development_status():
  for index, item in enumerate(data):
    if "last_update" in item:
      item["development_status"] = get_development_status(item["last_update"])
      ...
    # else:
      # print(None)
      # ...
    ...
  ...


def visit_maintainer_page(url):
  req = requests.get(url)
  html = req.text
  soup = BeautifulSoup(html, 'html.parser')
  name = soup.find("h1", {"class": "vcard-names"})\
             .find("span", {"itemprop": "name"}).text.strip()
  handle = soup.find("h1", {"class": "vcard-names"})\
             .find("span", {"itemprop": "additionalName"}).text.strip()
  if name:
    full_name = f'{name} - {handle}'
  else:
    full_name = handle
  return full_name


def visit_repo(url, data_index):
  req = requests.get(url)
  html = req.text
  soup = BeautifulSoup(html, 'html.parser')

  commits_url = soup.find("span", {"id": "history-icon-button-tooltip"})\
      .find("a").get("href")
  # print(commits_url)

  """https://github.com/fxal/obsidian-youhavebeenstaring-plugin/commits/master/
  """
  req = requests.get("https://github.com" + commits_url)
  # print(req)
  html = req.text
  # print(html)
  soup = BeautifulSoup(html, 'html.parser')
  data[data_index]["last_update"] = get_last_update_date(soup)




if __name__ == "__main__":
  with open("all obsidian plugins - README.md", "r", encoding="utf-8") as input_file:
    text = input_file.read()
  html = markdown.markdown(text)
  soup = BeautifulSoup(html, 'html.parser')

  data = get_links_and_names(soup)
  print("total plugins: ", len(data))
  # print(data)

  # visit_repo('https://github.com/fxal/obsidian-youhavebeenstaring-plugin')

  for index, item in enumerate(data[0:5]): # remove [0:10] when DONE
    print("getting data from:", item["repository"])
    visit_repo(item["repository"], index)
    maintainer = visit_maintainer_page(item["maintainer_url"])
    item["maintainer"] = maintainer
  aggregate_development_status()
  print(data[0:5])

  # with open('result.csv', 'w', newline='') as csv_file:
  #   spam_writer = csv.writer(csv_file)


  # print(soup.prettify())
