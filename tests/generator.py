import random, ipaddress, os

def rand_ip():
    return str(ipaddress.IPv4Address(random.randint(0x0A000000, 0x0AFFFFFF)))

def rand_port():
    return random.randint(1, 65535)

def rand_ts():
    base = 1732930000
    return base + random.randint(0, 5000)

actions = ["ACCEPT", "REJECT"]
statuses = ["OK", "NODATA", "SKIPDATA"]

target_size_mb = 20
target_size = target_size_mb * 1024 * 1024

path = os.path.join(os.getcwd(), "..", f"mock_flow_logs_{target_size_mb}mb.txt")

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
