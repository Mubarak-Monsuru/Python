from bs4 import BeautifulSoup
import requests
import pandas as pd

html_text = requests.get('https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue').text
soup = BeautifulSoup(html_text, 'html.parser')
# print(soup)

# Get information of the second <table>
table = soup.find_all('table')[1]
# print(table)

# Extract <th> for the columns
world_titles = table.find_all('th')
# print(world_titles)

# Clean up columns and set as dataframe 
table_titles = [title.text.strip() for title in world_titles]
# print(table_titles)
df = pd.DataFrame(columns = table_titles)
# print(df)

# Extract <th> for column data
column_data = table.find_all('tr')
# print(column_data)

# Set data points to the column they belong
for row in column_data[1:]:
    row_data = row.find_all('td')
    individual_row_data = [data.text.strip() for data in row_data]

    length = len(df)
    df.loc[length] = individual_row_data

print(df)