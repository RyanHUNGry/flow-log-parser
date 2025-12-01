import parser.constants as constants

class Flowlog:
    def __init__(self, row_idx, schema=constants.FLOW_LOG_SCHEMA_DEFAULT, **kwargs):
        self.schema = schema
        self.row_idx = row_idx
        for field in schema:
            setattr(self, field, kwargs.get(field))
    
    def to_pretty(self, indent: int = 2) -> str:
        lines = ["{"]
        pad = " " * indent
        lines.append(f"{pad}row_idx: {self.row_idx!r}")
        for field in self.schema:
            value = getattr(self, field, None)
            lines.append(f"{pad}{field}: {value!r}")
        lines.append("}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_pretty()
    
    def __repr__(self) -> str:
        return self.to_pretty()
    