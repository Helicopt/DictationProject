# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import re
import os
import sys
import json
import argparse
import glob
import time
import codecs

__version__ = 'v0.0.1'
global codes
codes = ['correct', 'wrong', 'typo', 'plenty', 'captial']

def init():
    with open('data.json') as fd:
        global data
        data = json.load(fd)

def getWord(tag, ind, direc):
    global data
    if direc == 'horizontal':
        return data[tag]['words'][ind]
    if direc == 'vertical':
        stride = data[tag]['stride']
        row = (len(data[tag]['words'])+stride-1)/stride
        rest = len(data[tag]['words'])%stride
        if rest==0:
            rest = stride
        if ind<rest*row:
            ri = ind%row
            ci = ind/row
            return data[tag]['words'][ri*stride+ci]
        else:
            ind-=rest*row
            ri = ind % (row - 1)
            ci = ind / (row - 1) + rest
            return data[tag]['words'][ri*stride+ci]
    raise ValueError('unknown direction type %s'%direc)

def plenty(x, os = False):
    if len(x)<=1:
        return x
    if x[-1] in ['s', 'x']:
        return x+'es'
    if x[-1]=='y':
        if x[-2] in ['a', 'o', 'u', 'i', 'y', 'e']:
            return x+'s'
        else:
            return x[:-1]+'ies'
    if x[-2:] in ['ch', 'sh']:
        return x+'es'
    if x[-1]=='o':
        if x[-2] in ['a', 'o', 'u', 'i', 'y', 'e'] or os:
            return x+'s'
        else:
            return x+'es'
    if x[-1]=='f' and os:
        return x[:-1]+'ves'
    return x+'s'

def wdis(x, y):
    d = 0
    f = {(-1,-1): 0}
    for i in range(len(x)):
        f[(i,-1)] = 0
    for i in range(len(y)):
        f[(-1,i)] = 0
    for i, p in enumerate(x):
        for j, q in enumerate(y):
            f[(i,j)] = 0
            if p==q:
                f[(i,j)] = f[(i-1,j-1)]+1
            f[(i,j)] = max(f[(i,j)], f[(i-1,j)])
            f[(i,j)] = max(f[(i,j)], f[(i,j-1)])
            d = max(d, f[(i,j)])
    return max(len(x)-d, len(y)-d)

def checkOne(w, s):
    global codes
    if w==s:
        return codes[0]
    if w.lower()==s.lower():
        return codes[4]
    wss = [w, plenty(w), plenty(w, True)]
    sss = [s, plenty(s), plenty(s, True)]
    for ws in wss:
        for ss in sss:
            if ws==ss:
                return codes[3]
    wd = wdis(w, s)
    if wd<=2 and len(s)>5 or wd<=3 and len(s)>8:
        return codes[2]
    return codes[1]


def match(t, d, p):
    tot = 0
    cor = 0
    for i, w in enumerate(p):
        tot+=1
        s = getWord(t, i, d)
        if checkOne(w, s)!='wrong':
            cor+=1
        if tot>20: break
    if cor>3:
        return True
    else:
        return False

def guess(p):
    global data
    for k in data:
        for d in ['horizontal', 'vertical']:
            if match(k, d, p):
                return k, d
    return None, None

def getAnalysis(w):
    return '//'

def correct(p, direction = 'auto', test = ''):
    with open(p) as fd:
        lines = fd.readlines()
        lines = filter(lambda x: x!='', map(lambda x: x.decode('utf-8').strip(), lines))
    tag, direc = guess(lines)
    t = test
    d = direction
    if t!='':
        tag = t
    if d!='auto':
        direc = d
    if tag is None or direc is None:
        raise ValueError('cannot determine which test, please choose one.')
    ind = 0
    marks = {c: [] for c in codes}
    for line in lines:
        if ind>=len(data[tag]['words']): break
        ans = getWord(tag, ind, direc)
        sol = re.split(r'[\s]+', line)[0]
        code = checkOne(sol, ans)
        marks[code].append((sol, ans))
        ind += 1
    ags = [[0], [2,3,4], [1]]
    res = []
    tot = len(data[tag]['words'])
    for ag in ags:
        sum_ = sum([len(marks[codes[a]]) for a in ag])
        res += [sum_, sum_*100./tot]
    res = tuple([p] + res)
    tstamp = time.strftime(r'%Y%m%d%H%M%S', time.localtime(int(time.time())))
    tout = sys.stdout
    rname = '%s-%s-[%s].report'%(tag, direc, tstamp)
    sys.stdout = codecs.open(rname, 'w', 'utf-8')
    print('Testpaper [%s]: correct %d(%.1f%%), almost correct %d(%.1f%%), wrong %d(%.1f%%)'%res)
    for code in codes[1:]:
        print('Err Type [%s]'%code)
        if len(marks[code]):
            for w in marks[code]:
                analysis = getAnalysis(w[1])
                print('\t[x] %s => %s [√], %s'%(w[0], w[1], analysis))
        else:
            print('\tNone')
    print('--End of report.')
    sys.stdout.close()
    sys.stdout = tout
    with codecs.open(rname, 'r', 'utf-8') as fd:
        for line in fd.readlines():
            print(line, end='')
    report = {'date': tstamp, 'test': tag, 'direction': direc, 'testpaper': p, 'delta': marks}
    rname = '%s-%s-[%s].json'%(tag, direc, tstamp)
    with open(rname, 'w') as fd:
        json.dump(report, fd, indent = 2)
    return report

if __name__ == "__main__":
    init()
    parser = argparse.ArgumentParser('judger.py ', description = 'dictation judger %s'%__version__, version = __version__)
    parser.add_argument('testpaper', type = str, nargs = '+', help = 'testpaper to be judged')
    parser.add_argument('-d', '--direction', choices = ['horizontal', 'vertical', 'auto'], default = 'auto', help = 'choose direction')
    parser.add_argument('-t', '--test', type = str, choices = data.keys() + [''], default = '', help = 'specify a test')
    parser.add_argument('-l', '--list', action = "store_true", help = 'list all tests')
    args = parser.parse_args()
    if args.list:
        for i in data:
            print(i)
        exit(0)
    for tp in args.testpaper:
        for ttp in glob.glob(tp):
            correct(ttp, direction = args.direction, test = args.test)
