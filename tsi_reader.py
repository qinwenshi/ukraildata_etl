# tsi_reader.py

'''tsi_reader - Read ATOC TOC Specific Interchange times

This module reads data from a TSI file from ATOC containing additional
information on the interchange times between train companies at certain TOCs
(for example, where a particular company has its own set of platforms at some
distance from the others.'''

from nrcif_fields import *

class TSI(object):
    '''A simple hander for TSI files.'''

    layout = [  TextField("Station code",3),
                TextField("Arriving train TOC", 2),
                TextField("Departing train TOC", 2),
                IntegerField("Minimum Interchange Time",2),
                VarTextField("Comments", 100) ]

    def __init__(self, cur):

        self.cur = cur

    def process(self, record):

        fields = record.rstrip().split(",")
        if len(fields) != 5:
            raise ValueError("Line {} in the TSI file does not have five fields".format(record))

        result = [None] * 5
        for i in range(0,5):
            result[i] = self.layout[i].read(fields[i])

        self.cur.execute("INSERT INTO tsi.tsi VALUES(%s,%s,%s,%s,%s);", result)

def main():
    import sys, nrcif
    if len(sys.argv) != 2:
        print("When called as a script, needs to be provided with a TSI file to process")
        sys.exit(1)
    cur = nrcif.DummyCursor()
    tsi = TSI(cur)
    with open(sys.argv[1], 'r') as fp:
        for line in fp:
            tsi.process(line)
    print("Processing complete")

if __name__ == "__main__":
    main()
