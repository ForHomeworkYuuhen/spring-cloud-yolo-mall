# 识别服务压测：并发打 /recognize，统计吞吐/延迟分布/成功率
import time, statistics, sys
import concurrent.futures as cf
import requests

BASE = "http://localhost:8123"
IMG = r"E:\Code\Yueqian\test_samples\sample1.jpg"

S = requests.Session()
S.trust_env = False  # 绕过系统代理(Clash)，直连 localhost

with open(IMG, "rb") as f:
    IMG_BYTES = f.read()


def wait_ready(timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = S.get(BASE + "/health", timeout=3)
            if r.ok and r.json().get("status") == "ok":
                return r.json()
        except Exception:
            pass
        time.sleep(1)
    return None


def one(model):
    t0 = time.perf_counter()
    try:
        r = S.post(BASE + "/recognize",
                   files={"file": ("s.jpg", IMG_BYTES, "image/jpeg")},
                   data={"model": model}, timeout=60)
        ms = (time.perf_counter() - t0) * 1000
        if r.status_code == 200 and "detections" in r.text:
            return (True, ms, r.json().get("infer_ms"))
        return (False, ms, None)
    except Exception:
        return (False, (time.perf_counter() - t0) * 1000, None)


def pct(sorted_arr, p):
    if not sorted_arr:
        return 0
    return sorted_arr[min(len(sorted_arr) - 1, int(len(sorted_arr) * p))]


def run(model, total, conc):
    one(model)  # 预热
    start = time.perf_counter()
    res = []
    with cf.ThreadPoolExecutor(max_workers=conc) as ex:
        for r in ex.map(lambda _: one(model), range(total)):
            res.append(r)
    wall = time.perf_counter() - start
    oks = [r for r in res if r[0]]
    lat = sorted(r[1] for r in oks)
    infers = [r[2] for r in oks if r[2] is not None]
    print(f"\n[{model}]  请求 {total}  并发 {conc}")
    print(f"  成功 {len(oks)}/{total}   失败 {total-len(oks)}")
    print(f"  总耗时 {wall:.2f}s   吞吐 {len(oks)/wall:.1f} req/s")
    print(f"  端到端延迟ms  p50={pct(lat,0.5):.0f}  p90={pct(lat,0.9):.0f}  p99={pct(lat,0.99):.0f}  max={lat[-1]:.0f}" if lat else "  无成功请求")
    if infers:
        print(f"  服务端推理ms  均值={statistics.mean(infers):.1f}  min={min(infers):.1f}  max={max(infers):.1f}")
    return {"model": model, "total": total, "conc": conc, "ok": len(oks),
            "wall": wall, "qps": len(oks)/wall if wall else 0,
            "p50": pct(lat,0.5), "p90": pct(lat,0.9), "p99": pct(lat,0.99),
            "infer_avg": statistics.mean(infers) if infers else 0}


if __name__ == "__main__":
    info = wait_ready()
    if not info:
        print("服务未就绪，退出"); sys.exit(1)
    print("服务就绪:", info)

    print("\n========== 1) 三模型横向对比（各 60 请求 / 并发 10）==========")
    rows = [run(m, 60, 10) for m in ["11s_balanced", "11s_base", "12x_balanced"]]

    print("\n========== 2) 部署模型 11s_balanced 持续压测（300 请求 / 并发 20）==========")
    heavy = run("11s_balanced", 300, 20)

    print("\n========== 汇总（吞吐 req/s | p50 | p99 | 服务端推理均值ms）==========")
    for r in rows:
        print(f"  {r['model']:<14} qps={r['qps']:.1f}  p50={r['p50']:.0f}  p99={r['p99']:.0f}  infer={r['infer_avg']:.1f}")
    print(f"  {'11s 持续压测':<14} qps={heavy['qps']:.1f}  p50={heavy['p50']:.0f}  p99={heavy['p99']:.0f}  infer={heavy['infer_avg']:.1f}")
