"""
@author: rpthi
"""
from qiskit import QuantumCircuit, execute, Aer
import numpy as np
import random
import json


class Sender:
    # utility class for measurement of
    def __init__(self, x, bits, bases):
        self.length = len(bases)
        self.send_bits = bits
        self.send_bases = bases
  
    def make_send_circuits(self):
        circuits = []
        for i in range(self.length):
            circuit = QuantumCircuit(1,1)
            if self.send_bases[i] == 0:
                if self.send_bits[i] == 0:
                    pass
                else:
                    circuit.x(0)
            else:
                if self.send_bits[i] == 0:
                    circuit.h(0)
                else:
                    circuit.x(0)
                    circuit.h(0)
            circuits.append(circuit)
        return circuits


class Receiver:
    def __init__(self, x, bases):        
        self.length = len(bases)
        self.receiveBases = bases 
        
    def make_receive_circuits(self):
        recCircuits = []
        for i in range(self.length):
            recCircuit = QuantumCircuit(1,1)
            if (self.receiveBases[i] == 1):
                recCircuit.h(0)
                recCircuit.measure(0,0)
            else:
                recCircuit.measure(0,0)
            recCircuits.append(recCircuit)
        return recCircuits


class Contributor(Sender, Receiver):
    def are_hashes_equal(K, H):
        """turn K into H_ into binary because H is in binary"""
        H_ = Contributor.decimalToBinary(hash(K))
        return Contributor.check_hash(H_, H)
    
    def remove_decoy(self, ls, pos):
        """returns list without decoys"""
        new_ls = []
        for i in range(len(ls)):
            if i in pos:
                pass
            else:
                new_ls.append(ls[i])
        return new_ls
     
    def check_hash(hash1, hash2):
        temp = (hash1 == hash2)
        for i in range(temp):
            if temp[i] == False:
                print('Fails')



    def check_decoy(self, dS, dC):
        """returns if there has been eavesdropping (False), no eavesdropping (True)"""
        for i in dS:
            if i != self.bi_dS[i]:
                return False
        for i in dC:
            if i != self.bi_dC[i]:
                return False
        else:
            return True
   
    def findDecoy(ls, pos):
        """returns list of decoys found within given list"""
        decoys = []
        for i in range(len(ls)):
            for j in range(len(pos)):
                if pos[j] == i:
                    decoys.append(ls[i])
        return decoys  
    
    def receive_decoy(self, ls, pos, ba):
        """returns decoy measurements"""
        len_ls = len(ls)
        decoys = Contributor.findDecoy(ls, pos)
        recCircuits = Contributor.create_rec_circuits(len_ls, ba)
        return self.measure(len_ls, decoys, recCircuits)
    
    def measure(self, length, sendCircuits, recCircuits):
        mes = []
        for i in range(len(sendCircuits)):
            sendAndReceive = sendCircuits[i] + recCircuits[i]
            result = execute(sendAndReceive, self.backend, shots=1, memory=True).result()
            measured_bit = int(result.get_memory()[0])
            mes.append(measured_bit)
        return mes
        
    def measure2(self, ls, ba):
        sendCircuits = ls[:]
        recCircuits = Contributor.create_rec_circuits(len(ba), ba)
        mes = []
        for i in range(len(sendCircuits)):
            sendAndReceive = sendCircuits[i] + recCircuits[i]
            result = execute(sendAndReceive, self.backend, shots=1, memory=True).result()
            measured_bit = int(result.get_memory()[0])
            mes.append(measured_bit)
        return mes
    
    def create_rec_circuits(len_ls, ba):
        """just creates measurement gates"""
        receiver = Receiver(len_ls, ba)
        return receiver.make_receive_circuits()
        
    def insertDecoys(dls, ls, pos):
        x = ls[:]
        for i in range(len(ls)):
            for j in range(len(pos)):
                if pos[j] == i:
                    x[i:i] = [dls[j]]
        return x
    
    
    def getDecoyPos(len_dls, len_ls):
        pos = random.sample(range(len_ls), len_dls)
        pos.sort()
        return pos
    
    def send(length, bits, bases):
        return Sender(length, bits, bases)
         
    
    def cbits(n):
        rng = np.random.default_rng()
        return rng.integers(0,1,n, endpoint=True)
    
    def decimalToBinary(n):
        if n > 0:
            return bin(n)[2:]
        else:
            return bin(n)[3:]

    def unshuffle(self, shuffled_ls, seed):
        n = len(shuffled_ls)
        p = [i for i in range(1, n + 1)]
        random.Random(seed).shuffle(p)
        zipped_ls = list(zip(shuffled_ls, p))
        zipped_ls.sort(key=lambda x: x[1])
        return [a for (a, b) in zipped_ls]
    
    def __init__(self,security_property, backend, bi_dS, bi_dC, Kkey):
        if security_property == None:
            self.bi_dS = bi_dS
            self.bi_dC = bi_dC
            self.Kkey = Kkey
            self.backend = backend
        
        else:
            self.security_property = security_property
            self.backend = backend
            n = 24
            """NEW DEFINITION
            s: shuffled list, s_: encoded shuffled list, s__: encoded shuffled list with decoys"""
            """what is different about the new definition is that now the shuffled list
            is encoded, and not that the encoded list is shuffled"""
            
            self.K = Contributor.cbits(n)
            self.seed = np.random.randint(1,101)
        
            Ktemp = (''.join(map(str, self.K)))
            self.Kkey = int(Ktemp)
            
            random.Random(self.seed).shuffle(self.K)
            S = self.K[:]
            self.K = self.unshuffle(self.K, self.seed)
        
            H_ = Contributor.decimalToBinary(hash(Ktemp))
            H = [int(x) for x in str(H_)]
            
            self.bS = list(Contributor.cbits(len(S)))
            self.bH = list(Contributor.cbits(len(H)))
          
            sentS = Contributor.send(len(S), S, self.bS)
            sentH = Contributor.send(len(H), H, self.bH)  
            
            S_ = sentS.make_send_circuits()
            C = sentH.make_send_circuits()
            
            """now for the decoys"""
            len_dS = int(len(S_) * security_property)
            len_dC = int(len(C) * security_property)
        
            self.bi_dS = Contributor.cbits(len_dS)
            self.ba_dS = Contributor.cbits(len_dS)
        
            self.bi_dC = Contributor.cbits(len_dC)
            self.ba_dC = Contributor.cbits(len_dC)
        
            sentdS = Contributor.send(len_dS, self.bi_dS, self.ba_dS)
            sentdC = Contributor.send(len_dC, self.bi_dC, self.ba_dC)
        
            dS = sentdS.make_send_circuits()
            dC = sentdC.make_send_circuits()
            """now we have decoys, time to input them into lists, remembering positions
            first get positions"""
            self.pos_dS = Contributor.getDecoyPos(len_dS, len(S_))
            self.pos_dC = Contributor.getDecoyPos(len_dC, len(C))
            """now, insert"""   
            self.S__ = Contributor.insertDecoys(dS, S_, self.pos_dS)
            self.C_ = Contributor.insertDecoys(dC, C, self.pos_dC)


class Eavesdropper(Sender):
    def __init__(self, backend):
        self.backend = backend
        
    def intercept_and_resend(self, ls):
        newls = self.measure(ls, Contributor.cbits(len(ls)))
        sender = Sender(None, newls, Contributor.cbits(len(ls)))
        return sender.make_send_circuits()
        
    def measure(self, ls, ba):
        sendCircuits = ls[:]
        recCircuits = Contributor.create_rec_circuits(len(ba), ba)
        mes = []
        for i in range(len(sendCircuits)):
            sendAndReceive = sendCircuits[i] + recCircuits[i]
            result = execute(sendAndReceive, self.backend, shots=1, memory=True).result()
            measured_bit = int(result.get_memory()[0])
            mes.append(measured_bit)
        return mes    
     

class QKAuser():
    S_ = ''
    C = ''
    strownKkey = ''
    strbi_dS = ''
    strbi_dC = ''
    seed = ''
    bS = ''
    bH = ''

    def __init__(self, name, security_property):
        self.backend = Aer.get_backend('qasm_simulator')
        self.name = name
        self.security_property = security_property
    
    def get_receiveA_data(self):
        self.strownKkey, self.strbi_dS, self.strbi_dC, strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC, self.seed, self.bS, self.bH = GiveData(self.security_property, self.backend)
        ls = [strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC]
        print('------------------------------------------------------------------------------------')
        print(self.name + ' created key, 2 lists which are derivations of key, decoys, and respective bases')
        print('key: ' + self.strownKkey)
        print('decoys for list: ' + self.strbi_dS)
        print('decoys for hashed list: ' + self.strbi_dC)
        print('To conclude this step, the decoys are put into their respective lists'
              ' and the lists are encrypted as explained in the report')
        print('------------------------------------------------------------------------------------')
        return ls
   
    def receiveA(self, ls):
        strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2 = ls[0],ls[1],ls[2],ls[3],ls[4],ls[5]
        dS, dC, S_, C = ReceiveData1(strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2, self.backend)
        self.S_ = S_
        self.C = C
        return dS, dC
    
    def get_receiveB_data(self):
        ls = [self.seed, self.bS, self.bH]
        return ls
    
    def receiveB(self, ls):
        print('------------------------------------------------------------------------------------')
        print(self.name + ' has received the required data and is making their new, shared key')
        print('------------------------------------------------------------------------------------')
        return makeKey(self.strownKkey, self.S_, self.C, ls[0], ls[1], ls[2], self.backend)
  
    def securityCheck1(self, ls):
        print('------------------------------------------------------------------------------------')
        print(self.name + ' is checking to see if eavesdropping occurred')
        securityCheck(ls[0], self.strbi_dS)
        securityCheck(ls[1], self.strbi_dC)
        print('------------------------------------------------------------------------------------')
'''    
def mainTest():
    security_property = 0.5
    backend = Aer.get_backend('qasm_simulator')
    #GiveData
    #Alice
    strownKkey, strbi_dS, strbi_dC, strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC, seed, bS, bH = GiveData(security_property, backend)
    #Bob
    strownKkey2, strbi_dS2, strbi_dC2, strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2, seed2, bS2, bH2 = GiveData(security_property, backend)
    ---------------------
    #Intercepted(strS__, strC_, backend)
    
    #ReceiveData1
    #Alice
    AdS, AdC, AS_, AC = ReceiveData1(strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2, backend)
    #Bob
    BdS, BdC, BS_, BC = ReceiveData1(strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC, backend)
    #Alice
    securityCheck(BdS, strbi_dS)
    securityCheck(BdC, strbi_dC)
    makeKey(strownKkey, AS_, AC, seed2, bS2, bH2, backend)    
    #Bob
    securityCheck(AdS, strbi_dS2)
    securityCheck(AdC, strbi_dC2)
    makeKey(strownKkey2, BS_, BC, seed, bS, bH, backend)       
'''


def GiveData(strsecurity_property, backend):
    security_property = float(strsecurity_property)
    user = Contributor(security_property, backend, None, None, None)
    #Send the bits across the channel
    strS__ = []
    strC_ = []   
    for i in range(len(user.S__)):
        strS__.append(user.S__[i].qasm())     
    for i in range(len(user.C_)):
        strC_.append(user.C_[i].qasm()) 
        
    json_strS__ = json.dumps(strS__)
    json_strC_ = json.dumps(strC_)
    
    return str(user.Kkey), str(user.bi_dS), str(user.bi_dC), json_strS__, json_strC_, str(user.pos_dS), str(user.pos_dC), str(user.ba_dS), str(user.ba_dC),str(user.seed), str(user.bS), str(user.bH)
    """
    print(user.Kkey)
    print(user.bi_dS)
    print(user.bi_dC)
    print(json_strS__)
    print(json_strC_)
    print(user.pos_dS)
    print(user.pos_dC)
    print(user.ba_dS)
    print(user.ba_dC)
    print(user.seed)
    print(user.bS)
    print(user.bH) 
    """


def strToLs(stringls):
    ls = stringls[1:len(stringls)-1]
    ls = ls.replace(" ","")    
    ls = [int(x) for x in ls]
    return ls


def Intercepted(json_strS__, json_strC_, backend):
    Eve = Eavesdropper(backend)
     
    strS__ = json.loads(json_strS__)
    strC_ = json.loads(json_strC_)
    
    S__ = []
    C_ = []
    
    for i in range(len(strS__)):
        S__.append(QuantumCircuit().from_qasm_str(strS__[i])) 
    
    for i in range(len(strC_)):
        C_.append(QuantumCircuit().from_qasm_str(strC_[i]))     
          
    # Oh no! Eve has intercepted the messages!
    e1 = Eve.intercept_and_resend(S__)
    e2 = Eve.intercept_and_resend(C_)
    strS__2 = []
    strC_2 = []   
    for i in range(len(e1)):
        strS__2.append(e1[i].qasm())     
    for i in range(len(e2)):
        strC_2.append(e2[i].qasm())  
    
    json_strS__2 = json.dumps(strS__2)
    json_strC_2 = json.dumps(strC_2)    
    
    print(json_strS__2)
    print(json_strC_2)

def ReceiveData1(json_strS__, json_strC_, strpos_dS, strpos_dC, strba_dS, strba_dC, backend):
#returns decoy bits + lists without decoys
    user = Contributor(None, backend, None, None, None)
    strS__ = json.loads(json_strS__)
    strC_ = json.loads(json_strC_)        
    S__ = []
    C_ = []   
    
    for i in range(len(strS__)):
        S__.append(QuantumCircuit().from_qasm_str(strS__[i])) 
    
    for i in range(len(strC_)):
        C_.append(QuantumCircuit().from_qasm_str(strC_[i])) 
    
    pos_dS = json.loads(strpos_dS)
    pos_dC = json.loads(strpos_dC)
    ba_dS = strToLs(strba_dS)
    ba_dC = strToLs(strba_dC)

    dS = user.receive_decoy(S__, pos_dS, ba_dS)
    dC = user.receive_decoy(C_, pos_dC, ba_dC)
    
    S_ = user.remove_decoy(S__, pos_dS)
    C = user.remove_decoy(C_, pos_dC)
    
    strS_ = []
    strC = []   
    for i in range(len(S_)):
        strS_.append(S_[i].qasm())     
    for i in range(len(C)):
        strC.append(C[i].qasm()) 
           
    json_S_ = json.dumps(strS_)
    json_C = json.dumps(strC)
    
    return str(dS), str(dC), json_S_, json_C

def securityCheck(d, bi_d):
    if json.loads(d) == strToLs(bi_d):
        pass
    else:
        print("eavesdropping!")


#ReceiveData2 ~ MakeKey
def makeKey(ownKkey, jS_, jC, seed, bS, bH, backend):
    ownKkey = int(ownKkey)
    sS_ = json.loads(jS_)
    sC = json.loads(jC)
    S_ = []
    C = []
    for i in range(len(sS_)):
        S_.append(QuantumCircuit().from_qasm_str(sS_[i])) 
    for i in range(len(sC)):
        C.append(QuantumCircuit().from_qasm_str(sC[i])) 
    seed = int(seed)
    bS = json.loads(bS)
    bH = json.loads(bH)
    user = Contributor(None, backend, None, None, ownKkey)
    S = user.measure2(S_, bS)
    K = (''.join(map(str, user.unshuffle(S, seed))))
    securityCheck2(Contributor.decimalToBinary(hash(K)), (''.join(map(str, user.measure2(C, bH)))))
    K=int(K)
    return str(K^user.Kkey)


def securityCheck2(H_,H):
    if H_ == H:
        pass
    else:
        print('Fails')
   

def mainTest():
    '''
    security_property = 0.5
    backend = Aer.get_backend('qasm_simulator')
    #GiveData
    #Alice
    strownKkey, strbi_dS, strbi_dC, strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC, seed, bS, bH = GiveData(security_property, backend)
    #Bob
    strownKkey2, strbi_dS2, strbi_dC2, strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2, seed2, bS2, bH2 = GiveData(security_property, backend)
    
    #Intercepted(strS__, strC_, backend)
    
    #ReceiveData1
    #Alice
    AdS, AdC, AS_, AC = ReceiveData1(strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2, backend)
    #Bob
    BdS, BdC, BS_, BC = ReceiveData1(strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC, backend)
    #Alice
    securityCheck(BdS, strbi_dS)
    securityCheck(BdC, strbi_dC)
    makeKey(strownKkey, AS_, AC, seed2, bS2, bH2, backend)    
    #Bob
    securityCheck(AdS, strbi_dS2)
    securityCheck(AdC, strbi_dC2)
    makeKey(strownKkey2, BS_, BC, seed, bS, bH, backend)
    
    
    def get_receiveA_data(self):
        security_property = 0.5
        self.strownKkey, self.strbi_dS, self.strbi_dC, strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC, self.seed, self.bS, self.bH = GiveData(security_property, self.backend)
        return strS__, strC_, pos_dS, pos_dC, ba_dS, ba_dC
   
    def receiveA(self, strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2):
       dS, dC, S_, C = ReceiveData1(strS__2, strC_2, pos_dS2, pos_dC2, ba_dS2, ba_dC2, self.backend)
       self.S_ = S_
       self.C = C
       return dS, dC
    
    def get_receiveB_data(self):
        return self.seed, self.bS, self.bH
    
    def receiveB(self, seed2, bS2, bH2):
        return makeKey(self.strownKkey, self.S_, self.C, seed2, bS2, bH2, self.backend)
  
    def securityCheck1(self, strbi_dS2, strbi_dC2):
        securityCheck(strbi_dS2, self.strbi_dS)
        securityCheck(strbi_dC2, self.strbi_dC)
    '''
    Alice = QKAuser()
    Bob = QKAuser()
    Bob.securityCheck1(Alice.receiveA(Bob.get_receiveA_data()))
    Alice.securityCheck1(Bob.receiveA(Alice.get_receiveA_data()))
    key_alice = Alice.receiveB(Bob.get_receiveB_data())
    key_bob = Bob.receiveB(Alice.get_receiveB_data())
    print(key_alice)
    print(key_bob)


def main():
    backend = Aer.get_backend('qasm_simulator')
    while True:
        inArgs = input().split('#')
        if len(inArgs) == 1:  # GiveData
            security_property = inArgs[0]
            Kkey, bi_dS, bi_dC, S__, C_, pos_dS, pos_dC, ba_dS, ba_dC, seed, bS, bH = GiveData(security_property, backend)
            print(Kkey)
            print(bi_dS)
            print(bi_dC)
            print(S__)
            print(C_)
            print(pos_dS)
            print(pos_dC)
            print(ba_dS)
            print(ba_dC)
            print(seed)
            print(bS)
            print(bH)
        
        if len(inArgs) == 4: #SecurityCheck
            dS = inArgs[0]
            dC = inArgs[1]
            bi_dS = inArgs[2]
            bi_dC = inArgs[3]
            securityCheck(dS, bi_dS)
            securityCheck(dC, bi_dC)
                    
        if len(inArgs) == 6: #ReceiveData1
            S__ = inArgs[0]
            C_ = inArgs[1]
            pos_dS = inArgs[2]
            pos_dC = inArgs[3]
            ba_dS = inArgs[4]
            ba_dC = inArgs[5]
            dS, dC, S_, C = ReceiveData1(S__, C_, pos_dS, pos_dC, ba_dS, ba_dC, backend)
            print(dS)
            print(dC)
            print(S_)
            print(C)
              
        #have to add a "" at the end to make this work
        if len(inArgs) == 7: #makeKey(ALICEKkey, ALICES_, ALICEAC, BOBseed, BOBbS, BOBbH, backend)    
            Kkey = inArgs[0]
            S_ = inArgs[1]
            C = inArgs[2]
            seed = inArgs[3]
            bS = inArgs[4]
            bH = inArgs[5]
            makeKey(Kkey, S_, C, seed, bS, bH, backend)
        
        if len(inArgs) == 2: #Eve intercepts
            S__ = inArgs[0]
            C_ = inArgs[1]
            Intercepted(S__, C_, backend)
            
 
#mainTest()
#main()


    
