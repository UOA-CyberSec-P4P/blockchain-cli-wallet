"""
Dataclasses for transaction inputs and outputs.

UTXO (unspent transaction output): "represents a certain amount of cryptocurrency that has been
authorized by a sender and is available to be spent by a recipient. The utilization of UTXOs in
transaction processes is a key feature of many cryptocurrencies, but it primarily characterizes
those implementing the UTXO model" ~ Wikipedia.
"""

from dataclasses import dataclass

@dataclass
class TxInput:
    """
    A transaction input. Contains a reference to a previous transaction output.
    """
    txid: str
    output_index: int
    # signature: str


@dataclass
class TxOutput:
    """
    A transaction output. Contains an amount and the recipient address.
    """
    amount: int
    addrress: str