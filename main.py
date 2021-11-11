"""
@author rpthi
"""
import qka


class KeyAgreement():
    def __init__(self):
        self.Alice = qka.QKAuser()
        self.Bob = qka.QKAuser()
        self.Bob.securityCheck1(self.Alice.receiveA(self.Bob.get_receiveA_data()))
        self.Alice.securityCheck1(self.Bob.receiveA(self.Alice.get_receiveA_data()))
        self.pswd_alice = self.Alice.receiveB(self.Bob.get_receiveB_data())
        self.pswd_bob = self.Bob.receiveB(self.Alice.get_receiveB_data())
        # self.pswd_ls = [self.pswd_alice, self.pswd_bob]

    def print_results(self):
        print("Alice's password: " + self.pswd_alice)
        print("Bob's password: " + self.pswd_bob)


qka = KeyAgreement()
qka.print_results()
