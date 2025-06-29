import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import subprocess
import queue
import threading

# Create the main window
root = tk.Tk()
root.title("PulseAudio Control")

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=0, sticky='ns')

# Create the scrolled text widget for output
output_text = ScrolledText(root, state='disabled')
output_text.grid(row=0, column=1, sticky='nsew')

# Configure the grid to allow the text widget to expand
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Create a queue for output lines
output_queue = queue.Queue()

# Function to update the output text widget from the queue
def update_output():
    try:
        while True:
            line = output_queue.get_nowait()
            output_text.config(state='normal')
            output_text.insert(tk.END, line)
            output_text.yview(tk.END)
            output_text.config(state='disabled')
    except queue.Empty:
        pass
    root.after(100, update_output)

# Function to run a command in a separate thread and capture its output
def run_command(cmd):
    # Clear the current output
    output_text.config(state='normal')
    output_text.delete(1.0, tk.END)
    output_text.config(state='disabled')

    def target():
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in iter(process.stdout.readline, ''):
            output_queue.put(line)
        for line in iter(process.stderr.readline, ''):
            output_queue.put(line)
        process.stdout.close()
        process.stderr.close()
        process.wait()

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

# List of buttons with labels and corresponding commands
commands = [
    ("PulseAudio Info", "pactl info"),
    ("Restart PulseAudio", "systemctl --user restart pulseaudio.service"),
    ("Start PulseAudio", "pulseaudio --start")
#    ("Kill PulseAudio", "pulseaudio -k"),
#    ("Status PulseAudio", "systemctl --user status pulseaudio.service")
]

# Create buttons in the button frame
for label, cmd in commands:
    button = tk.Button(button_frame, text=label, command=lambda c=cmd: run_command(c))
    button.pack(side='top', fill='x')
    
instruction_label = tk.Label(button_frame, text="Now switch audio device from digital on analog and vice versa.")
instruction_label.pack(side='top')

# Start the output update loop
update_output()

# Start the Tkinter event loop
root.mainloop()
