import random, ipaddress, os

random.seed(0)

# Use a small set of subnets so generated IPs are less unique / repeat more often
_SUBNETS = ["10.0.0.", "10.0.1.", "10.0.2.", "10.0.3."]
_POOL_SIZE = 50
_HOST_POOL = [f"{random.choice(_SUBNETS)}{random.randint(1, 254)}" for _ in range(_POOL_SIZE)]

def rand_ip():
    # return an IP from the small pool so src/dst pairs repeat often
    return random.choice(_HOST_POOL)

def rand_port():
    return random.randint(1, 65535)

def rand_ts():
    base = 1732930000
    return base + random.randint(0, 5000)

actions = ["ACCEPT", "REJECT"]
statuses = ["OK", "NODATA", "SKIPDATA"]

def generate_testcase(filename: str, target_size_mb: int = 20) -> str:
    target_size = target_size_mb * 1024 * 1024
    path = os.path.join(os.getcwd(), "..", "data", filename)
    with open(path, "w") as f:
        size = 0
        while size < target_size:
            if random.random() < 0.1:
                start = rand_ts()
                end = start + random.randint(10, 80)
                log_status = random.choice(["NODATA", "SKIPDATA"])
                line = f"2 123456789010 eni-ab12cd34ef5678901 - - - - - - - {start} {end} - {log_status}\n"
            else:
                src = rand_ip()
                dst = rand_ip()
                srcp = rand_port()
                dstp = rand_port()
                proto = 6
                packets = random.randint(1, 50)
                bytes_ = packets * random.randint(40, 300)
                start = rand_ts()
                end = start + random.randint(10, 80)
                action = random.choice(actions)
                log_status = "OK"
                line = (
                    f"2 123456789010 eni-ab12cd34ef5678901 {src} {dst} {srcp} {dstp} "
                    f"{proto} {packets} {bytes_} {start} {end} {action} {log_status}\n"
                )
            f.write(line)
            size += len(line) # each character is 1 byte

    return path
