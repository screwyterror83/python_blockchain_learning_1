from functools import reduce
from utility.hash_util import hash_block

import json
import requests
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet


MINING_REWARD = 10


class Blockchain:
    def __init__(self, wallet_pub_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        # Init empty blockchain list
        self.chain = [genesis_block]
        # Unhandled transactions
        self.__open_transactions = []
        self.wallet_pub_key = wallet_pub_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            # Using pickle to read previously stored pickle data
            # with open('blockchain.p', mode='rb') as f:
            #     file_content = pickle.loads(f.read())
            #     blockchain = file_content['chain']
            #     open_transactions = file_content['open_transactions']

            # using json lib, load stored json file format
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()

                # Use json.load method to convert
                # json format string back to python objects
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    # Using transaction class object to store
                    # transaction instead of using dictionary
                    converted_tx = [Transaction(
                        tx['sender'],
                        tx['recipient'],
                        tx['signature'],
                        tx['amount'])
                        for tx in block['transactions']]
                    updated_block = Block(
                        block['index'],
                        block['previous_hash'],
                        converted_tx,
                        block['proof'],
                        block['timestamp'])
                    # Replacing dictionary by class object
                    # updated_block = {
                    #     'previous_hash':block['previous_hash'],
                    #     'index':block['index'],
                    #     'proof':block['proof'],
                    #     'transactions':converted_tx
                    # }
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    # Also use Transaction class object
                    # to store updated_transactions
                    updated_transaction = Transaction(
                        tx['sender'],
                        tx['recipient'],
                        tx['signature'],
                        tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup~!')

    # Save blockchain data to local file (1)
    def save_data(self):
        try:
            # Using Pickle to store to local file
            # with open('blockchain.p', mode='wb') as f:
            #     save_data = {
            #         'chain': blockchain,
            #         'open_transactions':open_transactions
            #     }
            #     f.write(pickle.dumps(save_data))

            # using json lib, write to json format
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                # Convert a class object into dict, and then use json dump
                savable_chain = [
                    block.__dict__ for block in
                    [
                        Block(
                            block_el.index,
                            block_el.previous_hash,
                            [
                                tx.__dict__ for tx in block_el.transactions
                                ],
                            block_el.proof, block_el.timestamp
                            )
                        for block_el in self.__chain
                        ]
                    ]
                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(savable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))

            # use regular file write to store content(no longer working)
                # f.write(str(blockchain))
                # f.write('\n')
                # f.write(str(open_transactions))
        except IOError:
            print('Saving Failed ~!')

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not (
            Verification.valid_proof(
                self.__open_transactions,
                last_hash,
                proof)):
            proof += 1
        return proof

    # Check whether participant has balance in his(her) account to send
    def get_balance(self, sender=None):
        """
        get each participants balance from the blockchain

        """
        if sender is None:
            if self.wallet_pub_key is None:
                return None
        # complex(nested) list comprehension
            participant = self.wallet_pub_key
        else:
            participant = sender
        tx_sender = [
            [tx.amount for tx in block.transactions if
                tx.sender == participant]
            for block in self.__chain]
        open_tx_sender = [
            tx.amount for tx in self.__open_transactions if
            tx.sender == participant]
        tx_sender.append(open_tx_sender)

        # use reduce and lambda function to calculate
        # the amount to a single output(total amount)
        amount_sent = reduce(
            lambda tx_sum,
            tx_amt: tx_sum + sum(tx_amt)
            if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        # Replaced below code with reduce/lambda function above.
        # amount_sent = 0
        # for tx in tx_sender:
        #     if len(tx) > 0:
        #         amount_sent += tx[0]

        tx_recipient = [[tx.amount for tx in block.transactions
                        if tx.recipient ==
                        participant] for block in self.__chain]

        amount_received = reduce
        (
            lambda tx_sum, tx_amt:
                tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                tx_recipient, 0
        )

        return amount_received - amount_sent

    # return the last block on the chain
    def get_last_blockchain_value(self):
        """ Return the last value of the current blockchain. """
        if len(self.__chain) < 1:
            print('Blockchain is empty')
            return None
        return self.__chain[-1]

    # add transaction to block

    def add_transaction(self,
                        recipient,
                        sender,
                        signature,
                        amount,
                        is_receiving=False):
        """
        Append a new value as well as the last
        blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the transaction
            :recipient: The recipient of transaction
            :amount: amount of transaction sent by sender(default = 1.0)
        """
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.validate_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = f'http://{node}/broadcast-transaction'
                    try:
                        response = requests.post(url, json={
                                                'sender': sender,
                                                'recipient': recipient,
                                                'signature': signature,
                                                'amount': amount})
                        if response.status_code == 400 or \
                                response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        print('Invalid Transaction')
        return False

    # mine(verify) the block on blockchain

    def mine_block(self):
        """Create a new block and add open transaction to it with mining reward.

        Returns:
            bool: if True, reward is provided, if false, mining not successful.
        """
        if self.wallet_pub_key is None:
            return None
        # fetch the currently last blocks of the blockchain
        last_block = self.__chain[-1]
        # Hash the last block
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # How miner gets reward by mining
        # Use class object to replace the orderedDict
        reward_transaction = Transaction(
            'MINING', self.wallet_pub_key, ' ', MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)

        # Replacing genesis block dictionary using class object
        # block = {
        #     'previous_hash': hashed_block,
        #     'index': len(blockchain),
        #     'transactions':copied_transactions,
        #     'proof': proof
        #     }
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        for node in self.__peer_nodes:
            url = f'http://{node}/broadcast-block'
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [
                tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        transactions = [Transaction(
            tx['sender'],
            tx['recipient'],
            tx['signature'],
            tx['amount']) for
                        tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1] == block['previous_hash'])
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(
            block['index'],
            block['previous_hash'],
            transactions,
            block['proof'],
            block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and \
                    opentx.recipient == itx['recipient'] and \
                        opentx.amount == itx['amount'] and \
                        opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = f'http://{node}/chain'
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(
                    block['index'],
                    block['previous_hash'],
                    [Transaction(
                        tx['sender'],
                        tx['recipient'],
                        tx['signature'],
                        tx['amount']) for tx in block['transactions']],
                    block['proof'],
                    block['timestamp']) for block in node_chain]
                node_chain_len = len(node_chain)
                local_chain_len = len(winner_chain)
                if node_chain_len > local_chain_len and\
                        Verification.validate_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    def add_peer_node(self, node):
        """Add a new node to the peer node set.

        Args:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """Remove a node to the peer node set.

        Args:
            :node: The node URL which should be removed.
        """
        self.__peer_nodes.discard(node)

    def get_peer_nodes(self):
        """Return a list of all connected nodes
        """
        return list(self.__peer_nodes)
