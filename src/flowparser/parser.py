import collections
import flowparser.constants as constants
from flowparser.model import Flowlog

class Parser:
    def __init__(self, path: str, schema=constants.FLOW_LOG_SCHEMA_DEFAULT):
        self.path = path
        self.source_ip_index: dict[str, list[Flowlog]] = collections.defaultdict(list)
        self.destination_ip_index: dict[str, list[Flowlog]] = collections.defaultdict(list)
        self.source_and_destination_ip_index: dict[tuple[str, str], list[Flowlog]] = collections.defaultdict(list)
        self.connection_counts: dict[tuple[str, str, str, str, str], int] = collections.defaultdict(int)
        self.schema: list[str] = schema

    def deserialize(self) -> None:
        row_idx = 0
        try:
            with open(self.path, 'r') as file:
                for line in file:
                    fields = line.strip().split()
                    flowlog_data = {}
                    for i, field in enumerate(self.schema):
                        if fields[i] != '-':
                            flowlog_data[field] = fields[i]

                    flowlog = Flowlog(row_idx=row_idx, schema=self.schema, **flowlog_data)
                    self.source_ip_index[getattr(flowlog, "srcaddr")].append(flowlog)
                    self.destination_ip_index[getattr(flowlog, "dstaddr")].append(flowlog)
                    self.source_and_destination_ip_index[(getattr(flowlog, "srcaddr"), getattr(flowlog, "dstaddr"))].append(flowlog)
                    self.connection_counts[(getattr(flowlog, "srcaddr"), getattr(flowlog, "dstaddr"), getattr(flowlog, "srcport"), getattr(flowlog, "dstport"), getattr(flowlog, "protocol"))] += 1

                    row_idx += 1
        except FileNotFoundError:
            print(f"File not found: {self.path}")
        except IndexError:
            print(f"Schema mismatch in line. Please check the schema and ensure it matches the log format.")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def search_by_source_ip(self, src_ip: str) -> list[Flowlog]:
        try:
            return self.source_ip_index.get(src_ip, [])
        except Exception as e:
            print(f"An error occurred during search_by_source_ip: {e}")
            return []
    
    def search_by_destination_ip(self, dst_ip: str) -> list[Flowlog]:
        try:
            return self.destination_ip_index.get(dst_ip, [])
        except Exception as e:
            print(f"An error occurred during search_by_destination_ip: {e}")
            return []

    def search_by_source_and_destination_ip(self, src_ip: str, dst_ip: str) -> list[Flowlog]:
        try:
            return self.source_and_destination_ip_index.get((src_ip, dst_ip), [])
        except Exception as e:
            print(f"An error occurred during search_by_source_and_destination_ip: {e}")
            return []
    
    def get_connection_count(self, src_ip: str, src_port: str, dst_ip: str, dst_port: str, transport_protocol: str) -> int:
        return self.connection_counts.get((src_ip, dst_ip, src_port, dst_port, transport_protocol), 0)
    