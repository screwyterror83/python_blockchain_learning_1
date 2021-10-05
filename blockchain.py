from functools import reduce
from utility.hash_util import hash_string_256, hash_block

import json
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
                
                # Use json.load method to convert json format string back to python objects
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    # Using transaction class object to store transaction instead of using dictionary
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    # converted_tx = [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions'] ]
                    updated_block = Block(block['index'], block['previous_hash'],converted_tx, block['proof'], block['timestamp'])
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
                    # Also use Transaction class object to store updated_transactions
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'],tx['amount'])
                    # updated_transaction = OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
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
                savable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions] ,block_el.proof, block_el.timestamp) for block_el in self.__chain]]
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
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof


    # Check whether participant has balance in his(her) account to send
    def get_balance(self):
        """
        get each participants balance from the blockchain
        
        """
        if self.wallet_pub_key == None:
            return None
        # complex(nested) list comprehension
        participant = self.wallet_pub_key
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        
        # use reduce and lambda function to calculate the amount to a single output(total amount)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        
        ### Replaced below code with reduce/lambda function above.
        # amount_sent = 0
        # for tx in tx_sender:
        #     if len(tx) > 0:
        #         amount_sent += tx[0]
        
        
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        
        
        return amount_received - amount_sent

    # return the last block on the chain
    def get_last_blockchain_value(self):
        """ Return the last value of the current blockchain. """
        if len(self.__chain) < 1:
            print('Blockchain is empty')
            return None
        return self.__chain[-1]





    # add transaction to block
    def add_transaction(self, recipient, sender, signature, amount):
        """
        Append a new value as well as the last blockchain value to the blockchain.
        
        Arguments:
            :sender: The sender of the transaction
            :recipient: The recipient of transaction
            :amount: amount of transaction sent by sender(default = 1.0)
        """
        
        # Use class object to replace the OrderedDict
        
        # Using OrderedDict to make sure the dictionary is in order, OrderedDict takes in list, and in the list use tuple for key-value pair.
        # transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
        
        # transaction = {
        #     'sender': sender,
        #     'recipient': recipient,
        #     'amount': amount
        #     }
        if self.wallet_pub_key == None:
            print('Got no wallet ? ')
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.validate_transaction(transaction, self.get_balance):    
            self.__open_transactions.append(transaction)
            self.save_data()
            for node in self.__peer_nodes:
                url = f'http://{node}/broadcast-transaction'
            return True
        print('Invalid Transaction')
        return False    
        
    # mine(verify) the block on blockchain  

    def mine_block(self):
        """Create a new block and add open transaction to it with mining reward.

        Returns:
            bool: if True, reward is provided, if false, mining not successful.
        """        
        if self.wallet_pub_key == None:
            return None
        # fetch the currently last blocks of the blockchain
        last_block = self.__chain[-1]
        # Hash the last block 
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        #How miner gets reward by mining
        # Use class object to replace the orderedDict
        reward_transaction = Transaction('MINING', self.wallet_pub_key,' ', MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)

        
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
        # use boolean to reset open_transaction
        return block

    def add_peer_node(self,node):
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
