#!"D:\Program Files\CodeLanguage\Python\Python37\python.exe"

from functools import reduce
from hashlib import sha256
from json import dumps
from collections import OrderedDict

# Init empty blockchain list

MINING_REWARD = 10

open_transactions = []
owner = 'Alpha'
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions':[],
    'proof': 100
}

blockchain = [genesis_block]

# using a set to create and manage list of participants of the blockchain
participants = {'Alpha'} 


def hash_block(block):
    # Use hashlib sha265 and json package to hash the block as string, and transcode to utf-8 and output to readable charactors instead of binary numbers
    return sha256(dumps(block, sort_keys=True).encode()).hexdigest()


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = sha256(guess).hexdigest()
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


# Check whether participant has balance in his(her) account to send
def get_balance(participant):
    """
    get each participants balance from the blockchain
    
    
    """
    
    # complex(nested) list comprehension
    # identify the block in the blockchain, where within the block, the transaction sender is function input argument 'participant'
    
    tx_sender = [[tx['amount']for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    
    # use reduce and lambda function to calculate the amount to a single output(total amount)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    
    ### Replaced below code with reduce/lambda function above.
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0:
    #         amount_sent += tx[0]
    
    
    tx_recipient = [[tx['amount']for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    
    
    return amount_received - amount_sent

# return the last block on the chain
def get_last_blockchain_value():
    """ Return the last value of the current blockchain. """
    if len(blockchain) < 1:
        print('Blockchain is empty')
        return None
    return blockchain[-1]


def validate_transaction(transaction):
    """
    To validate whether sender of the transaction has enough balance to afford the transaction
    """
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']
    


# add transaction to block
def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Append a new value as well as the last blockchain value to the blockchain.
    
    Arguments:
        :sender: The sender of the transaction
        :recipient: The recipient of transaction
        :amount: amount of transaction sent by sender(default = 1.0)
    """
    # Using OrderedDict to make sure the dictionary is in order, OrderedDict takes in list, and in the list use tuple for key-value pair.
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    #     }
    
    if validate_transaction(transaction):    
        open_transactions.append(transaction)
    
        # add participant of each transaction to participants set
        participants.add(sender)
        participants.add(recipient)
        return True
    return False    
    
# mine(verify) the block on blockchain  

def mine_block():
    # fetch the currently last blocks of the blockchain
    last_block = blockchain[-1]
    # Hash the last block 
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    #How miner gets reward by mining
    # Using OrderedDict instead of regular dict
    reward_transaction = ([('sender','MINING'),('recipient',owner), ('amount', MINING_REWARD)])
    
    # reward_transaction = {
    #     'sender':'MINING',
    #     'recipient':owner,
    #     'amount': MINING_REWARD
    # }
    
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
        
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions':copied_transactions,
        'proof': proof
        }
    blockchain.append(block)
    # use boolean to reset open_transaction
    return True

    
def get_transaction_value():
    """
    Returns the input of the user as a float. (new transaction amount)
    """
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return tx_recipient, tx_amount

def get_user_choice():
    """
    Let user choose what they want to do:
    1: add transaction
    2: Output the blockchain blocks
    h: Manipulate blockchain data
    q: Quit
    
    """
    user_input = input('Your Choice: ')
    return user_input


def print_blockchain_elements():
    # Output the blockchain list to the console
    for block in blockchain:
        print("Outputting Block")
        print(block)

# Verify chain to avoid any malicious manipulation 
def validate_chain():
    """
    validate current blockchain return true if is valid.
    """
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid ~!')
            return False
    return True

# Helper function to validate all open transactions in list
def verify_transactions():
    return all([validate_transaction(tx) for tx in open_transactions])

waiting_for_input = True

while waiting_for_input:
    print('Please choose: ')
    print('1: Add a new transaction value.')
    print('2: Mine a new block.')
    print('3: Output the blockchain blocks.')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('h: Manipulate the chain.')
    print('q: Quit~!')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        # Tuple unpacking
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Transaction added ~!')
        else:
            print('Transaction failed ~!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
    elif user_choice == '3':
        print_blockchain_elements()
        print('Done!')
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions:
            print('All transactions are valid ~!')
        else:
            print('Invalid transaction found')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] =  {
                'previous_hash': '',
                'index': 0,
                'transactions':[{
                    'sender': 'Chris',
                    'recipient': 'Max',
                    'amount': 100.0
                }]
}
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Invalid input, please choose again. ')
    if not validate_chain():
        print_blockchain_elements()
        print('Invalid Blockchain~!')
        break
    print('Total amount sent.')
    print('Banlance of {}: {:6.2f}'.format('Alpha', get_balance('Alpha')))
else: 
    print('User left~!')   
    

print('Done!')


