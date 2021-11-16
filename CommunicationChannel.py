import qka


class QKAChannel:
    """Simulates the communication channel between alice and bob for the key agreement"""
    def __init__(self, security_property):
        # Creates users alice and bob with all respective information to prepare for first exchange
        self.alice = qka.QKAuser('alice', security_property)
        self.bob = qka.QKAuser('bob', security_property)
        # Is the first exchange of information. alice and bob send each other lists with decoys
        # and they check if what the other measures is correct. This is the optimal way to determine
        # eavesdropping.
        self.bob.securityCheck1(self.alice.receiveA(self.bob.get_receiveA_data()))
        self.alice.securityCheck1(self.bob.receiveA(self.alice.get_receiveA_data()))
        # Is the second exchange. After determining that there has been no eavesdropping,
        # alice and bob then complete the key agreement and create a shared key
        self.pwd_alice = self.alice.receiveB(self.bob.get_receiveB_data())
        self.pwd_bob = self.bob.receiveB(self.alice.get_receiveB_data())
        # self.pwd_ls = [self.pwd_alice, self.pwd_bob]

    def print_results(self):
        print("alice's key: " + self.pwd_alice)
        print("bob's key: " + self.pwd_bob)


# qka = QKAChannel()
# qka.print_results()
