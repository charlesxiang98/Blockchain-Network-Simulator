import numpy as np
from queue import PriorityQueue as PQ
                     ##Need To Check##
##################################################################
x = 0.5## parameter of transaction comming rate                 ##
y = 1  ## parameter of mining speed                             ##
z = 100## loop of simulation                                    ##
w = 0.05# parameter of information transaction time among node  ##
node_number = 30    ## number of node                           ##
##################################################################

class TransRecord:
    __tCount = 1
    __tTime = 0.0000000000000001
    object_type = 'T'
    new = 0

    def __init__(self):
        self.id = TransRecord.__tCount # id of the transaction, auto number
        self.node = np.random.randint(node_number) + 1 # Node that the transaction is created
        self.time = TransRecord.__tTime # create time of the transaction record
        self.__wait_time = np.random.exponential(x)
        TransRecord.__tCount +=1 
        TransRecord.__tTime += self.__wait_time
        # self.next_arrival = TransRecord.__tTime # next transaction arrival time
        TransRecord.new = self

    def avg_trans_time(self): # here we use this because the first transaction comes at time 0
        if self.id==1:
            return 0
        else:
            return self.time/(self.id-1)

class Mining:
    __mCount = 1
    __k = np.random.exponential(y)
    __mTime = __k
    object_type = 'M'
    new = 0

    def __init__(self):
        self.id = Mining.__mCount # id of the mining, auto number
        self.node = np.random.randint(node_number) + 1 # Node that the transaction is created
        self.time = Mining.__mTime
        self.__time_spent = np.random.exponential(y)
        Mining.__mCount += 1
        Mining.__mTime += self.__time_spent
        # self.next_mining = Mining.__mTime # next mining happen
        Mining.new = self

    def avg_mining_time(self):
        return self.time/self.id

class Block:
    __bCount = 0
    object_type = 'B'
    new = 0

    def __init__(self,time, p_id, pool, miner):
        self.id = Block.__bCount # corresponding to the id of mining(one mining generates one block)
        self.time = time
        self.p_id = p_id # the id of the previous block
        self.trans_pool = pool
        self.node = miner
        Block.__bCount += 1
        Block.new = self

    def position(self): # the position of the block in its own chain, starts with 1
        count = 1
        i = self.p_id
        while i != 0:
            count += 1
            i = Block_chain_dic[i].p_id
        return count

    def print_chain(self): # print (the id of) blocks in the chain from the first to the given block
        chain = [self.id]
        i = self.p_id
        while i != 0:
            chain.append(i)
            i = Block_chain_dic[i].p_id
        chain.reverse()
        return chain


class Node:
    __nCount = 0
    object_type = 'N'

    def __init__(self):
        self.id = Node.__nCount + 1
        self.trans_pool = {}
        self.main_chain = Block_chain_dic[0]
        self.fork = []
        self.node_time = 0
        Node.__nCount += 1
        self.pq = PQ()
        self.pq.put((0,Block_chain_dic[0])) #in simulation, we use pq.put() twice, so here initialize twice
        self.pq.put((0,Block_chain_dic[0]))

    def print_main_chain(self):
        return self.main_chain.print_chain()

    def print_fork_chain(self):
        for i in self.fork:
            return i.print_chain()
        
    def pq_insert(self,data):
        t = data.time # update node time
        a = 0
        if data.node != self.id:   #judge if the node who boradcast data is the node receive the data. If same, a is 0. otherwise, a will be exponential distribution
            a = np.random.randint(1,4)*w
        time = t + a
        self.pq.put((float(time),data))   #other node will add transaction Record or block into its transaction pool or chain

    def pq_trigger(self):
        x = self.pq.get()
        a = x[1] #acquire the object B or T. Mining will generate Block, so a's type may be B
        if a.object_type=='B':
            self.mining_broadcast(x)
        elif a.object_type=='T':
            self.transaction_broadcast(x)
        self.node_time = x[0] #update the node time to the moment that an new event is triggered. 

    def transaction_broadcast(self,x): # x is pq.get() in pq_trigger
        trans = x[1] #acquire object that is transaction reocrd
        self.trans_pool[trans.id] = [trans,x[0]]#connect the transaction in priority queue with transaction pool of nodes. address trans x[1] ahead, time x[0] behind

    def mining_broadcast(self,x):  #when nodes receive new block broadcasted by other nodes, deal with it.
        k = x[1] #k is block object_type
        if self.main_chain.id == k.p_id: # for node that calculating the same chain, this new block previous id is the main chain id, just extend the main chain through adding the new block in the main chain
            self.update_main_chain(k)
            self.clean_fork()
            self.update_pool(k)
        else: # for node that do a different chain
            if self.main_chain.position() < k.position(): # two chain, if the current main chain is shorter
                self.update_main_chain(k)
                self.clean_fork()
                self.update_pool(k)
            elif self.main_chain.position() == k.position(): # if the chain has the same length
                self.add_fork(k)
            # if a node has longer chain, do nothing
        
    # functions used in a mining broadcast
    def update_main_chain(self, block): # input should be an object in class 'Block'
        self.main_chain = block

    def clean_fork(self):
        self.fork = []

    def update_pool(self,block): # remove pending transactions. input should be an object in class 'Block'
        s_pool = self.trans_pool.keys() # current pool
        n_pool = block.trans_pool.keys() # trans that packed by the new block
        p_pool = self.main_chain.trans_pool.keys() # trans that packed by the pervious block
        newpool = {}
        for i in s_pool:
            if (i not in n_pool) and (i not in p_pool):
                newpool[i] = self.trans_pool[i]
        self.trans_pool = newpool

    def add_fork(self, block): # input should be an object in class 'Block'
        self.fork.append(block)

def broadcast(data):  #block pacakging, calculate performance measures and call two methods
    global p
    if data.object_type == 'M':
        miner = Node_dic[data.node] #the node is doing mining who is miner
        # print('---------',data.node)
        m = miner.main_chain
        p = miner.trans_pool
        Block_chain_dic[data.id] = Block(data.time,m.id,p,miner.id) #block pacakging, data is m=Mining(), data.id is Mining.id, m.id is 0,beacuase  Node.main_chain=Block_chain_dic[0],data.time is same with the m.time in pq.put((float(m.time),m)) that is the time that the node finish mining,data.node is same with miner.id
        # print('test is: ',Block_chain_dic[data.id],data.time,m.id,p,miner.id )
        # print('++++++', p)
        n=len(p)
        # print('~~~~~',n)
        sum = 0
        for i in p:
            # print('every trans in pool', p[i])
            sum=sum+p[i][1]
        print('average number of transactions in the transaction pool',(n*data.time-sum)/data.time)#performance measures:Average Number of Customers
        if n!=0:
            print('average response time is',(n*data.time-sum)/n)
            print('average waiting time is',(n*data.time-sum)/n)#because each transaction in the pool will depart in the same time, the formula is same with response time
        print('throughput is',n/data.time)
        data = Block_chain_dic[data.id] #one mining--one block, one one relationship

    for i in range(1,node_number+1): #call two methods
        Node_dic[i].pq_trigger()
        Node_dic[i].pq_insert(data)

              
def simulation(n):
    pq = PQ()
    t = TransRecord()
    m = Mining()
    pq.put((float(t.time),t))
    pq.put((float(m.time),m))
    for i in range(n):
        x = pq.get()  #it will delete the information that is pq.put() above.  pq.get() has time order
        a = x[1]  #a is  TransRecord or Mining (that is the parameter in pq.put() above )
        print(x) #print every TransRecord or Mining
        broadcast(a)
        if a.object_type=='M':
            m = Mining()   #pq.get() will delete once, here it will use pq.put again
            pq.put((float(m.time),m))
        else:
            t = TransRecord()  #pq.get() will delete once, here it will use pq.put again
            pq.put((float(t.time),t))

    return pq

##################################################################
# Initiate the system
Block_chain_dic ={0:Block(0,0,{0:'Hidden 0th block'},'Satoshi')} #dictionary, time,p_id,pool,miner
Node_dic ={}

for i in range(node_number): # create nodes
    k = i+1
    Node_dic[k] = Node()

simulation(z)
rNode = np.random.randint(node_number)+1
print('Node',rNode,'\n', Node_dic[rNode].print_main_chain())
# print('Node',rNode,'\n', Node_dic[rNode].print_fork_chain())
##################################################################
print('program finished!  ~~~~~~~~~~')










        



        
