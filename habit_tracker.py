import json
import os
from datetime import date, timedelta

DATA_FILE = "data.json"

VERDE = "\033[92m"
ROSSO = "\033[91m"
GIALLO = "\033[93m"
RESET = "\033[0m"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"habits": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def aggiungi_abitudine(data):
    nome = input("Nome abitudine: ").strip()
    if nome == "":
        print("Nome non valido.")
        return
    if nome in data["habits"]:
        print(f"`{nome}` esiste già!")
        return
    data["habits"][nome] = []
    save_data(data)
    print(f"Abitudine `{nome}` aggiunta!")

def segna_completata(data):
    if not data["habits"]:
        print("Nessuna abitudine trovata. Aggiungine una prima!")
        return

    oggi = str(date.today())
    print("\nLe tue abitudini:")
    nomi = list(data["habits"].keys())
    for i, nome in enumerate(nomi):
        completata = "✓" if oggi in data["habits"][nome] else " "
        print(f"{i+1}. [{completata}] {nome}")

    scelta = input("\nQuale hai completato oggi? (numero): ")
    try:
        idx = int(scelta) - 1
        nome = nomi[idx]
        if oggi in data["habits"][nome]:
            print(f"Hai già segnato `{nome}` oggi!")
        else:
            data["habits"][nome].append(oggi)
            save_data(data)
            print(f"`{nome}` segnata per oggi!")
    except (ValueError, IndexError):
        print("Scelta non valida.")

def calcola_streak(date_list):
    if not date_list:
        return 0
    date_ordinate = sorted(
        [date.fromisoformat(d) for d in date_list],
        reverse=True
    )
    streak = 0
    giorno = date.today()
    for d in date_ordinate:
        if d == giorno:
            streak += 1
            giorno -= timedelta(days=1)
        elif d == giorno + timedelta(days=1):
            giorno = d - timedelta(days=1)
            streak += 1
        else:
            break
    return streak

def vedi_statistiche(data):
    if not data["habits"]:
        print("Nessuna abitudine trovata.")
        return
    print("\nSTATISTICHE\n")
    print(f"{'Abitudine': <25} {'Totale': >7} {'Streak': >7} {'% 7gg': >7}")
    print("-" * 50)
    ultima_settimana = [
        (date.today() - timedelta(days=i)).isoformat()
        for i in range(7)
    ]
    for nome, date_list in data["habits"].items():
        totale = len(date_list)
        streak = calcola_streak(date_list)
        completate = sum(1 for d in ultima_settimana if d in date_list)
        percentuale = int((completate / 7) * 100)
        print(f"{nome: <25} {totale: >7} {streak: >6} {percentuale: >6}%")

def mostra_heatmap(data):
    if not data["habits"]:
        print("Nessuna abitudine trovata")
        return
    print("\nHEATMAP ULTIMI 21 GIORNI\n")
    giorni = [
        (date.today() - timedelta(days=i)).isoformat()
        for i in range(20, -1, -1)
    ]
    print("Abitudine            ", end="")
    for g in giorni:
        d = date.fromisoformat(g)
        print(f"{d.day:>3}", end="")
    print()
    for nome, date_list in data["habits"].items():
        print(f"{nome: <25}", end="")
        for g in giorni:
            if g in date_list:
                print(f" {VERDE}●{RESET}", end=" ")
            else:
                print(f"{ROSSO}○{RESET}", end=" ")
        print()

def elimina_abitudine(data):
    if not data["habits"]:
        print("Nessuna abitudine da eliminare.")
        return
    nomi = list(data["habits"].keys())
    for i, nome in enumerate(nomi):
        print(f"{i+1}. {nome}")
    scelta = input("Quale eliminare? (numero): ")
    try:
        idx = int(scelta) - 1
        nome = nomi[idx]
        conferma = input(f"Sicuro di eliminare `{nome}`? (s/n): ")
        if conferma.lower() == "s":
            del data["habits"][nome]
            save_data(data)
            print(f"`{nome}` eliminata.")
    except (ValueError, IndexError):
        print("Scelta non valida")

def main():
    while True:
        data = load_data()
        print("\n=== HABIT TRACKER ===")
        print("1. Aggiungi abitudine")
        print("2. Segna completata oggi")
        print("3. Vedi statistiche")
        print("4. Heatmap")
        print("5. Elimina abitudine")
        print("6. Esci")
        scelta = input("\nScegli: ")

        if scelta == "1":
            aggiungi_abitudine(data)
        elif scelta == "2":
            segna_completata(data)
        elif scelta == "3":
            vedi_statistiche(data)
        elif scelta == "4":
            mostra_heatmap(data)
        elif scelta == "5":
            elimina_abitudine(data)
        elif scelta == "6":
            print("Ciao!")
            break

if __name__ == "__main__":
    main()