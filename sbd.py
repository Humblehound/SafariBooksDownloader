from lxml import html
from bs4 import BeautifulSoup
import pdfkit
import re
import mechanize
import cookielib
import argparse
import os


def remove_non_ascii_chars(text):
    return re.sub(r'[^\x00-\x7F]+', ' ', text)


def get_credentials(arguments):
    if arguments.email is not None and arguments.password is not None:
        return arguments.email, arguments.password
    elif os.environ.has_key("SBD_LOGIN") and os.environ.has_key("SBD_PASSWORD"):
        return os.environ["SBD_LOGIN"], os.environ["SBD_PASSWORD"]
    else:
        print "You must provide Safari Books Online credentials"
        exit()


baseurl = 'https://www.safaribooksonline.com/'
baseurl_unsafe = 'http://www.safaribooksonline.com/'
login_url = "https://www.safaribooksonline.com/accounts/login"

parser = argparse.ArgumentParser(
    description='A small program to download books from Safari Books Online for offline storage.')
parser.add_argument('-e', '--email', help='Safari Books Online login')
parser.add_argument('-p', '--password', help='Safari Books Online password')
parser.add_argument('safari_book_url',
                    help='Safari book url, ex. https://www.safaribooksonline.com/library/view/software-build-systems/XXX/')

args = parser.parse_args()
url = args.safari_book_url
email, password = get_credentials(args)

if baseurl not in url and baseurl not in baseurl_unsafe not in url:
    print "You must pass a valid safari books online url"
    exit()

cj = cookielib.CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.open("https://www.safaribooksonline.com/accounts/login")
br.select_form(nr=0)
br.form['email'] = email
br.form['password1'] = password
response = br.submit()
print br.response.code
page = br.open(url).read()

# get rid of non ascii characters
page_ascii_only = remove_non_ascii_chars(page)

tree = html.fromstring(page_ascii_only)
urllist = []

wtf = tree.xpath('//*[@id="toc"]')

for atag in tree.xpath('//*[@class="detail-toc"]//li/a'):
    urllist.append(baseurl + atag.attrib['href'])

bookpages = []

complete_book = ''

# fetch all the book pages
# for x in range(0, urllist.__len__()):
#     print "fetching page nr " + str(x) + "out of " + str(urllist.__len__())
#     bookpage = br.open(urllist[x]).read()
#     bookpage_clean = remove_non_ascii_chars(bookpage)
#     # bookpage_content = html.fromstring(bookpage_clean)
#     # purebook = bookpage_content.xpath('//*[@id="sbo-rt-content"]')
#     bs = BeautifulSoup(bookpage_clean, 'lxml')
#     content = bs.find("div", {"id": "sbo-rt-content"})
#     for img in content.findAll('img'):
#         img['src'] = img['src'].replace("/library/", baseurl + "library/")
#     complete_book += content.__str__()
#
# pdfkit.from_string(complete_book, 'book.pdf', options=dict(encoding="utf-8"))
