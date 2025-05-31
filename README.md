<h1>🧬 DLL Injector GUI</h1>

<p>This is a simple Windows DLL injector with a graphical user interface (GUI) built using <strong>Python</strong> 🐍 and <strong>tkinter</strong> 🪟.</p>

<h2>🚀 Features</h2>
<ul>
  <li>🔍 Allows selecting a running process by name.</li>
  <li>📂 Lets you browse and select a DLL file to inject.</li>
  <li>🧠 Performs DLL injection using Windows API calls via <code>ctypes</code>.</li>
  <li>📣 Provides real-time feedback on success or error messages.</li>
  <li>🎨 Clean and minimalistic user interface.</li>
</ul>

<h2>⚙️ How it works</h2>
<p>The injector finds the target process ID by its name, opens the process with required permissions, allocates memory inside it, writes the DLL path there, and creates a remote thread to load the DLL using <code>LoadLibraryW</code>.</p>

<h2>📌 Usage</h2>
<ol>
  <li>🖊️ Enter the exact name of the process you want to inject the DLL into (e.g., <code>notepad.exe</code>).</li>
  <li>📁 Select the DLL file using the "Select DLL" button.</li>
  <li>💉 Click "Inject" to perform the injection.</li>
  <li>✅ Messages will display below to indicate success or any errors encountered.</li>
</ol>

<h2>📦 Requirements</h2>
<ul>
  <li>🪟 Windows OS</li>
  <li>🐍 Python 3.x</li>
  <li>📚 Modules: <code>tkinter</code>, <code>psutil</code>, <code>ctypes</code></li>
</ul>

<h2>⚠️ Disclaimer</h2>
<p>This tool is intended for <strong>educational purposes only</strong>. Injecting DLLs into processes can be dangerous and may violate software terms of service or laws. Use responsibly.</p>
