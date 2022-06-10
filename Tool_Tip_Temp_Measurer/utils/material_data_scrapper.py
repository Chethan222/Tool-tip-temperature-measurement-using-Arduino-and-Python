import requests
import pandas as pd
from bs4 import BeautifulSoup

#URL to fetch
sourceLink = 'https://thermtest.com/thermal-resources/materials-database'

#Getting HTML data from the website
response = requests.get(sourceLink,headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})

content = response.content

#Converting byted to string
soup = BeautifulSoup(content,'html.parser')

#Finding required table,thead,tbody and trow from the html data
table = soup.find("table",{"class":'tablepress'})
thead = table.find('thead')
tbody = table.find('tbody')
trows = tbody.select('tr[class^="row"]')

#Getting header data
ths = thead.find('tr').find_all('th')
headers = [ x.text for x in ths]
headers

#Creating dict template 
materialDetails = dict((header,[]) for header in headers)
materialDetails

#Getting data from each row and appending to corresponding headder array
for tr in trows:
    i=0
    for td in tr:
        if(td.text.strip()!=''):
            materialDetails[headers[i]].append(td.text)
            i=i+1
       
#Converting dictionary into dataframe
df = pd.DataFrame(materialDetails)

#Exporting data to a csv file
df.to_csv("materials_data.csv")




