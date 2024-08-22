import tkinter as tk
from tkinter import filedialog as fd
import ctypes
import ctypes.wintypes as wintypes
import psutil
import os

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04

SIZE_T = ctypes.c_size_t
LPVOID = ctypes.c_void_p
HANDLE = wintypes.HANDLE
BOOL = wintypes.BOOL
DWORD = wintypes.DWORD

kernel32 = ctypes.WinDLL('Kernel32', use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.restype = HANDLE
OpenProcess.argtypes = (DWORD, BOOL, DWORD)

VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.restype = LPVOID
VirtualAllocEx.argtypes = (HANDLE, LPVOID, SIZE_T, DWORD, DWORD)

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.restype = BOOL
WriteProcessMemory.argtypes = (HANDLE, LPVOID, ctypes.c_void_p, SIZE_T, ctypes.POINTER(SIZE_T))

CreateRemoteThread = kernel32.CreateRemoteThread
CreateRemoteThread.restype = HANDLE
CreateRemoteThread.argtypes = (HANDLE, LPVOID, SIZE_T, LPVOID, LPVOID, DWORD, ctypes.POINTER(DWORD))

GetProcAddress = kernel32.GetProcAddress
GetProcAddress.restype = LPVOID
GetProcAddress.argtypes = (HANDLE, ctypes.c_char_p)

def get_process_id(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
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
    
    try:
        process_id = get_process_id(process_name)
        if not process_id:
            output_label.config(text=f"Could not find process '{process_name}'.")
            return
        process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, process_id)
        if not process_handle:
            output_label.config(text=f"Failed to open process. Error code: {ctypes.get_last_error()}")
            return
        dll_path_encoded = dll_path.encode('utf-16-le')
        size = len(dll_path_encoded) + 2
        allocated_memory = VirtualAllocEx(process_handle, None, SIZE_T(size), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not allocated_memory:
            output_label.config(text=f"Failed to allocate memory in target process. Error code: {ctypes.get_last_error()}")
            return
        written_size = SIZE_T(0)
        write = WriteProcessMemory(process_handle, allocated_memory, dll_path_encoded, SIZE_T(size), ctypes.byref(written_size))
        if not write:
            output_label.config(text=f"Failed to write DLL to target process. Error code: {ctypes.get_last_error()}")
            return
        load_library_address = GetProcAddress(kernel32._handle, b'LoadLibraryW')
        if not load_library_address:
            output_label.config(text=f"Failed to get LoadLibraryW address. Error code: {ctypes.get_last_error()}")
            return
        thread_id = DWORD(0)
        thread_handle = CreateRemoteThread(process_handle, None, 0, load_library_address, allocated_memory, 0, ctypes.byref(thread_id))
        if not thread_handle:
            output_label.config(text=f"Failed to create remote thread. Error code: {ctypes.get_last_error()}")
            return
        output_label.config(text="DLL injection successful!")
    except Exception as e:
        output_label.config(text=f"An error occurred: {str(e)}")

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
