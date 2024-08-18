import tkinter as tk
from tkinter import filedialog as fd
from ctypes import *
import psutil as ps
import os

def getpid(process_name):
    for proc in ps.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name.lower():
            return proc.info['pid']
    return None

def inject():
    process_name = entry_process.get().strip()
    dll_path = entry_file.get().strip()
    if not process_name or not dll_path:
        output_label.config(text="Invalid process name or DLL path!")
        return
    if not os.path.exists(dll_path):
        output_label.config(text="The DLL path does not exist!")
        return
    pid = getpid(process_name)
    if not pid:
        output_label.config(text=f"Process '{process_name}' not found!")
        return
    PAGE_READWRITE = 0x04
    PROCESS_ALL_ACCESS = (0x00F0000 | 0x00100000 | 0xFFF)
    VIRTUAL_MEM = (0x1000 | 0x2000)
    kernel32 = windll.kernel32
    dll_len = len(dll_path)
    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, True, pid)
    if not h_process:
        output_label.config(text=f"Unable to get handle for PID {pid}!")
        return
    arg_address = kernel32.VirtualAllocEx(h_process, 0, dll_len, VIRTUAL_MEM, PAGE_READWRITE)
    written = c_int(0)
    kernel32.WriteProcessMemory(h_process, arg_address, dll_path.encode('utf-8'), dll_len, byref(written))
    h_kernel32 = kernel32.GetModuleHandleA(b"kernel32.dll")
    h_loadlib = kernel32.GetProcAddress(h_kernel32, b"LoadLibraryA")
    thread_id = c_ulong(0)
    if not kernel32.CreateRemoteThread(h_process, None, 0, h_loadlib, arg_address, 0, byref(thread_id)):
        output_label.config(text="Failed :(")
        return
    output_label.config(text=f"Completed! Thread ID: 0x{thread_id.value:08x}")

def select_dll():
    path = fd.askopenfilename(
        title="Select a DLL file",
        filetypes=[("DLL files", "*.dll")],
        defaultextension=".dll"
    )
    if path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, path)

main = tk.Tk()
main.title("DLL Injector")
frm = tk.Frame(main)
frm.grid(row=0, column=0, padx=10, pady=10)
tk.Label(frm, text="Name of the process:").grid(row=0, column=0, pady=5)
entry_process = tk.Entry(frm)
entry_process.grid(row=0, column=1, padx=10, pady=5)
tk.Label(frm, text="DLL Path:").grid(row=1, column=0, pady=5)
entry_file = tk.Entry(frm)
entry_file.grid(row=1, column=1, padx=10, pady=5)
select_button = tk.Button(frm, text="Select DLL", command=select_dll)
select_button.grid(row=2, column=1, pady=10)
inject_button = tk.Button(frm, text="Inject", command=inject)
inject_button.grid(row=3, column=1, pady=10)
output_label = tk.Label(frm, text="", fg="red")
output_label.grid(row=4, column=0, columnspan=2, pady=10)
tk.Button(frm, text="Close", command=main.destroy).grid(row=5, column=1, pady=10)
main.mainloop()