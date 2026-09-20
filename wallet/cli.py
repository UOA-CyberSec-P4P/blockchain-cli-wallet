"""Command-line entry point for the assignment wallet."""
import argparse
import json
import os

from .wallet import Wallet


def main() -> None:
    parser = argparse.ArgumentParser(prog='wallet')
    node = os.getenv('BLOCKCHAIN_URL', 'http://0.0.0.0:5000')
    merchant = os.getenv('MERCHANT_URL', 'http://127.0.0.1:5001')
    merchant_address = os.getenv('MERCHANT_ADDRESS', 'university')
    primary_address = os.getenv('STUDENT_PRIMARY_ADDRESS', 'UoA1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    secondary_address = os.getenv('STUDENT_SECONDARY_ADDRESS', 'UoA2UgUM6TMnw8EjwgObaQ1fQ5RHfgj3ENQ')
    primary_private_key = os.getenv('STUDENT_PRIMARY_PRIVATE_KEY')
    secondary_private_key = os.getenv('STUDENT_SECONDARY_PRIVATE_KEY')

    commands = parser.add_subparsers(dest='command', required=True)

    commands.add_parser('list', help="List all wallets and their balances.")

    balance = commands.add_parser('balance', help="Get the balance of the given wallet.")
    balance.add_argument('--wallet', choices=('primary', 'secondary'), help="The wallet to query.")

    send = commands.add_parser('send', help="Send grade points from one of your wallets to a recipient.")
    send.add_argument('--wallet', choices=('primary', 'secondary'), help="The wallet to send from.")
    send.add_argument('recipient', help=f"The address of the recipient wallet, or {merchant_address} to send to the university grading office.")
    send.add_argument('amount', type=int, help="The amount of grade points to send, as a positive integer.")

    redeem = commands.add_parser('redeem', help="Redeem a reward from the university grading office.")
    redeem.add_argument('transaction_id', help="The ID of the transaction that sent the grade points to the university.")
    redeem.add_argument('piece', type=int, choices=(1, 2), help="The reward piece to redeem (#1 or #2).")

    # buy = commands.add_parser('buy', help="A convenience method that transacts with the merchant, mines a block with the transaction, and redeems a reward piece.")
    # buy.add_argument('--wallet', choices=('primary', 'secondary'), help="The wallet to send from.")
    # buy.add_argument('piece', type=int, choices=(1, 2), help="The reward piece to redeem (1 or 2).")

    # template = commands.add_parser('template', help="Get a template for a block with the given parent and transactions.")
    # template.add_argument('--parent')
    # template_group = template.add_mutually_exclusive_group()
    # template_group.add_argument('--transaction', action='append')
    # template_group.add_argument('--empty', action='store_true')

    mine = commands.add_parser('mine', help="Mine a block with the given parent and transactions.")
    mine.add_argument('--parent', help="The hash of the block to be the parent of the new block. If not provided, the new block will be mined on top of the current canonical tip of the blockchain.")
    mine_group = mine.add_mutually_exclusive_group()
    mine_group.add_argument('--transaction', action='append', help="The ID of a transaction to include in the block.")
    mine_group.add_argument('--empty', action='store_true', help="Create an empty block.")

    args = parser.parse_args()
    wallets = {
        'primary': Wallet(primary_address, primary_private_key, node, merchant),
        'secondary': Wallet(secondary_address, secondary_private_key, node, merchant),
    }
    try:
        if args.command == 'list':
            result = {
                'wallets': [
                    {'name': name, 'address': wallet.address, 'balance': wallet.balance()}
                    for name, wallet in wallets.items()
                ],
            }
        elif args.command == 'balance':
            wallet = wallets[args.wallet]
            result = {'name': args.wallet, 'address': wallet.address, 'balance': wallet.balance(), 'utxos': wallet.utxos()}
        elif args.command == 'send':
            result = wallets[args.wallet].send(args.recipient, args.amount)
        elif args.command == 'redeem':
            result = wallets['primary'].redeem(args.transaction_id, args.piece)
        # elif args.command == 'buy':
        #     result = wallets[args.wallet].buy(args.piece)
        # elif args.command == 'template':
        #     result = wallets['primary'].get_template(args.parent, [] if args.empty else args.transaction)
        elif args.command == 'mine':
            result = wallets['primary'].mine(args.parent, [] if args.empty else args.transaction)
        else:
            raise ValueError(f'unknown command: {args.command}')
    except RuntimeError as error:
        parser.exit(1, f'wallet: {error}\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
