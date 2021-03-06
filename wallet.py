from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii

class Wallet:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id
        
    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key


    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            
            try:
                with open(f'wallet-{self.node_id}.txt', mode='w') as f:
                    f.write('Your Public Key: \n')
                    f.write(self.public_key)
                    f.write('\n')
                    f.write('Your Private Key: \n')
                    f.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Saving wallet failed...!')
                return False
            
    def load_keys(self):
        try:
            with open(f'wallet-{self.node_id}.txt', mode='r') as f:
                keys = f.readlines()
                public_key = keys[1][:-1]
                private_key = keys[3]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except (IOError, IndexError):
            print('Loading wallet failed...!')
            return False
    
    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), 
                binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))
        
    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        hash_payload = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(hash_payload)
        return binascii.hexlify(signature).decode('ascii')
    
    @staticmethod
    def verify_transaction(transaction):
        """Verify signature of a transaction

        Args:
            transaction: transaction in block that needs to be verified.
        """        
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        hash_payload = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
        return verifier.verify(hash_payload, binascii.unhexlify(transaction.signature))
