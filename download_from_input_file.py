import csv
import subprocess
import concurrent.futures

# Funktion für das Ausführen eines einzelnen Downloads
def download_video(row):
    filename, status, url = row
    
    # Update Status auf "In Bearbeitung" in der CSV-Datei
    update_status(filename, "In Bearbeitung")
    
    # URL manipulieren: Alles nach '&altmanifest' abschneiden und Escape-Zeichen entfernen
    manipulated_url = url.split('&altManifestMetadata')[0].replace('\\', '')
    
    # ffmpeg-Befehl zusammenstellen
    command = [
        'ffmpeg', '-i', manipulated_url, '-codec', 'copy', filename
    ]

    try:
        # Download ausführen
        subprocess.run(command, check=True)
        # Status auf "Erfolgreich" setzen, wenn der Download abgeschlossen ist
        update_status(filename, "Erfolgreich")
    except subprocess.CalledProcessError as e:
        # Status auf "Fehler" setzen, wenn ein Fehler auftritt
        update_status(filename, f"Fehler: {e}")

# Funktion zum Status-Update in der CSV-Datei
def update_status(filename, new_status):
    with open('input.csv', 'r', newline='') as infile:
        rows = list(csv.reader(infile, delimiter=';'))
    
    # Status ändern
    for row in rows:
        if row[0] == filename:
            row[1] = new_status
            break

    # Datei aktualisieren
    with open('input.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerows(rows)

# Hauptprogramm zum Verwalten von parallelen Downloads
def main():
    # Laden der zu bearbeitenden Zeilen
    with open('input.csv', 'r', newline='') as infile:
        reader = csv.reader(infile, delimiter=';')
        rows = [row for row in reader if row[1].lower() == "todo"]

    # ThreadPool für parallele Downloads (4 Threads)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_video, row): row for row in rows}

        # Abarbeitung der Downloads und Fehlerhandling
        for future in concurrent.futures.as_completed(futures):
            row = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f'Download für {row[0]} fehlgeschlagen: {exc}')

if __name__ == "__main__":
    main()
