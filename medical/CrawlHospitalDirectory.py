__author__ = 'hzhu'

from bs4 import BeautifulSoup
from urllib.request import urlopen

baseURL = "http://www.medilexicon.com/hospitalsdirectory.php?hcountry=USA&keywords=&searchtype=hospital&page="

for pagenum in range(1, 1):
    webpage = urlopen(baseURL + str(pagenum)).read()
    soup = BeautifulSoup(webpage)


