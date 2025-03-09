import heapq

class PriorityQueue():

    def __init__(self):
        self.PQ = []

    def isEmpty(self):
        return len(self.PQ) == 0
    
    def size(self):
        return len(self.PQ)
    
    def top(self):
        if self.isEmpty() == False:
            return self.PQ[0]
        else:
            raise IndexError('The queue is empty.')

    def enqueue(self , priority , process):
        heapq.heappush(self.PQ , [priority , process.PID , process]) # enqueue a list. list[0] is the priority of the process. list[1] is the object of the process. the priority queue will sort based on list[0]
        
    def dequeue(self):

        if not self.isEmpty():
            return heapq.heappop(self.PQ)
        else:
            raise IndexError('The queue is empty.')
        
    def printPQ(self):
        tempData = []

        while not self.isEmpty():
            temp = self.dequeue()
            print(vars(temp[1]))
            tempData.append(temp) 

        for data in tempData:
            self.enqueue(data[0] , data[1])

