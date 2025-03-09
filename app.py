from PriorityQueue import *
from Process import *
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def Read_file():

    """
    File format:
        0 0 1 CPU{R[1],50,F[1]}
        1 5 1 CPU{20} IO{30} CPU{20,R[2],30,F[2],10}
    """

    processes = [] # list of processes
    Dict = {} # dict to store the info of the process
    with open("input.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip() # remove '\n'
            Data = line.split(' ')
            
            Dict = {}
            Dict['pid'] = int(Data[0])
            Dict['arrivalTime'] = int(Data[1])
            Dict['priority'] = int(Data[2])
            Dict['bursts'] = [] # [ [cpu] [io] [cpu] [io] ...... [cpu] ]
            Dict['total_cpu_time'] = 0
            Dict['total_io_time'] = 0
            Dict['burst_time'] = []
            
            bursts = Data[3:]
            isCPU = 1
            for burst in bursts:
                temp = burst.split('{')[1].split('}')[0].split(',') # temp = [20 , R[1] , 30 , F[1]] if cpu. temp = [40] if io

                if isCPU == 1: # temp = [20 , R[1] , 30 , F[1]]
                    cpu = [int(item) if item.isdigit() else item for item in temp] # casting the numbers in temp into integers
                    
                    # calculate cpu time
                    Dict['total_cpu_time'] += sum(item for item in cpu if isinstance(item , int))
                    Dict['burst_time'].append(cpu)
                    Dict['bursts'].append(cpu)

                else: # temp = [40]
                    io = [int(item) for item in temp] # casting the numbers in temp into integers (items are always numbers here)
                    
                    # calculate io time
                    Dict['total_io_time'] += sum(io)
                    Dict['burst_time'].append(sum(io))
                    Dict['bursts'].append(io)

                isCPU = isCPU ^ 1 # change form 1 to 0 or form 0 to 1

            process = Process(
                PID=Dict['pid'],
                Arrival_time=Dict['arrivalTime'],
                total_cpu_time=Dict['total_cpu_time'],
                total_IO_time=Dict['total_io_time'],
                Priority=Dict['priority'],
                bursts=Dict['bursts'],
                burstsTime=Dict['burst_time'],
                state="NEW",  # initial state
                enter_cpu_time = [],
                leaving_cpu_time = [],
                finish_time=-1,
                ready_queue_time=0,
                done=False,
                currentBurst=0,
                currentCPUBurst=0,
                Fixed_Arrival_Time=Dict['arrivalTime'],
                total_waiting_resource_time=0
            )
            
            processes.append(process)


    return processes

def calculateQuantum(processes_list):

    tempList = []

    for process in processes_list:
        tempList.append(process.total_cpu_time)

    tempList.sort()
    index = len(tempList)*0.8

    index = int(index)

    return tempList[index]+1

def initializeDeadlock(allocation, request, available):

    with open("input.txt", "r") as file:
        lines = file.readlines()
        for line in lines: # n
            allocation.append({})
            request.append({})

        for line in lines:
            line = line.strip() # remove '\n'
            Data = line.split(' ')
            
            bursts = Data[3:]
            isCPU = 1
            # cpu io cpu io cpu
            for burst in bursts:
                if isCPU == 1: # temp = [20 , R[1] , 30 , F[1]]
                    cpu = burst.split('{')[1].split('}')[0].split(',') # temp = [20 , R[1] , 30 , F[1]]                    
                    for item in cpu:
                        if 'R' in item or 'F' in item: # then its R or F
                            number = int(item.split('[')[1].split(']')[0])  # Split and extract the number
                            for process in allocation:
                                process[number] = 0

                            for process in request:
                                process[number] = 0

                            available[number] = 1

                isCPU = isCPU ^ 1 # change form 1 to 0 or form 0 to 1

def deadlock_detection(allocation, available, request):

    #using Banker's Algorithm (Detection Algorithm)

    n = len(allocation)  # Number of processes
    m = len(available)  # Number of resources

    deadlocked_processes = []
    safe_seq = []
    
    work = available.copy() #copy the available to the work

    finish = []
    for x in range(n):
        finish.append(False) #initially all processes false

    for i in range(n): # FROM SLIDESSSS
        if all(allocation[i][j] == 0 for j in allocation[i]): #for one process, if all its allocation resources are zero => finish = true
            finish[i] = True    
            safe_seq.append(i+1)
    
    while True:
        progress = False  # Flag to check if any process completes in this iteration
        
        for i in range(n):
            if not finish[i] and all(request[i][j] <= work[j] for j in request[i]): # loop in all resources then check if request < work for ALL of them 115 < 236 (one by one)
                #if less => work += allocation for every resource

                for j in allocation[i]:
                    work[j]+=allocation[i][j]
                
                #work = [work[j] + allocation[i][j] for j in allocation[i]] # 1 + 2 || 1 + 3 || 5 + 6 (one by one)

                finish[i] = True #finished
                safe_seq.append(i+1) #finish => safe
                progress = True # i found process that can finish

        # If no progress (no one can finish) either stuck or all of them have finished => leave loop 
        if not progress:
            break

    for i in range(n):
        if not finish[i]: #processes made deadlock
            deadlocked_processes.append(i+1)

    if deadlocked_processes:
        return (1, deadlocked_processes)
    else:
        return (0, safe_seq)


def main():

    ready_queue = PriorityQueue()
    IOList = []
    cpu = [0 , -1] # [empty? , process]
    processes_list = Read_file()
    processes_list_copy = Read_file()

    allocation = [] # [ {},{},{}....n ] n processes in the list, each process is dict  # [ {1:0, 2:0, 3:0} {} {} ... ]
    request = [] # [ {},{},{}....n ] n processes in the list, each process is dict
    available = {} # number of resource: 0 or 1
    WaitingOnResource = {} # process.PID: [process object, [resources that its waiting for]]

    for process in processes_list:
        WaitingOnResource[process.PID] = (process, [])

    initializeDeadlock(allocation, request, available)

    quantum = calculateQuantum(processes_list)
    quantum = 5
    tempQuantum = quantum
    RRQueue = deque()


    # insert processes to the ready queue
    time_limit = 10000
    time=0
    while time <= time_limit:

        removeFlag=0
        # decrement each IO
        for process in IOList:
            if process.burstsTime[process.currentBurst] > 1:
                process.burstsTime[process.currentBurst]-=1
            else:
                process.burstsTime[process.currentBurst]-=1
                process.currentBurst+=1 # go to cpu
                process.currentCPUBurst=0
                IOList.remove(process)
                process.state="READY"
                ready_queue.enqueue(process.Priority, process)        
            

        if cpu[0] == 1: # there is process in cpu
            process = cpu[1]
            entercpuflag=1 
            while process.currentCPUBurst < len(process.burstsTime[process.currentBurst]) and not isinstance(process.burstsTime[process.currentBurst][process.currentCPUBurst], int): # the process is requesting or releasing a resource
                resource = process.burstsTime[process.currentBurst][process.currentCPUBurst] # resource = R[1] or F[1]
                number = int(resource.split('[')[1].split(']')[0])  # number = 1
                if 'R' in resource:
                    request[process.PID - 1][number] = 1
                    if available[number] == 1:
                        request[process.PID - 1][number] = 0
                        allocation[process.PID - 1][number] = 1
                        available[number] = 0
                    else:
                        print(process.PID, time)
                        cpu[0]=0
                        cpu[1]=-1
                        entercpuflag=0
                        process.state="WaitOnResource"
                        process.leaving_cpu_time.append(time)
                        WaitingOnResource[process.PID][1].append(number)
                        RRQueue.remove(process)
                else:
                    allocation[process.PID-1][number] = 0
                    available[number] = 1

                process.currentCPUBurst+=1

            if entercpuflag == 1:
                process.burstsTime[process.currentBurst][process.currentCPUBurst]-=1
                process.remaining_time-=1
                quantum-=1
                if process.remaining_time > 0:
                    if quantum > 0:
                        if process.burstsTime[process.currentBurst][process.currentCPUBurst] == 0: # we have finished the time burst in the cpu. [20,R[1],30,F[1],40] -> we have finished 20 or 30 or 40 
                            if process.currentCPUBurst+1 == len(process.burstsTime[process.currentBurst]): # if [20,R[1],30,F[1],40] and we are pointing on F[1], then check if there is a next IO burst (40)                          
                                if process.currentBurst+1 < len(process.burstsTime): # check if there is a next burst
                                    process.currentBurst+=1 # go to io
                                    process.currentCPUBurst=0
                                    cpu[0]=0
                                    cpu[1]=-1
                                    process.leaving_cpu_time.append(time)
                                    process.state="WAITING"
                                    IOList.append(process)
                                    RRQueue.remove(process)
                                    removeFlag=1
                                    # should i release all its allocated resources when it goes to IO???????????????????? -> no
                                else: # this is the last burst
                                    process.currentCPUBurst=0
                                    process.state = "TERMINATE"
                                    process.leaving_cpu_time.append(time)
                                    process.done = True
                                    cpu[0] = 0
                                    cpu[1] = -1
                                    RRQueue.remove(process)
                                    removeFlag=1
                                    for resourcenumber in allocation[process.PID-1]: # allocation[process.PID-1] is dict, 
                                        allocation[process.PID - 1][resourcenumber] = 0
                                        available[resourcenumber] = 1
                            else:
                                newFlag=1
                                process.currentCPUBurst+=1
                                while process.currentCPUBurst < len(process.burstsTime[process.currentBurst]) and not isinstance(process.burstsTime[process.currentBurst][process.currentCPUBurst], int): # the process is requesting or releasing a resource
                                    resource = process.burstsTime[process.currentBurst][process.currentCPUBurst] # resource = R[1] or F[1]
                                    number = int(resource.split('[')[1].split(']')[0])  # number = 1
                                    if 'R' in resource:
                                        request[process.PID - 1][number] = 1
                                        if available[number] == 1:
                                            request[process.PID - 1][number] = 0
                                            allocation[process.PID - 1][number] = 1
                                            available[number] = 0
                                        else:

                                            cpu[0]=0
                                            cpu[1]=-1
                                            process.state="WaitOnResource"
                                            process.leaving_cpu_time.append(time)
                                            WaitingOnResource[process.PID][1].append(number)
                                            RRQueue.remove(process)
                                            removeFlag=1
                                            newFlag=0
                                            break
                                    else:
                                        allocation[process.PID-1][number] = 0
                                        available[number] = 1
                                    
                                    process.currentCPUBurst+=1
                                if newFlag == 1:
                                    process.currentCPUBurst-=1    
                                    if process.currentCPUBurst+1 == len(process.burstsTime[process.currentBurst]): # if [20,R[1],30,R[2]] and we are pointing on R[2], then check if there is a next IO burst                         
                                        if process.currentBurst+1 < len(process.burstsTime): # check if there is a next burst
                                            process.currentBurst+=1 # go to io
                                            process.currentCPUBurst=0
                                            cpu[0]=0
                                            cpu[1]=-1
                                            process.leaving_cpu_time.append(time)
                                            process.state="WAITING"
                                            IOList.append(process)
                                            RRQueue.remove(process)
                                            removeFlag=1
                                            # should i release all its allocated resources when it goes to IO???????????????????? -> no
                                        else: # this is the last burst
                                            process.currentCPUBurst=0
                                            process.state = "TERMINATE"
                                            process.leaving_cpu_time.append(time)
                                            process.done = True
                                            cpu[0] = 0
                                            cpu[1] = -1
                                            RRQueue.remove(process)
                                            removeFlag=1
                                            for resourcenumber in allocation[process.PID-1]: # allocation[process.PID-1] is dict, 
                                                allocation[process.PID - 1][resourcenumber] = 0
                                                available[resourcenumber] = 1
                                    else:
                                        process.currentCPUBurst+=1

                    else: # quantum = 0
                        if process.burstsTime[process.currentBurst][process.currentCPUBurst] == 0: # we have finished the time burst in the cpu. [20,R[1],30,F[1],40] -> we have finished 20 or 30 or 40 
                            if process.currentCPUBurst+1 == len(process.burstsTime[process.currentBurst]): # if [20,R[1],30,F[1],40] and we are pointing on F[1], then check if there is a next IO burst (40)                          
                                if process.currentBurst+1 < len(process.burstsTime): # check if there is a next burst
                                    process.currentBurst+=1 # go to io
                                    process.currentCPUBurst=0
                                    cpu[0]=0
                                    cpu[1]=-1
                                    process.leaving_cpu_time.append(time)
                                    process.state="WAITING"
                                    IOList.append(process)
                                    RRQueue.remove(process)
                                    removeFlag=1
                                    # should i release all its allocated resources when it goes to IO???????????????????? -> no
                                else: # this is the last burst
                                    process.currentCPUBurst=0
                                    process.state = "TERMINATE"
                                    process.leaving_cpu_time.append(time)
                                    process.done = True
                                    cpu[0] = 0
                                    cpu[1] = -1
                                    RRQueue.remove(process)
                                    removeFlag=1
                                    for resourcenumber in allocation[process.PID-1]: # allocation[process.PID-1] is dict, 
                                        allocation[process.PID - 1][resourcenumber] = 0
                                        available[resourcenumber] = 1
                            else:
                                newFlag=1
                                process.currentCPUBurst+=1
                                while process.currentCPUBurst < len(process.burstsTime[process.currentBurst]) and not isinstance(process.burstsTime[process.currentBurst][process.currentCPUBurst], int): # the process is requesting or releasing a resource
                                    resource = process.burstsTime[process.currentBurst][process.currentCPUBurst] # resource = R[1] or F[1]
                                    number = int(resource.split('[')[1].split(']')[0])  # number = 1
                                    if 'R' in resource:
                                        request[process.PID - 1][number] = 1
                                        if available[number] == 1:
                                            request[process.PID - 1][number] = 0
                                            allocation[process.PID - 1][number] = 1
                                            available[number] = 0
                                        else:
                                            
                                            cpu[0]=0
                                            cpu[1]=-1
                                            process.state="WaitOnResource"
                                            process.leaving_cpu_time.append(time)
                                            WaitingOnResource[process.PID][1].append(number)
                                            RRQueue.remove(process)
                                            removeFlag=1
                                            newFlag=0
                                            break
                                    else:
                                        allocation[process.PID-1][number] = 0
                                        available[number] = 1
                                    
                                    process.currentCPUBurst+=1
                                if newFlag == 1:
                                    process.currentCPUBurst-=1
                                    if process.currentCPUBurst+1 == len(process.burstsTime[process.currentBurst]): # if [20,R[1],30,R[2]] and we are pointing on R[2], then check if there is a next IO burst                         
                                        if process.currentBurst+1 < len(process.burstsTime): # check if there is a next burst
                                            process.currentBurst+=1 # go to io
                                            process.currentCPUBurst=0
                                            cpu[0]=0
                                            cpu[1]=-1
                                            process.leaving_cpu_time.append(time)
                                            process.state="WAITING"
                                            IOList.append(process)
                                            RRQueue.remove(process)
                                            removeFlag=1
                                            # should i release all its allocated resources when it goes to IO???????????????????? -> no
                                        else: # this is the last burst
                                            process.currentCPUBurst=0
                                            process.state = "TERMINATE"
                                            process.leaving_cpu_time.append(time)
                                            process.done = True
                                            cpu[0] = 0
                                            cpu[1] = -1
                                            RRQueue.remove(process)
                                            removeFlag=1
                                            for resourcenumber in allocation[process.PID-1]: # allocation[process.PID-1] is dict, 
                                                allocation[process.PID - 1][resourcenumber] = 0
                                                available[resourcenumber] = 1
                                    else:
                                        process.currentCPUBurst+=1

                        cpu[0] = 0
                        cpu[1] = -1
                        if removeFlag == 0:
                            process.state = "READY"
                            process.leaving_cpu_time.append(time)
                            RRQueue.popleft()
                            RRQueue.append(process)
                else:
                    process.currentCPUBurst=0
                    process.state = "TERMINATE"
                    process.leaving_cpu_time.append(time)
                    process.done = True
                    cpu[0] = 0
                    cpu[1] = -1
                    RRQueue.remove(process)
                    for resourcenumber in allocation[process.PID-1]: # allocation[process.PID-1] is dict, 
                        allocation[process.PID - 1][resourcenumber] = 0
                        available[resourcenumber] = 1

        # loop to find the processes that their arrival time = time
        for process in processes_list:
            arival = process.Arrival_time
            if arival == time:
                process.state = "READY"
                ready_queue.enqueue(process.Priority, process)

        for process in WaitingOnResource.values():
            flag=0
            tempList = []
            if process[1]:
                process[0].total_waiting_resource_time+=1
            for resource in process[1]:
                if available[resource] == 1:
                    flag=1
                    process[1].remove(resource)
                    tempList.append(resource)
                    
            if not process[1] and flag == 1:
                if cpu[0] == 0:
                    time-=1
                    process[0].enter_cpu_time.append(time)
                    process[0].state = "RUNNING"
                    cpu[0] = 1 
                    cpu[1] = process[0]
                    quantum = tempQuantum
                    RRQueue.append(process[0])
                else:
                    ready_queue.enqueue(process[0].Priority, process[0])
                
                process[0].total_waiting_resource_time-=1
            else:
                for i in tempList:
                    process[1].append(i) 

        if ready_queue.isEmpty() == False and not RRQueue and cpu[0] == 0: # ready_queue is not empty and RRQueue is empty and cpu is empty
            process = ready_queue.top()[2] # process object
            priority = process.Priority
            RRQueue.append(process)
            ready_queue.dequeue()
            while ready_queue.isEmpty() == False:
                processTemp = ready_queue.top()[2] # process object
                priorityTemp = processTemp.Priority
                if priorityTemp == priority:
                    RRQueue.append(processTemp)
                    ready_queue.dequeue()
                else:
                    break

        # check if not empty
        if RRQueue:
            process = RRQueue[0]
            if cpu[0] == 0:
                process.enter_cpu_time.append(time)
                process.state = "RUNNING"
                cpu[0] = 1 
                cpu[1] = process
                quantum = tempQuantum
                
        deadlockResult = deadlock_detection(allocation, available, request)
        deadlockFlag = 0
        if deadlockResult[0] == 1:
            print(f"Deadlocked Processes at time {time}: {deadlockResult[1]}")
        while deadlockResult[0] == 1:
            deadlockFlag=1
            ListOfDeadlock = deadlockResult[1]
            processPID = ListOfDeadlock[0]
            ListOfDeadlock.remove(processPID)
            process = ""
            for Process in processes_list:
                if Process.PID == processPID:
                    process = Process
                    break
            
            process.state = "TERMINATE"
            process.done = True
            for resourcenumber in allocation[process.PID-1]: # allocation[process.PID-1] is dict, 
                allocation[process.PID - 1][resourcenumber] = 0
                available[resourcenumber] = 1
            if process.PID in WaitingOnResource:
                del WaitingOnResource[process.PID]
            if process in RRQueue:
                RRQueue.remove(process)
            if process in IOList:
                IOList.remove(process)
            
            tempList = []
            while ready_queue.isEmpty() == 0:
                processTemp = ready_queue.dequeue()
                if processTemp.PID != process.PID:
                    tempList.append(processTemp)
            
            for i in tempList:
                ready_queue.enqueue(i.priority, i)
            
            for i in processes_list_copy:
                if i.PID == process.PID:

                    process.Arrival_time += (time+1)
                    process.burstsTime = i.burstsTime
                    process.currentBurst = 0
                    process.currentCPUBurst = 0
                    process.total_cpu_time = i.total_cpu_time+(i.total_cpu_time-process.remaining_time)
                    process.total_IO_time = i.total_IO_time
                    process.remaining_time = i.remaining_time
                    process.done = i.done
                    process.bursts = i.bursts
                    process.state = i.state

                    print(f"Process {process.PID} has been terminated at time {time}. It will start over.")

                    break

            deadlockResult = deadlock_detection(allocation, available, request)

        if deadlockFlag == 1:
            print(f"Deadlock recovered successfully at time {time}.")

        time+=1

    print()
    sum_turnaround_time=0
    num_of_process = 0
    for process in processes_list:
        process.finish_time = process.leaving_cpu_time[len(process.leaving_cpu_time)-1]
        print(f"Turnaround Time for process {process.PID}: {process.calculate_turnaround_time()}")
        sum_turnaround_time+=process.calculate_turnaround_time()
        num_of_process+=1

    print(f"Average Turnaround TIme: {sum_turnaround_time/num_of_process}")
    print()

    for process in processes_list:
        if process.total_waiting_resource_time > 0:
            process.total_waiting_resource_time-=1

    sum_waiting_time=0
    for process in processes_list:
        print(f"Time waiting in ready queue for process {process.PID}: {process.calculate_waiting_time()}")
        sum_waiting_time+=process.calculate_waiting_time()
    print(f"Average waiting time: {sum_waiting_time/num_of_process}")

     # Define 10 distinct colors
    colors = [
        'skyblue', 'lightgreen', 'salmon', 'gold', 'violet', 
        'orchid', 'turquoise', 'lightcoral', 'palegreen', 'plum'
    ]

    fig, ax = plt.subplots(figsize=(10, 2))

    # Loop through each process and its intervals
    for i, process in enumerate(processes_list):
        color = colors[i % len(colors)]  # Assign a unique color to each process
        for start, end in zip(process.enter_cpu_time, process.leaving_cpu_time):
            duration = end - start
            ax.barh(0, duration, left=start, color=color, edgecolor='black', height=0.5)

    # Add labels and grid
    ax.set_xlabel('Time')
    ax.set_title('Gantt Chart for Multiple Processes')
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)

    # Remove y-axis
    ax.get_yaxis().set_visible(False)

    # Set x-axis ticks to increment by 1
    increase = 1
    max_time = max(max(p.leaving_cpu_time) for p in processes_list)
    ax.set_xticks(range(0, max_time + 1, increase))

    # Add legend for PIDs and colors
    legend_patches = [
        mpatches.Patch(color=colors[i % len(colors)], label=process.PID) for i, process in enumerate(processes_list)
    ]
    ax.legend(handles=legend_patches, title="Process PID", loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=len(processes_list))

    plt.tight_layout()
    plt.show()   



    for process in processes_list:
        print(process.PID)
        print(process.enter_cpu_time)
        print(process.leaving_cpu_time)

main()