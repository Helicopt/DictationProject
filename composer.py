import os
import sys
import re
import json

__version__ = "v0.0.1"

def nxtans(rec, s):
    while len(rec):
        if rec[0][0]!='[':
            # print('!%s!'%rec[0])
            del rec[0]
            continue
        assert rec[0].strip()==s, str((rec[0], s))
        ans = rec[1].strip()
        del rec[0]
        del rec[0]
        return ans
    return ''

if __name__ == "__main__":
    print("Words Composer %s"%__version__)
    all = {}
    with open('records.temp') as fd:
        recs = fd.readlines()
    for i in os.listdir('.'):
        if os.path.splitext(i)[-1]=='.txt':
            print(i)
            cc = []
            all[os.path.splitext(i)[0].replace('H', '')] = {'words': cc, 'stride': 4}
            with open(i) as fd:
                lines = list(filter(lambda x: x!='', map(str.strip, fd.readlines())))
            for lin in lines:
                words = re.split(r'[\s]+', lin)
                if len(words)==1:
                    cc.append(words[0])
                else:
                    # print(words)
                    ans = nxtans(recs, str(words))
                    if ans!='':
                        cc.append(ans)
                    else:
                        print(words)
                        c = raw_input()
                        cc.append(c)
    with open('data.json', 'w') as fd:
        json.dump(all, fd, indent = 2)
