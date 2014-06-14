"""
Interface to google sheets
"""
import sys
import re
import string

from gdata.spreadsheet.service import SpreadsheetsService


SPREADSHEET = '0Av9C7X6RVo7udFJtaTFyX2NvdDlMaGdaUnBJeF9sNFE'
WORKSHEET = 'od6'
HEADERS = ('timestamp', 'title', 'servings', 'tags', 'ingredients', 'instructions')

def getSheetData(spreadsheet=SPREADSHEET, worksheet=WORKSHEET, headers=HEADERS):
    """
    Get the data of the worksheet as a list of rows, each row a dictionary of
    the headers
    """
    client = SpreadsheetsService()

    cols = dict(zip(string.uppercase, headers))
    rLabel = 0
    niceRows = []

    feedArgs = dict(key=spreadsheet, wksht_id=worksheet, visibility='public',
            projection='basic')

    cells = client.GetCellsFeed(**feedArgs)
    for cell in cells.entry:
        label = re.match('^([A-Z]+)([0-9]+)$', cell.title.text)
        cLabel = label.group(1)
        _rLabel = int(label.group(2))
        if _rLabel == 1:
            continue # header row
        if _rLabel > rLabel:
            niceRow = {}
            niceRows.append(niceRow)
            rLabel = _rLabel
        niceRow[cols[cLabel]] = cell.content.text

    return niceRows


def run():
    import pprint
    pprint.pprint(getSheetData(SPREADSHEET, WORKSHEET, HEADERS))

if __name__ == '__main__':
    sys.exit(run())
