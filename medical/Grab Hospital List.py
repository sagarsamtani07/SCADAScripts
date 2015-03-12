__author__ = 'Hongyi'

from bs4 import BeautifulSoup
from urllib.request import urlopen
import socket
from urllib.parse import urlparse

f = open('D:/hospital.txt', 'r+')

for i in range(0, 37):
    url = "http://hospitals.webometrics.info/en/North_america/United%20States%20of%20America?page=" + str(i)
    page = urlopen(url).read()

    soup = BeautifulSoup(page)

    for link in soup.find_all('a', target='_blank'):
        if link.parent.name == 'td':
            s = link.string + "\t"
            s += link['href'] + "\t"
            hostname = ""
            try:
                hostname = socket.gethostbyname_ex(urlparse(link['href']).hostname)[2][0]
            except socket.gaierror:
                print("{0}'s webpage {1} is not accessible".format(link.string, link['href']))
                hostname = "Not available"
            s += hostname
            s += "\n"
            # print(s)
            f.write(s)

    print('finish page {0}: {1}'.format(str(i), url))

f.close()