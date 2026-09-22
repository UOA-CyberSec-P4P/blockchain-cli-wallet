from .block import Block

class ProofOfWork:
    """
    Simple PoW implementation for the blockchain.
    """
    def __init__(self, difficulty):
        self.difficulty = difficulty

    def mine(self, block: Block):
        """
        Hashcash: mines a block by finding a nonce that has x leading zeros (where x = difficulty).
        """
        block.nonce = 0
        while True:
            if self.is_valid(block):
                return block
            block.nonce += 1

    def is_valid(self, block: Block) -> bool:
        """
        Validates a block. Returns true if the block's hash has x leading zeros (where x = difficulty),
        r false otherwise.
        """
        return block.hash.startswith('0' * self.difficulty)

    # Keep the original name available to callers of the starter code.
    valid = is_valid
