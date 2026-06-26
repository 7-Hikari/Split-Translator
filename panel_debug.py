import sys
import tkinter as tk

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        if self.text_widget.winfo_exists():
            self.text_widget.configure(state=tk.NORMAL)
            self.text_widget.insert(tk.END, string)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state=tk.DISABLED)

    def flush(self):
        pass

def buat_panel_debug(root):
    debug_frame = tk.LabelFrame(root, text=" Jendela Debug Console (System Log) ", bg="#2f3640", fg="#f5f6fa", font=("Arial", 9, "bold"), padx=5, pady=5)
    debug_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    debug_scrollbar = tk.Scrollbar(debug_frame)
    debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    debug_text_widget = tk.Text(debug_frame, height=6, bg="#1e2124", fg="#00ff00", font=("Consolas", 9), yscrollcommand=debug_scrollbar.set, state=tk.DISABLED)
    debug_text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
    debug_scrollbar.config(command=debug_text_widget.yview)

    sys.stdout = TextRedirector(debug_text_widget)
    return debug_frame
