import pandas as pd
import re
import os

home = os.environ["HOME"]
with open(home + "/my_dev/IMR/result/中辞書作成中.txt") as f:
    lines = f.readlines()

tmp = []
tmp1 = []
for line in lines:
    # print(line)
    if "：" in line:
        pass
    elif re.match(r"\[", line):
        # print(line)
        elms = re.split("'", line)
        for elm in elms:
            tmp.append(elm)
    elif "===" in line:
        pass
    else:
        line = line.rstrip()
        if len(line) > 0:
            tmp1.append(line)

tmp = sorted(set(tmp))
tmp1 = sorted(set(tmp1))
df = pd.DataFrame(tmp)
df1 = pd.DataFrame(tmp1)
df2 = df1[~df1.isin(tmp)]
tmp2 = []
for i in df2[0]:
    i = str(i)
    if i == "nan":
        pass
    else:
        print(i)
        tmp2.append(i)
