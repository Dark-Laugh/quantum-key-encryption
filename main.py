"""
@author rpthi
"""
import qka


class KeyAgreement:
    """Simulates the communication channel between Alice and Bob for the key agreement"""
    def __init__(self):
        # Creates users Alice and Bob with all respective information to prepare for first exchange
        self.Alice = qka.QKAuser()
        self.Bob = qka.QKAuser()
        # Is the first exchange of information. Alice and Bob send each other lists with decoys
        # and they check if what the other measures is correct. This is the optimal way to determine
        # eavesdropping.
        self.Bob.securityCheck1(self.Alice.receiveA(self.Bob.get_receiveA_data()))
        self.Alice.securityCheck1(self.Bob.receiveA(self.Alice.get_receiveA_data()))
        # Is the second exchange. After determining that there has been no eavesdropping,
        # Alice and Bob then complete the key agreement and create a shared key
        self.pswd_alice = self.Alice.receiveB(self.Bob.get_receiveB_data())
        self.pswd_bob = self.Bob.receiveB(self.Alice.get_receiveB_data())
        # self.pswd_ls = [self.pswd_alice, self.pswd_bob]

    def print_results(self):
        print("Alice's key: " + self.pswd_alice)
        print("Bob's key: " + self.pswd_bob)


qka = KeyAgreement()
qka.print_results()
