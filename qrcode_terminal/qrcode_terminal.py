#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author: ‘wang_pc‘
@site: 
@software: PyCharm
@file: qrcode_terminal.py
@time: 2017/2/10 16:38
'''
import qrcode
from optparse import OptionParser
import sys

parser = OptionParser()
parser.add_option('-d', '--data', dest='data', help='data to be paser to QRCode')
parser.add_option('-s', '--size', type='choice', choices = ['s','m','l','S','M','L'], dest='size',default='s', help='QRCode size,you can choose S/M/L')

white_block = '\033[0;37;47m  '
black_block = '\033[0;37;40m  '
new_line = '\033[0m\n'

def qr_terminal_str(str,version=1):
    qr = qrcode.QRCode(version)
    qr.add_data(str)
    qr.make()
    output = white_block*(qr.modules_count+2) + new_line
    for mn in qr.modules:
        output += white_block
        for m in mn:
            if m:
                output += black_block
            else:
                output += white_block
        output += white_block + new_line
    output += white_block*(qr.modules_count+2) + new_line
    return output

def draw(str,version=1):
    output = qr_terminal_str(str,version)
    print(output)

def draw_cmd():
    (options, args) = parser.parse_args()
    if not options.data:
        options.data = sys.stdin.readline()[:-1]
    if not options.data:
        print ('data must be specified. see %s -h' % sys.argv[0])
    else:
        size = options.size
        if size == 'm' or size == 'M':
            version = 3
        elif size == 'l' or size == 'L':
            version = 5
        else:
            version = 1
        draw(options.data,version)

if __name__ == '__main__':
    draw_cmd()
