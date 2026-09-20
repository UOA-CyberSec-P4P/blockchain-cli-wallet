"""
Dataclass for a blockchain transaction.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
from .utxo import TxInput, TxOutput

@dataclass
class Transaction:
    """
    A transaction. Contains a list of inputs and outputs.
    """
    inputs: list[TxInput]
    outputs: list[TxOutput]

    def to_dict(self) -> dict:
        """Return a stable, JSON-compatible transaction representation."""
        return asdict(self)

    @property
    def id(self) -> str:
        """A deterministic identifier for this unsigned educational transaction."""
        encoded = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(encoded.encode()).hexdigest()
