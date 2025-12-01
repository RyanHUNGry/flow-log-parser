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
- Deserializer class
    1. With `\n` as delimiter, serialize each row into a Python object (default serializer supports version 2 flow logs)
    2. Store in an array
    3. `i-01234567890123456 eni-1111aaaa2222bbbb3 subnet-aaaaaaaa012345678 10.0.1.5 203.0.113.5 10.0.1.5 203.0.113.5 #Traffic from the source instance to host on the internet` -> bytes
- Similar to database indexing, create indices on source
    1. Point queries, can use hashmaps
- For both counts and indexes, can simultaneously process during serialization step
- Expose instrument as CLI

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
- Move flow log txt files underneath `data/`
- `python3 main.py` to start CLI
- `help` to list commands
- `help <cmd>` to get command documentation

```bash
# example usage
load data/temp_flowlogs.txt
set_schema default
search_src 10.0.1.194
get_connection_count 10.0.0.159 21248 10.0.1.130 33202 6
```

## Testing
`cd tests && python3 tests.py` will run integration test suite. It uses random generation for test cases, but the tests are based off `random.seed(0)`. Please use `cpython` implementation with version `3.9.6` for deterministic testing behavior. Ideally, I'd put this in a `dockerfile` if it were production code.
