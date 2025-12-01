# AWS flow log parser

## Functional requirements
- Filter rows based on source/destination IP addresses
- Store counts for connections
- Tests

## Notes
- 20 MB flow log size
- The IP addresses are IPv4 only
- Input file is a plain text file

## Design
- 20 MB file size comfortably fits within address space
    1. Parsing CPU-bound (not amenable to multithreading here)
    2. Overhead for multiprocessing too expensive with respect to input size
- Parser class
    1. With `\n` as delimiter, serialize each row into a Python object (default serializer supports version 2 flow logs)
    2. Store in an array
- Similar to database indexing, create indices on source
    1. Point queries, can use hashmaps
- For both counts and indexes, can simultaneously process during serialization step
- Expose instrument as CLI
    1. search and get_counts functionality
    2. Dump output as JSON

```
# Source IP index: Source IP -> row index
{
    "1.1.1.1": [0, 3, 4, 1],
    "2.3.255.255": [2, 5]
}

# Pair IP index: Pair IP -> row index
{
    ("1.1.1.1", "255.255.255.255") -> [0]
}
```

## Usage
- Move flow log txt files underneath `data/`. You can generate sample test cases using `tests/generator.py` or by running the test suite once.
- `python3 main.py` to start CLI
- `help` to list commands
- `help <cmd>` to get command documentation

```python
# valid fields
fields = ["version",
    "account-id",
    "interface-id",
    "srcaddr",
    "dstaddr",
    "srcport",
    "dstport",
    "protocol",
    "packets",
    "bytes",
    "start",
    "end",
    "action",
    "log-status",
    "vpc-id",
    "subnet-id",
    "instance-id",
    "tcp-flags",
    "type",
    "pkt-srcaddr",
    "pkt-dstaddr",
    "region",
    "az-id",
    "sublocation-type",
    "sublocation-id",
    "pkt-src-aws-service",
    "pkt-dst-aws-service",
    "flow-direction",
    "traffic-path",
    "ecs-cluster-arn",
    "ecs-cluster-name",
    "ecs-container-instance-arn",
    "ecs-container-instance-id",
    "ecs-container-id",
    "ecs-second-container-id",
    "ecs-service-name",
    "ecs-task-definition-arn",
    "ecs-task-arn",
    "ecs-task-id",
    "reject-reason",
    "resource-id",
    "encryption-status"]
```

```bash
# example usage
load data/temp_flowlogs.txt
set_schema default
search_src 10.0.1.194
get_connection_count 10.0.0.159 21248 10.0.1.130 33202 6

# for custom schema (make sure flow logs adhere to this, and must be called before load)
set_schema interface-id srcaddr srcport dstaddr dstport protocol packets bytes start end action log-status

# write to output
search_src 10.0.1.194 output.txt
```

## Testing
`cd tests && python3 tests.py` will run integration test suite. It uses random generation for test cases, but the tests are based off `random.seed(0)`. Please use `cpython` implementation with version `3.9.6` for deterministic testing behavior. Ideally, I'd put this in a `dockerfile` if it were production code.
