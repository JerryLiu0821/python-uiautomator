import os
import shutil

cfg = "cfg.txt"

rdict = {
"print": "echo",
"return": "back",
}

files = []
if os.path.exists(cfg):
    with open(cfg, "r") as fp:
        files = fp.readlines()

if os.path.exists("new"):
    shutil.rmtree("new")
os.mkdir("new")

for filename in files:
    filename = filename.strip()
    sfp = open(os.path.join("new",filename), "w")
    if not os.path.exists(filename):
        print filename + " not exists"
        continue
    with open(filename, "r") as fp:
        for line in fp:
            for k,v in rdict.items():
                if line.__contains__(k):
                    print line+ "      "+ k + ", "+ v
                    line = line.replace(k, str(v))
            sfp.write(line)
    sfp.close()
