#!/usr/bin/env python

import argparse

def read_scan(scan_fn):
    """yield position and barcode"""
    f = open(scan_fn, 'r')
    while True:
        line = next(f).strip('\r\n').split(',')
        if 'Well' not in line:
            yield line
def main():
    markerLookup = {
    'P10':['AS7','PfPK2'],
    'P11':['TA40'],
    'P12':['PolyA'],
    'P1':['AS1','AS11','AS31'],
    'P2':['AS32','TA1','AS34'],
    'P3':['TA109','TA87'],
    'P4':['AS2','AS14'],
    'P5':['TA81','AS12'],
    'P6':['TA60','PFG377'],
    'P7':['AS19','Ara2','AS21'],
    'P8':['AS8','AS15'],
    'P9':['B7M19','AS2','AS25']
    }

    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input', help='scan file to populate platemaps', required=True)
    p.add_argument('-o', '--basename', help='basename of output files', required=True)
    a = p.parse_args()

    # iterate through plate numbers
    for plateNum in markerLookup:
        f = open(a.basename+'_'+plateNum+".csv", 'w+')

        # print header
        header = ','.join(['Well'] + [marker for marker in markerLookup[plateNum]])
        f.write(header + '\n')

        # print well plus barcode * number of markers
        for pos, bc in read_scan(a.input):
            items = [pos] + [bc for i in range(len(markerLookup[plateNum]))]
            f.write(','.join(items) + '\n')



if __name__ == '__main__':
    main()
