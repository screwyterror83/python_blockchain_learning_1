#!"D:\Program Files\CodeLanguage\Python\Python37\python.exe"

# Init empty blockchain list

open_transactions = []
owner = '48962189089408906504189460489'
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions':[]
}
blockchain = [genesis_block]

def get_last_blockchain_value():
    """ Return the last value of the current blockchain. """
    if len(blockchain) < 1:
        print('Blockchain is empty')
        return None
    return blockchain[-1]

# This function accepts 2 arguments.
# Required one (transaction_amount) and optional one (last_transaction)
def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Append a new value as well as the last blockchain value to the blockchain.
    
    Arguments:
        :sender: The sender of the transaction
        :recipient: The recipient of transaction
        :amount: amount of transaction sent by sender(default = 1.0)
    """
    
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
        }
    open_transactions.append(transaction)
    
    
    
def mine_block():
    last_block = blockchain[-1]
    hashed_block = ''
    for keys in last_block:
        value = last_block[keys]
        hashed_block = hashed_block + str(value)
    print(hashed_block)
        
    block = {
        'previous_hash': 'XYZ',
        'index': len(blockchain),
        'transactions':open_transactions
        }
    blockchain.append(block)

    
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

def chain_validate():
    # block_index = 0
    is_valid = True
    for block_index in range(len(blockchain)):
        if block_index == 0:
            continue
        elif blockchain[block_index][0] == blockchain[block_index - 1]:
            is_valid = True
        else:
            is_valid = False
    
    return is_valid

waiting_for_input = True

while waiting_for_input:
    print('Please choose: ')
    print('1: Add a new transaction value.')
    print('2: Mine a new block.')
    print('3: Output the blockchain blocks.')
    print('h: Manipulate the chain.')
    print('q: Quit~!')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        # Tuple unpacking
        recipient, amount = tx_data
        add_transaction(recipient, amount=amount)
        print(open_transactions)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
        print('Done!')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = [2]
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Invalid input, please choose again. ')
    # if not chain_validate():
    #     print_blockchain_elements()
    #     print('Invalid Blockchain~!')
    #     break
else: 
    print('User left~!')   
    

print('Done!')


