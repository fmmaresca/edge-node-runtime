#!/usr/bin/env python3
import os
import random
import sys
import time

def main():
    ttl = int(os.getenv("DUMMY_TTL_S", "5"))
    print(f"dummy workload starting ttl={ttl}s pid={os.getpid()}", flush=True)
    t0 = time.time()
    while time.time() - t0 < ttl:
        print("dummy: working...", flush=True)
        time.sleep(1)
    rc = random.choice([1, 2, 3])
    print(f"dummy: exiting rc={rc}", flush=True)
    sys.exit(rc)

if __name__ == "__main__":
    main()
