import cmd
from flowparser.parser import Parser
import flowparser.constants as constants
import ipaddress as ip
import json

class SchemaError(Exception):
    pass

class FlowlogParserCLI(cmd.Cmd):
    intro = 'Welcome to the flowlog parser shell.   Type help or ? to list commands.\n'
    prompt = '(flowlog_parser) '
    file = None
    
    def do_load(self, arg):
        'Load flow logs from a specified file:  LOAD path/to/flowlog.txt\nIf the schema is set, it will be used; otherwise, the default schema is applied.'
        print(f'Loading flow logs from {arg}...\n', file=self.stdout)
        if hasattr(self, 'schema'):
            self.parser = Parser(path=arg, schema=self.schema)
        else:
            self.parser = Parser(path=arg)

        self.parser.deserialize()

    def do_set_schema(self, arg):
        'Set the schema for parsing flow logs:  SET_SCHEMA default|all\n Set the custom schema for parsing flow logs: SET_SCHEMA dstaddr srcaddr srcport dstport protocol packets bytes start end action log-status'
        try:
            fields = arg.split(' ')
            if len(fields) == 1 and fields[0].lower() == 'default':
                self.schema = constants.FLOW_LOG_SCHEMA_DEFAULT
            elif len(fields) == 1 and fields[0].lower() == 'all':
                self.schema = list(constants.FLOW_LOG_SCHEMA_ALL)
            else:
                for field in fields:
                    if field not in constants.FLOW_LOG_SCHEMA_ALL:
                        raise SchemaError(f'Invalid field: {field}')
                self.schema = fields
                
            print(f'Schema set to {arg}.\n', file=self.stdout)
        except ValueError as e:
            print(f'Invalid arguments: {e}. Usage: SET_SCHEMA default|all or SET_SCHEMA <field1> <field2> ...\n', file=self.stdout)
            return
        except SchemaError as e:
            print(f'{e}\n', file=self.stdout)
            return
    
    def do_search_src(self, arg):
        'Search flow logs by source IP:  SEARCH_SRC <src_ip> [output_file]'

        output_file = None
        try:
            split_args = arg.split()
            if len(split_args) == 2:
                src_ip, output_file = split_args
            elif len(split_args) == 1:
                src_ip = split_args[0]
            else:
                raise ValueError
        except ValueError:
            print('Invalid arguments. Usage: SEARCH_SRC <src_ip> [output_file]\n', file=self.stdout)
            return

        # validate IP addresses
        try:
            ip.ip_address(src_ip)
        except ValueError:
            print(f'Invalid IP address: {src_ip!r}. Please provide a valid IPv4 address.\n', file=self.stdout)
            return

        results = self.parser.search_by_source_ip(src_ip)
        for flowlog in results:
            print(flowlog, file=self.stdout)
        print(f'\nTotal results: {len(results)}\n', file=self.stdout)

        if output_file:
            with open(output_file, 'w') as f:
                json_obj = json.dumps(
                    [
                        {k: v for k, v in flowlog.__dict__.items() if k != "schema"}
                        for flowlog in results
                    ],
                    indent=2,
                )
                f.write(json_obj)

    def do_search_dst(self, arg):
        'Search flow logs by destination IP:  SEARCH_DST <dst_ip> [output_file]'

        output_file = None
        try:
            split_args = arg.split()
            if len(split_args) == 2:
                dst_ip, output_file = split_args
            elif len(split_args) == 1:
                dst_ip = split_args[0]
            else:
                raise ValueError
        except ValueError:
            print('Invalid arguments. Usage: SEARCH_DST <dst_ip> [output_file]\n', file=self.stdout)
            return

        # validate IP addresses
        try:
            ip.ip_address(dst_ip)
        except ValueError:
            print(f'Invalid IP address: {dst_ip!r}. Please provide a valid IPv4 address.\n', file=self.stdout)
            return

        results = self.parser.search_by_destination_ip(dst_ip)
        for flowlog in results:
            print(flowlog, file=self.stdout)
        print(f'\nTotal results: {len(results)}\n', file=self.stdout)

        if output_file:
            with open(output_file, 'w') as f:
                json_obj = json.dumps(
                    [
                        {k: v for k, v in flowlog.__dict__.items() if k != "schema"}
                        for flowlog in results
                    ],
                    indent=2,
                )
                f.write(json_obj)
        
    def do_search_src_dst(self, arg):
        'Search flow logs by source and destination IP:  SEARCH_SRC_DST <src_ip> <dst_ip> [output_file]'
        output_file = None
        src_ip, dst_ip = "", ""
        try:
            split_args = arg.split()
            if len(split_args) == 3:
                src_ip, dst_ip, output_file = split_args
            elif len(split_args) == 2:
                src_ip, dst_ip = split_args
        except ValueError:
            print('Invalid arguments. Usage: SEARCH_SRC_DST <src_ip> <dst_ip>\n', file=self.stdout)
            return

        # validate IP addresses
        try:
            ip.ip_address(src_ip)
            ip.ip_address(dst_ip)
        except ValueError:
            print(f'Invalid IP address: {src_ip!r} or {dst_ip!r}. Please provide valid IPv4 addresses.\n', file=self.stdout)
            return

        results = self.parser.search_by_source_and_destination_ip(src_ip, dst_ip)
        for flowlog in results:
            print(flowlog, file=self.stdout)
        print(f'\nTotal results: {len(results)}\n', file=self.stdout)

        if output_file:
            with open(output_file, 'w') as f:
                # Build list of dicts excluding any 'schema' property before dumping to JSON
                json_obj = json.dumps(
                    [
                        {k: v for k, v in flowlog.__dict__.items() if k != "schema"}
                        for flowlog in results
                    ],
                    indent=2,
                )
                f.write(json_obj)

    def do_get_connection_count(self, arg):
        'Get connection count by src_ip, src_port, dst_ip, dst_port, protocol:  GET_CONNECTION_COUNT <src_ip> <src_port> <dst_ip> <dst_port> <protocol>'
        try:
            src_ip, src_port, dst_ip, dst_port, protocol = arg.split()
        except ValueError:
            print('Invalid arguments. Usage: GET_CONNECTION_COUNT <src_ip> <src_port> <dst_ip> <dst_port> <protocol>\n', file=self.stdout)
            return
        
        try:
            ip.ip_address(src_ip)
            ip.ip_address(dst_ip)
        except ValueError:
            print(f'Invalid IP address: {src_ip!r} or {dst_ip!r}. Please provide valid IPv4 addresses.\n', file=self.stdout)
            return

        count = self.parser.get_connection_count(src_ip, src_port, dst_ip, dst_port, protocol)
        print(f'Connection count: {count}\n', file=self.stdout)
