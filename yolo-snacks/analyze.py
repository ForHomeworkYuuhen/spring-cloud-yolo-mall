import glob, os, collections, yaml
base = r"E:\Code\Yueqian\archive\Iranian Snack and Chips Detection (YOLO Format)"
names = yaml.safe_load(open(os.path.join(base, "data.yaml"), encoding="utf-8"))["names"]
out = open("analyze.log", "w", encoding="utf-8")
def p(s):
    print(s); out.write(s + "\n")
for split in ["train", "valid", "test"]:
    inst = collections.Counter(); imgs = collections.Counter()
    files = glob.glob(os.path.join(base, split, "labels", "*.txt"))
    for f in files:
        seen = set()
        for ln in open(f):
            t = ln.split()
            if t:
                c = int(t[0]); inst[c] += 1; seen.add(c)
        for c in seen:
            imgs[c] += 1
    p("\n==== %s: %d 张图 ====" % (split, len(files)))
    counts = [(i, names[i], inst.get(i, 0), imgs.get(i, 0)) for i in range(len(names))]
    for i, n, ic, im in sorted(counts, key=lambda x: x[2]):
        p("  cls%2d  实例=%4d  含该类图=%3d  %s" % (i, ic, im, n))
    if split == "train":
        vals = [c[2] for c in counts]
        p(">>> 最多/最少实例: %d / %d  (不均衡比 %.1fx)" % (max(vals), min(vals), max(vals)/max(1, min(vals))))
out.close()
