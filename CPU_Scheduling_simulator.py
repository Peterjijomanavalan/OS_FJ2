import customtkinter as ctk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ---------------- Scheduling Algorithms ----------------

def fcfs(processes):
    processes.sort(key=lambda x: x[1])
    time = 0
    gantt, wt, tat = [], [], []
    for pid, at, bt, pr in processes:
        if time < at:
            time = at
        start, end = time, time + bt
        gantt.append((pid, start, end))
        wt.append(start - at)
        tat.append(end - at)
        time += bt
    return wt, tat, gantt


def sjf(processes):
    processes.sort(key=lambda x: x[1])
    n = len(processes)
    completed = [False] * n
    t = 0
    gantt, wt, tat = [], [0]*n, [0]*n
    completed_count = 0

    while completed_count < n:
        ready = [(i, p) for i, p in enumerate(processes) if p[1] <= t and not completed[i]]
        if not ready:
            t += 1
            continue
        i, p = min(ready, key=lambda x: x[1][2])  # choose smallest burst time
        start, end = t, t + p[2]
        gantt.append((p[0], start, end))
        wt[i] = start - p[1]
        tat[i] = end - p[1]
        t = end
        completed[i] = True
        completed_count += 1

    return wt, tat, gantt


def priority_scheduling(processes):
    processes.sort(key=lambda x: (x[1], x[3]))  # sort by arrival then priority
    n = len(processes)
    t = 0
    completed = [False]*n
    gantt, wt, tat = [], [0]*n, [0]*n
    done = 0

    while done < n:
        ready = [(i, p) for i, p in enumerate(processes) if p[1] <= t and not completed[i]]
        if not ready:
            t += 1
            continue
        i, p = min(ready, key=lambda x: x[1][3])
        start, end = t, t + p[2]
        gantt.append((p[0], start, end))
        wt[i] = start - p[1]
        tat[i] = end - p[1]
        t = end
        completed[i] = True
        done += 1

    return wt, tat, gantt


def round_robin(processes, quantum):
    n = len(processes)
    queue = []
    gantt = []
    t = 0
    rem_bt = [p[2] for p in processes]
    wt = [0]*n
    tat = [0]*n

    processes.sort(key=lambda x: x[1])
    queue.append(0)
    visited = [False]*n
    visited[0] = True

    while queue:
        i = queue.pop(0)
        if rem_bt[i] > quantum:
            gantt.append((processes[i][0], t, t+quantum))
            t += quantum
            rem_bt[i] -= quantum
        else:
            gantt.append((processes[i][0], t, t+rem_bt[i]))
            t += rem_bt[i]
            wt[i] = t - processes[i][1] - processes[i][2]
            rem_bt[i] = 0

        for j in range(n):
            if processes[j][1] <= t and not visited[j] and rem_bt[j] > 0:
                queue.append(j)
                visited[j] = True
        if rem_bt[i] > 0:
            queue.append(i)

    for i in range(n):
        tat[i] = wt[i] + processes[i][2]
    return wt, tat, gantt


# ---------------- GUI Application ----------------

class ModernSchedulerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Simulator by Team 17")
        self.geometry("900x650")
        ctk.set_appearance_mode("system")  # Options: "light", "dark", "system"
        ctk.set_default_color_theme("blue")

        self.processes = []

        # ---------------- Title ----------------
        title = ctk.CTkLabel(self, text="CPU Scheduling Algorithm Simulator", font=("Helvetica", 22, "bold"))
        title.pack(pady=15)

        # ---------------- Algorithm Frame ----------------
        algo_frame = ctk.CTkFrame(self)
        algo_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(algo_frame, text="Select Algorithm:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.algo = ctk.CTkComboBox(algo_frame, values=["FCFS", "SJF", "Priority", "Round Robin"], width=180)
        self.algo.grid(row=0, column=1, padx=10)
        self.algo.set("FCFS")

        ctk.CTkLabel(algo_frame, text="Time Quantum:", font=("Helvetica", 14)).grid(row=0, column=2, padx=10)
        self.quantum = ctk.CTkEntry(algo_frame, width=100, placeholder_text="For RR only")
        self.quantum.grid(row=0, column=3, padx=10)

        # ---------------- Input Frame ----------------
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, padx=10, fill="x")

        labels = ["PID", "Arrival Time", "Burst Time", "Priority"]
        for i, text in enumerate(labels):
            ctk.CTkLabel(input_frame, text=text, font=("Helvetica", 13)).grid(row=0, column=i, padx=10)

        self.pid = ctk.CTkEntry(input_frame, width=100)
        self.at = ctk.CTkEntry(input_frame, width=100)
        self.bt = ctk.CTkEntry(input_frame, width=100)
        self.pr = ctk.CTkEntry(input_frame, width=100)

        self.pid.grid(row=1, column=0, padx=10, pady=5)
        self.at.grid(row=1, column=1, padx=10, pady=5)
        self.bt.grid(row=1, column=2, padx=10, pady=5)
        self.pr.grid(row=1, column=3, padx=10, pady=5)

        ctk.CTkButton(input_frame, text="Add Process", command=self.add_process).grid(row=1, column=4, padx=10)
        ctk.CTkButton(input_frame, text="Clear All", command=self.clear_all, fg_color="red", hover_color="#cc0000").grid(row=1, column=5, padx=10)

        # ---------------- TreeView ----------------
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1a1a1a", foreground="white", fieldbackground="#1a1a1a", rowheight=25)
        style.map("Treeview", background=[("selected", "#007acc")])

        columns = ("PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(fill="both", expand=True)

        # ---------------- Buttons ----------------
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Run Simulation", command=self.run_simulation, width=200).pack(side="left", padx=10)

        # ---------------- Gantt Chart Frame ----------------
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # ---------------- Functions ----------------
    def add_process(self):
        try:
            pid = self.pid.get().strip()
            at = int(self.at.get())
            bt = int(self.bt.get())
            pr = int(self.pr.get()) if self.pr.get() else 0
            self.processes.append((pid, at, bt, pr))
            self.tree.insert("", "end", values=(pid, at, bt, pr, "", ""))
            self.pid.delete(0, 'end')
            self.at.delete(0, 'end')
            self.bt.delete(0, 'end')
            self.pr.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")

    def clear_all(self):
        self.processes.clear()
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.quantum.delete(0, 'end')
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please add at least one process")
            return

        algo = self.algo.get()
        if algo == "FCFS":
            wt, tat, gantt = fcfs(self.processes)
        elif algo == "SJF":
            wt, tat, gantt = sjf(self.processes)
        elif algo == "Priority":
            wt, tat, gantt = priority_scheduling(self.processes)
        elif algo == "Round Robin":
            try:
                q = int(self.quantum.get())
                wt, tat, gantt = round_robin(self.processes, q)
            except ValueError:
                messagebox.showerror("Error", "Enter valid time quantum for Round Robin")
                return
        else:
            return

        # Clear table and refill
        for i in self.tree.get_children():
            self.tree.delete(i)

        total_wt, total_tat = 0, 0
        for i, p in enumerate(self.processes):
            total_wt += wt[i]
            total_tat += tat[i]
            self.tree.insert("", "end", values=(p[0], p[1], p[2], p[3], wt[i], tat[i]))

        avg_wt = total_wt / len(self.processes)
        avg_tat = total_tat / len(self.processes)
        messagebox.showinfo("Results", f"Average Waiting Time: {avg_wt:.2f}\nAverage Turnaround Time: {avg_tat:.2f}")

        self.plot_gantt(gantt)

    def plot_gantt(self, gantt):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 2))
        colors = plt.cm.tab20.colors

        for i, (pid, start, end) in enumerate(gantt):
            ax.barh(0, end - start, left=start, color=colors[i % len(colors)], edgecolor='black', height=0.5)
            ax.text((start + end) / 2, 0, pid, ha='center', va='center', color='white', fontweight='bold')

        ax.set_xlabel("Time", fontsize=10)
        ax.set_yticks([])
        ax.set_title("Gantt Chart", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


# ---------------- Run App ----------------
if __name__ == "__main__":
    app = ModernSchedulerApp()
    app.mainloop()