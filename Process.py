class Process:
    # [PID]    [Arrival Time]    [Priority]    [Sequence of CPU and IO bursts]

    wait_request_time = 0 #time in waiting q (request for resource)
    currentBurst = 0

    def __init__(self, PID, Arrival_time, total_cpu_time, total_IO_time, Priority,bursts,burstsTime,state,
                 enter_cpu_time,leaving_cpu_time,finish_time,ready_queue_time,done,currentBurst,currentCPUBurst,Fixed_Arrival_Time,
                 total_waiting_resource_time): #,data for the dictionary:

        self.PID = PID
        self.Arrival_time = Arrival_time
        self.total_cpu_time = total_cpu_time #sum of cpu bursts times
        self.total_IO_time = total_IO_time #sum of IO bursts times
        self.Priority = Priority
        self.remaining_time = total_cpu_time #initially
        self.bursts = bursts
        self.burstsTime = burstsTime
        self.state=state #ready, waiting ...
        self.enter_cpu_time = enter_cpu_time
        self.leaving_cpu_time = leaving_cpu_time
        self.finish_time = finish_time # termination time 
        self.ready_queue_time = ready_queue_time #time in ready Q
        self.done = done #if process has done
        self.currentBurst = currentBurst
        self.currentCPUBurst = currentCPUBurst
        self.Fixed_Arrival_Time = Fixed_Arrival_Time
        self.total_waiting_resource_time = total_waiting_resource_time

    def decrease_cpu_remaining(self):

        if self.remaining_time <= 0:
            self.remaining_time = 0
        else:
            self.remaining_time = self.remaining_time - 1


    def calculate_waiting_time(self): #avg in main
         #in ready Q
         return self.finish_time - self.Fixed_Arrival_Time - self.total_cpu_time - self.total_IO_time - self.total_waiting_resource_time

    def calculate_turnaround_time(self): #avg in main
         return self.finish_time - self.Fixed_Arrival_Time
    