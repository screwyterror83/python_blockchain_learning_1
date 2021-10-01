from utility.hash_util import hash_string_256, hash_block

class Verification:
    
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        # Create a string with all the hash inputs
        guess = (str([tx.to_ordered_dict for tx in transactions]) + str(last_hash) + str(proof)).encode()
        # Hash the string
        # IMPORTANT: This is NOT the same hash as will be stored in the previous hash
        guess_hash = hash_string_256(guess)
        # Only a hash(based on the above inputs) which starts with 2 '0' will be accepted.
        # This condision is defined anyway you'd like, the more identical digits required, the longer it will take to proof.
        # print(guess_hash)
        return guess_hash[0:2] == '00'

    

    # Verify chain to avoid any malicious manipulation
    @classmethod
    def validate_chain(cls, blockchain):
        """
        validate current blockchain return true if is valid.
        """
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid ~!')
                return False
        return True

    @staticmethod
    def validate_transaction(transaction, get_balance):
        """
        To validate whether sender of the transaction has enough balance to afford the transaction
        """
        sender_balance = get_balance()
        return sender_balance >= transaction.amount

    # Helper function to validate all open transactions in list
    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        return all([cls.validate_transaction(tx, get_balance) for tx in open_transactions])






    