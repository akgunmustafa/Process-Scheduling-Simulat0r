import copy


class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        self.priority = int(priority)
        self.remaining_time = int(burst_time)
        self.start_time = -1
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0

    def reset(self):
        self.remaining_time = self.burst_time
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0

    def to_dict(self):
        return {
            "pid": self.pid,
            "arrival": self.arrival_time,
            "burst": self.burst_time,
            "priority": self.priority,
            "finish": self.finish_time,
            "turnaround": self.turnaround_time,
            "waiting": self.waiting_time,
        }


def calculate_metrics(processes, gantt, total_time):
    total_turnaround = 0
    total_waiting = 0
    idle_time = sum([end - start for pid, start, end in gantt if pid is None])

    proc_list = []
    for p in processes:
        p.turnaround_time = p.finish_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        total_turnaround += p.turnaround_time
        total_waiting += p.waiting_time
        proc_list.append(p.to_dict())

    # Sort output by PID for a stable table
    proc_list.sort(key=lambda x: x["pid"])

    avg_turnaround = total_turnaround / len(processes) if processes else 0
    avg_waiting = total_waiting = total_waiting / len(processes) if processes else 0
    utilization = (
        ((total_time - idle_time) / total_time * 100) if total_time > 0 else 0
    )

    return {
        "processes": proc_list,
        "average_turnaround": round(avg_turnaround, 2),
        "average_waiting": round(avg_waiting, 2),
        "utilization": round(utilization, 2),
        "gantt_chart": gantt,
    }


def run_fcfs(processes):
    processes.sort(key=lambda x: x.arrival_time)
    current_time = 0
    gantt = []
    for p in processes:
        if current_time < p.arrival_time:
            gantt.append((None, current_time, p.arrival_time))
            current_time = p.arrival_time
        start = current_time
        current_time += p.burst_time
        p.finish_time = current_time
        gantt.append((p.pid, start, current_time))
    return calculate_metrics(processes, gantt, current_time)


def run_sjf(processes):
    n = len(processes)
    completed = 0
    current_time = 0
    gantt = []
    is_completed = [False] * n

    while completed < n:
        idx = -1
        min_burst = float("inf")
        for i in range(n):
            if processes[i].arrival_time <= current_time and not is_completed[i]:
                if processes[i].burst_time < min_burst:
                    min_burst = processes[i].burst_time
                    idx = i
                elif processes[i].burst_time == min_burst:
                    # Tie‑break FCFS style
                    if processes[i].arrival_time < processes[idx].arrival_time:
                        idx = i

        if idx != -1:
            p = processes[idx]
            start = current_time
            current_time += p.burst_time
            p.finish_time = current_time
            is_completed[idx] = True
            completed += 1
            gantt.append((p.pid, start, current_time))
        else:
            gantt.append((None, current_time, current_time + 1))
            current_time += 1

    return calculate_metrics(processes, gantt, current_time)


def run_priority(processes):
    n = len(processes)
    completed = 0
    current_time = 0
    gantt = []
    is_completed = [False] * n

    while completed < n:
        idx = -1
        min_prio = float("inf")
        for i in range(n):
            if processes[i].arrival_time <= current_time and not is_completed[i]:
                if processes[i].priority < min_prio:
                    min_prio = processes[i].priority
                    idx = i
                elif processes[i].priority == min_prio:
                    if processes[i].arrival_time < processes[idx].arrival_time:
                        idx = i

        if idx != -1:
            p = processes[idx]
            start = current_time
            current_time += p.burst_time
            p.finish_time = current_time
            is_completed[idx] = True
            completed += 1
            gantt.append((p.pid, start, current_time))
        else:
            gantt.append((None, current_time, current_time + 1))
            current_time += 1

    return calculate_metrics(processes, gantt, current_time)


def run_rr(processes, time_quantum):
    processes.sort(key=lambda x: x.arrival_time)
    current_time = 0
    gantt = []
    queue = []
    i = 0
    n = len(processes)

    # Push initial processes that have already arrived
    while i < n and processes[i].arrival_time <= current_time:
        queue.append(processes[i])
        i += 1

    while queue or i < n:
        if not queue:
            # CPU is idle until next process arrives
            gantt.append((None, current_time, processes[i].arrival_time))
            current_time = processes[i].arrival_time
            while i < n and processes[i].arrival_time <= current_time:
                queue.append(processes[i])
                i += 1

        p = queue.pop(0)
        start = current_time
        exec_time = min(p.remaining_time, time_quantum)
        p.remaining_time -= exec_time
        current_time += exec_time
        gantt.append((p.pid, start, current_time))

        while i < n and processes[i].arrival_time <= current_time:
            queue.append(processes[i])
            i += 1

        if p.remaining_time > 0:
            queue.append(p)
        else:
            p.finish_time = current_time

    return calculate_metrics(processes, gantt, current_time)


