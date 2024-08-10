## Overview
This project is a Python script to automate the process of downloading, extracting, and parsing a KML file containing USA FAA airspace recognized identification areas data.
  The script uses Playwright for web scraping, BeautifulSoup for HTML parsing, and pandas for data manipulation. The script performs the following steps:
* Downloads a KML file from the specified URL.
* Parses the KML file to extract airspace restriction data.
* Converts the parsed data into a pandas DataFrame and prints it in JSON format.

### Packages
* Playwright
* pandas
* BeautifulSoup4
* pykml

### To Install Packages
pip install pandas beautifulsoup4 pykml playwright

### Install Playwright browsers
* playwright install
