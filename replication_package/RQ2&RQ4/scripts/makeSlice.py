import requests
from datetime import datetime, timedelta
import os
import subprocess
import argparse
import shutil
import sys

def parse_repo_url(url):
    """Estrae owner e repo da un URL GitHub."""
    parts = url.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("URL non valido. Formato atteso: https://github.com/owner/repo")
    owner = parts[-2]
    repo = parts[-1].replace(".git", "")
    return owner, repo

def get_repo_creation_date(owner, repo, token):
    """Recupera la data di creazione del repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {token}"} if token else {}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        repo_data = response.json()
        created_at = repo_data.get("created_at")
        if created_at:
            return datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    except requests.exceptions.RequestException as e:
        print(f"Errore API per ottenere data creazione: {str(e)}", file=sys.stderr)
    
    # Fallback: se non riesce a recuperare, usa una data predefinita antica
    return datetime(2008, 1, 1)  # GitHub è stato lanciato nel 2008

def get_commits_in_interval(owner, repo, token, since, until):
    """Recupera i commit nell'intervallo specificato."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"} if token else {}
    params = {"since": since.isoformat(), "until": until.isoformat()}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Errore API per {since.date()} - {until.date()}: {str(e)}", file=sys.stderr)
        return None

def create_snapshot(repo_url, commit_hash, output_dir, dir_name):
    """Crea una snapshot completa del repo a un commit specifico."""
    snapshot_dir = os.path.join(output_dir, dir_name)
    
    if os.path.exists(snapshot_dir):
        shutil.rmtree(snapshot_dir)

    try:
        # Clona l'intera repository (senza --depth 1)
        subprocess.run(
            ["git", "clone", repo_url, snapshot_dir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        # Checkout del commit specifico
        subprocess.run(
            ["git", "-C", snapshot_dir, "checkout", commit_hash],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Errore Git per {dir_name}: {e.stderr.decode().strip()}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Crea snapshot quadrimestrali di una repository GitHub.")
    parser.add_argument("repo_url", help="URL della repository (es: https://github.com/owner/repo)")
    parser.add_argument("--token", help="Token GitHub (per repo private)", default="")
    parser.add_argument("--start_date", help="Data di inizio (YYYY-MM-DD). Se non specificata, usa la data di creazione del repo", default=None)
    parser.add_argument("--end_date", help="Data di fine (YYYY-MM-DD)", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()

    try:
        owner, repo = parse_repo_url(args.repo_url)
    except ValueError as e:
        print(f"Errore: {str(e)}", file=sys.stderr)
        sys.exit(1)

    try:
        # Ottieni la data di creazione del repository
        creation_date = get_repo_creation_date(owner, repo, args.token)
        print(f"Data di creazione del repository: {creation_date.date()}")
        
        # Determina la data di inizio
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        else:
            start_date = creation_date
        
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        
        # Assicurati che la data di inizio non sia anteriore alla creazione
        if start_date < creation_date:
            print(f"Avviso: La data di inizio specificata ({start_date.date()}) è anteriore alla creazione del repo ({creation_date.date()}).")
            print(f"Userò la data di creazione come inizio.")
            start_date = creation_date
            
    except ValueError as e:
        print(f"Formato data non valido. Usa YYYY-MM-DD: {str(e)}", file=sys.stderr)
        sys.exit(1)

    repo_dir = f"snapshots_{owner}_{repo}"
    os.makedirs(repo_dir, exist_ok=True)

    print(f"Creazione snapshot quadrimestrali per {owner}/{repo} in '{repo_dir}/'...")
    print(f"Periodo: {start_date.date()} - {end_date.date()}")
    print("-" * 60)

    current_start = start_date
    snapshot_count = 0
    
    while current_start < end_date:
        # Intervallo di 4 mesi (circa 120 giorni)
        # Usiamo 4 * 30 = 120 giorni come approssimazione
        days_in_interval = 120
        current_end = min(current_start + timedelta(days=days_in_interval), end_date)
        
        # Arrotonda al primo giorno del mese per naming consistente
        interval_start = current_start.replace(day=1)
        # Per l'end, se siamo alla fine del periodo, usiamo la data effettiva
        if current_end == end_date:
            interval_end = current_end
        else:
            interval_end = current_end.replace(day=1)
        
        commits = get_commits_in_interval(owner, repo, args.token, current_start, current_end)

        if not commits:
            print(f"Nessun commit tra {interval_start.date()} e {interval_end.date()}. Saltato.")
            current_start = current_end
            continue

        last_commit_hash = commits[0]["sha"]
        dir_name = f"{interval_start.strftime('%Y-%m')}_to_{interval_end.strftime('%Y-%m')}"
        
        if create_snapshot(args.repo_url, last_commit_hash, repo_dir, dir_name):
            print(f"✓ Snapshot {snapshot_count + 1}: {dir_name}")
            print(f"  Periodo: {current_start.date()} - {current_end.date()}")
            print(f"  Ultimo commit: {last_commit_hash[:7]}")
            print(f"  Numero commit nell'intervallo: {len(commits)}")
            print("-" * 60)
            snapshot_count += 1
        else:
            print(f"✗ Fallita snapshot per {dir_name}.", file=sys.stderr)

        current_start = current_end

    print(f"\nOperazione completata!")
    print(f"Create {snapshot_count} snapshot quadrimestrali in '{repo_dir}/'")
    print(f"Data inizio (creazione repo): {creation_date.date()}")
    print(f"Data fine: {end_date.date()}")

if __name__ == "__main__":
    main()