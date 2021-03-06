from uuid import uuid4
from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet

class Node:
    
    def __init__(self):
        # self.wallet.public_key = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

        
        
    def get_transaction_value(self):
        """
        Returns the input of the user as a float. (new transaction amount)
        """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        """
        Let user choose what they want to do:
        1: add transaction
        2: Mine a new block.
        3: Output the blockchain blocks.
        4: Check transaction validity.
        h: Manipulate blockchain data
        q: Quit
        
        """
        user_input = input('Your Choice: ')
        return user_input


    def print_blockchain_elements(self):
        """Print all blocks of the blockchain."""
        # Output the blockchain list to the console
        print('\n')
        print('Outputting Blocks')
        print('\n')
        print('-' * 20)
        print('\n')
        for block in self.blockchain.chain:
            print(block)
        else:
            print('-' * 20)

    
    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print('Please choose: ')
            print('1: Add a new transaction value.')
            print('2: Mine a new block.')
            print('3: Output the blockchain blocks.')
            print('4: Check transaction validity.')
            print('5: Create wallet.')
            print('6: Load wallet.')
            print('7: Save keys')
            print('q: Quit~!')
            
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                signature = self.wallet.sigh_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print('Transaction added ~!')
                else:
                    print('Transaction failed ~!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining failed, Got no wallet? ')
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid ~!')
                else:
                    print('Invalid transaction found')
            elif user_choice == '5':
                print('-' * 20)
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
                print('-' * 20)
                print('Wallet Created, Enjoy~!')
                print('-' * 20)
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Invalid input, please choose again. ')
            if not Verification.validate_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Invalid Blockchain~!')
                break
            # print('Total amount sent.')
            print('Banlance of {}: {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance()))
        else: 
            print('User left~!')   
            

        print('Done!')
        
if __name__ == '__main__':
    node = Node()
    node.listen_for_input()

