import time, traceback
log = open("gpu_test.log", "w", encoding="utf-8")
def p(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    log.write(s + "\n"); log.flush()
try:
    import torch
    p("torch", torch.__version__)
    p("cuda_available", torch.cuda.is_available())
    p("cuda_runtime", torch.version.cuda)
    p("device", torch.cuda.get_device_name(0))
    p("capability(本机算力)", torch.cuda.get_device_capability(0))
    p("arch_list(torch支持的架构)", torch.cuda.get_arch_list())
    t = time.time()
    x = torch.randn(1024, 1024, device="cuda")
    torch.cuda.synchronize()
    p("alloc_ok %.2fs" % (time.time() - t))
    t = time.time()
    y = (x @ x).sum().item()
    torch.cuda.synchronize()
    p("matmul_ok %.2fs sum=%.1f" % (time.time() - t, y))
    p("==> GPU 计算正常")
except Exception:
    p("==> 出错:")
    log.write(traceback.format_exc()); log.flush()
    traceback.print_exc()
finally:
    log.close()
