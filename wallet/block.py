"""
Dataclass for a blockchain block.
"""
from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json

@dataclass
class Block:
    """
    A block in the blockchain. Has a block header and a hash function for the header.
    """
    height: int
    timestamp: float
    transactions: list
    previous_hash: str | None
    nonce: int

    def to_dict(self) -> dict:
        """Return a JSON-compatible representation of this block."""
        return {
            'height': self.height,
            'timestamp': self.timestamp,
            'transactions': _json_value(self.transactions),
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
        }

    def header(self) -> str:
        """
        Returns a JSON string of the block header.
        """
        return json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))

    @property
    def hash(self) -> str:
        """
        A SHA-256 hash of the block header.
        """
        return hashlib.sha256(self.header().encode()).hexdigest()


def _json_value(value):
    """Convert the small transaction dataclasses to deterministic JSON values."""
    if hasattr(value, 'to_dict') and callable(value.to_dict):
        return _json_value(value.to_dict())
    if is_dataclass(value):
        return _json_value(asdict(value))
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value
