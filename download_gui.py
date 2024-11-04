import tkinter as tk
from tkinter import messagebox
import subprocess
import concurrent.futures
from threading import Thread

# Abbruch-Flag für das Stoppen der Downloads
stop_event = False
processes = []  # Liste zur Speicherung der gestarteten Prozesse

# Funktion zum Hinzufügen eines neuen Downloads zur Liste
def add_to_list():
    filename = entry_filename.get()
    url = entry_url.get()
    
    if not filename or not url:
        messagebox.showwarning("Eingabefehler", "Bitte sowohl Dateiname als auch URL eingeben.")
        return
    
    # Dateiname und gekürzte URL zur Liste hinzufügen
    shortened_url = url if len(url) <= 20 else url[:20] + "..."
    download_list.append({"filename": filename, "url": url, "status": "Todo"})
    listbox.insert(tk.END, f"{filename} | {shortened_url} | Todo")
    
    # Textfelder leeren
    entry_filename.delete(0, tk.END)
    entry_url.delete(0, tk.END)

# Funktion für die parallele Verarbeitung
def start_downloads():
    global stop_event
    stop_event = False  # Reset des Abbruch-Flags
    processes.clear()  # Vorherige Prozesse leeren

    def download_video(item):
        global stop_event
        filename = item["filename"]
        url = item["url"]
        
        # URL manipulieren
        manipulated_url = url.split('&altManifestMetadata')[0].replace('\\', '')

        # Status auf "In Bearbeitung" setzen
        update_status(item, "In Bearbeitung")
        
        # ffmpeg-Befehl zusammenstellen
        command = [
            'ffmpeg', '-i', manipulated_url, '-codec', 'copy', filename
        ]
        
        # Prozess starten und zur Liste der Prozesse hinzufügen
        process = subprocess.Popen(command)
        processes.append(process)
        
        try:
            # Warten auf den Prozess
            process.wait()
            if stop_event:
                update_status(item, "Gestoppt")
            else:
                update_status(item, "Erfolgreich")
        except Exception as e:
            update_status(item, f"Fehler: {e}")

    # Funktion zum Status-Update in der GUI-Liste
    def update_status(item, new_status):
        item["status"] = new_status
        update_listbox()

    # Funktion zum Aktualisieren der GUI-Liste
    def update_listbox():
        listbox.delete(0, tk.END)
        for item in download_list:
            filename = item["filename"]
            shortened_url = item["url"] if len(item["url"]) <= 20 else item["url"][:20] + "..."
            status = item["status"]
            listbox.insert(tk.END, f"{filename} | {shortened_url} | {status}")

    # Parallele Downloads starten
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_video, item): item for item in download_list if item["status"] == "Todo"}

        # Fehlerhandling für parallele Downloads
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                future.result()
            except Exception as exc:
                update_status(item, f"Fehler: {exc}")

# Funktion zum Stoppen der Downloads
def stop_downloads():
    global stop_event
    stop_event = True
    messagebox.showinfo("Download-Manager", "Downloads werden gestoppt.")

    # Alle laufenden Prozesse beenden
    for process in processes:
        process.terminate()
    processes.clear()  # Liste der Prozesse leeren

# GUI-Setup mit tkinter
root = tk.Tk()
root.title("Video Downloader")

# Eingabefelder und Buttons
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Dateiname:").grid(row=0, column=0, padx=5)
entry_filename = tk.Entry(frame, width=30)
entry_filename.grid(row=0, column=1, padx=5)

tk.Label(frame, text="URL:").grid(row=1, column=0, padx=5)
entry_url = tk.Entry(frame, width=30)
entry_url.grid(row=1, column=1, padx=5)

button_add = tk.Button(frame, text="Add", command=add_to_list)
button_add.grid(row=2, column=0, columnspan=2, pady=5)

# Liste für die anzuzeigenden Einträge
download_list = []
listbox = tk.Listbox(root, width=60)
listbox.pack(pady=10)

button_start = tk.Button(root, text="Start", command=lambda: Thread(target=start_downloads).start())
button_start.pack(side=tk.LEFT, padx=5)

button_stop = tk.Button(root, text="Stop", command=stop_downloads)
button_stop.pack(side=tk.RIGHT, padx=5)

root.mainloop()
