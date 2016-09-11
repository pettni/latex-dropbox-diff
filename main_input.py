

import sys
import datetime

from cloud import get_files


def main(argv):

    xString = raw_input("Enter the name of the file: ")

    date_entry = raw_input("Enter a date in YYYY-MM-DD format: ")
    year, month, day = map(int, date_entry.split('-'))
    date1 = datetime.date(year, month, day)

    get_files(xString, date1)

    pass

if __name__ == "__main__":
    main(sys.argv)
