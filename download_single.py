import sys
import subprocess

def main():
    # Überprüfen, ob genügend Argumente übergeben wurden
    if len(sys.argv) != 3:
        print("Usage: python download_single.py <output_filename> <URL>")
        sys.exit(1)

    # Argumente auslesen
    output_filename = sys.argv[1]
    url = sys.argv[2]

    # URL manipulieren: Alles nach '&altmanifest' abschneiden und Escape-Zeichen entfernen
    manipulated_url = url.split('&altManifestMetadata')[0].replace('\\', '')

    # ffmpeg-Befehl zusammenstellen und ausführen
    command = [
        'ffmpeg', '-i', manipulated_url, '-codec', 'copy', output_filename
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Download abgeschlossen: {output_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von ffmpeg: {e}")

if __name__ == "__main__":
    main()
