"""A deliberately small HTTP wallet; private keys are not used or transmitted."""


from .block import Block
from .transaction import Transaction
from .utxo import TxInput, TxOutput
from .proof_of_work import ProofOfWork
from .request import get, post


class Wallet:
    """Construct unsigned UTXO transactions and submit them to a blockchain API."""

    def __init__(
        self,
        address: str,
        private_key: str | None = None,
        node_url: str = 'http://0.0.0.0:5000',
        merchant_url: str = 'http://127.0.0.1:5001',
    ):
        if not isinstance(address, str) or not address:
            raise ValueError('address must be a non-empty string')
        self.address = address
        # Retained for the later Kali-provided wallet material.  Signatures are
        # intentionally outside this assignment's simplified transaction model.
        self.private_key = private_key
        self.node_url = node_url.rstrip('/')
        self.merchant_url = merchant_url.rstrip('/')

    def balance(self) -> int:
        return get(f'/utxos/{self.address}', self.node_url)['balance']

    def utxos(self) -> list[dict]:
        return get(f'/utxos/{self.address}', self.node_url)['utxos']

    def create_transaction(self, recipient: str, amount: int) -> dict:
        """Select canonical UTXOs and construct a payment plus change output."""
        if not isinstance(recipient, str) or not recipient:
            raise ValueError('recipient must be a non-empty string')
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError('amount must be a positive integer')

        selected = []
        total = 0
        for utxo in self.utxos():
            selected.append(utxo)
            total += utxo['amount']
            if total >= amount:
                break
        if total < amount:
            raise RuntimeError('insufficient confirmed funds')

        outputs = [{'amount': amount, 'address': recipient}]
        if total > amount:
            outputs.append({'amount': total - amount, 'address': self.address})
        return {
            'inputs': [
                {
                    'txid': utxo['txid'],
                    'output_index': utxo['output_index'],
                    # 'signature': 'unsigned',
                }
                for utxo in selected
            ],
            'outputs': outputs,
        }

    def send(self, recipient: str, amount: int) -> dict:
        """Create and place an unsigned transaction in the node's inbox."""
        return post('/transactions', self.create_transaction(recipient, amount), self.node_url)

    def redeem(self, transaction_id: str, piece: int) -> dict:
        """Ask the merchant to deliver a reward piece for a confirmed payment."""
        if piece not in (1, 2):
            raise ValueError('piece must be 1 or 2')
        return post('/redeem', {
            'transaction_id': transaction_id,
            'piece': piece,
        }, self.node_url)

    def buy(self, piece: int) -> dict:
        """Pay the merchant 15 grade points, mine the payment, then collect a reward piece."""
        payment = self.send('merchant', 15)
        mined = self.mine(transaction_ids=[payment['id']])
        delivery = self.redeem(payment['id'], piece)
        return {'payment': payment, 'block': mined, 'delivery': delivery}

    def get_template(self, parent_hash: str | None = None, transaction_ids: list[str] | None = None) -> dict:
        """Request a block template, optionally for a private branch parent."""
        payload = {}
        if parent_hash is not None:
            payload['parent_hash'] = parent_hash
        if transaction_ids is not None:
            pending = {item['id']: item for item in get('/transactions/pending', self.node_url)['transactions']}
            try:
                payload['transactions'] = [pending[transaction_id] for transaction_id in transaction_ids]
            except KeyError as error:
                raise RuntimeError(f'unknown pending transaction: {error.args[0]}') from error
        return post('/mining/template', payload, self.node_url)

    def mine(self, parent_hash: str | None = None, transaction_ids: list[str] | None = None) -> dict:
        """Mine a requested template locally, then submit the resulting block."""
        template = self.get_template(parent_hash, transaction_ids)
        block_payload = template['block']
        block = _block_from_api(block_payload)
        ProofOfWork(template['difficulty']).mine(block)
        submission = {
            **block_payload,
            'nonce': block.nonce,
            'hash': block.hash,
        }
        return post('/blocks', submission, self.node_url)


def _block_from_api(payload: dict) -> Block:
    transactions = []
    for item in payload['transactions']:
        transactions.append(Transaction(
            inputs=[TxInput(**tx_input) for tx_input in item['inputs']],
            outputs=[
                TxOutput(amount=output['amount'], addrress=output['address'])
                for output in item['outputs']
            ],
        ))
    return Block(
        height=payload['height'],
        timestamp=payload['timestamp'],
        transactions=transactions,
        previous_hash=payload['previous_hash'],
        nonce=payload['nonce'],
    )
