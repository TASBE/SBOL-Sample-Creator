import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_info.json', scope)
client = gspread.authorize(creds)

#opening the spreadsheet
spreadsheet = client.open("LCP Project Dictionary")
sheetList = spreadsheet.worksheets()
worksheetNames = []
for sheet in sheetList:
    worksheetNames.append(sheet.title)
for sheetName in worksheetNames:
    currentSheet = spreadsheet.worksheet(sheetName)
    currentInfo = currentSheet.get_all_records(False,2,'',False)
    if len(currentInfo) != 0:
        for index in range(0,len(currentInfo)):
            commonNames = ((currentInfo[index])['Common Name'])


#def NameFinder(sheet,partList):
#    for part in partList:
#        sheet.find(part)


# Extract and print all of the values
#sheet1 = spreadsheet.
#list_of_hashes = sheet.get_all_values()
#print(list_of_hashes)


#sheet called 'Genetic Construct' and 'Reagant'

