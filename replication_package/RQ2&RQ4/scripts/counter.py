import os
import argparse
import csv
from collections import defaultdict
import openpyxl
from openpyxl import Workbook


COLUMN_ORDER = ['CG', 'ROC', 'NC', 'LC', 'IM', 'IdQ', 'IQ', 'LPQ']

def debug_folder_content(folder_path):
    print("\nDEBUG - Contenuto della cartella:")
    print("="*50)
    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        file_type = "file" if os.path.isfile(full_path) else "cartella"
        print(f"- {item} ({file_type})")
    print("="*50)

def count_types_in_csv(filepath):
    type_counts = defaultdict(int)
    try:
        with open(filepath, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'type' not in reader.fieldnames:
                print(f" Colonna 'type' non trovata nel file CSV")
                return {}, False
                
            count = 0
            for row in reader:
                type_value = row['type'].strip().upper()
                if type_value == "IDQ":
                    type_value = "IdQ"
                if type_value in COLUMN_ORDER or type_value == "IdQ":
                    type_counts[type_value] += 1
                    count += 1
            
            print(f"  Trovate {count} occorrenze valide nel file CSV")
            return dict(type_counts), True
            
    except Exception as e:
        print(f" Errore durante l'analisi del CSV {filepath}: {str(e)}")
    return {}, False

def count_types_in_excel(filepath):
    type_counts = defaultdict(int)
    try:
        wb = openpyxl.load_workbook(filepath, read_only=True)
        print(f"\nAnalisi di: {os.path.basename(filepath)}")
        
        for sheet in wb:
            try:
                header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
                if "type" not in header_row:
                    print(f" 'type' non trovato nelle intestazioni: {header_row}")
                    continue
                    
                type_col_idx = header_row.index("type") + 1
                count = 0
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if row and len(row) >= type_col_idx:
                        type_value = str(row[type_col_idx-1]).strip().upper()
                        if type_value == "IDQ":
                            type_value = "IdQ"
                        if type_value in COLUMN_ORDER or type_value == "IdQ":
                            type_counts[type_value] += 1
                            count += 1
                print(f"  Trovate {count} occorrenze valide nel foglio '{sheet.title}'")
                
            except Exception as sheet_error:
                print(f" Errore nel foglio {sheet.title}: {sheet_error}")
                
        return dict(type_counts), True
        
    except Exception as e:
        print(f" Errore durante l'apertura del file Excel: {str(e)}")
    return {}, False

def process_files(folder_path):
    supported_extensions = ('.xlsx', '.xls', '.xlsm', '.xlsb', '.csv')
    files = [f for f in os.listdir(folder_path) 
            if f.lower().endswith(supported_extensions)]
    
    if not files:
        print("\n Nessun file supportato trovato (accettati: .xlsx, .xls, .csv)")
        return None
    
    results = {}
    for filename in files:
        filepath = os.path.join(folder_path, filename)
        if filename.lower().endswith('.csv'):
            counts, success = count_types_in_csv(filepath)
        else:
            counts, success = count_types_in_excel(filepath)
            
        if success and counts:
            ordered_counts = {t: counts.get(t, 0) for t in COLUMN_ORDER}
            results[filename] = ordered_counts
    
    return results if results else None

def write_to_excel(results, output_file, folder_path):
    """Scrive i risultati in un file Excel nella cartella specificata"""
    try:
        # Costruisce il percorso completo del file di output nella cartella di input
        output_path = os.path.join(folder_path, output_file)
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Risultati"
        
        
        headers = ["Script"] + COLUMN_ORDER
        ws.append(headers)
        
      
        for filename, counts in results.items():
            
            script_name = os.path.basename(filename)
            if script_name.lower().endswith('.csv'):
                script_name = script_name[:-4]  
           
            script_name = script_name.replace('_', '\\')
            row = [script_name]
            for col in COLUMN_ORDER:
                row.append(counts[col])
            ws.append(row)
        
       
        for cell in ws[1]:
            cell.font = openpyxl.styles.Font(bold=True)
        
      
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        wb.save(output_path)
        print(f"\n File Excel salvato come: {output_path}")
        
    except Exception as e:
        print(f" Errore durante il salvataggio del file Excel: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Conta le occorrenze dei tipi nei file Excel/CSV')
    parser.add_argument('folder', help='Percorso della cartella contenente i file')
    parser.add_argument('--output', '-o', default='results.xlsx', 
                       help='Nome del file Excel di output (default: results.xlsx)')
    
    args = parser.parse_args()
    folder_path = args.folder
    output_file = args.output
    
    if not os.path.isdir(folder_path):
        print(f" Errore: '{folder_path}' non è una cartella valida")
        return
    
    print(f"\nAvvio analisi nella cartella: {os.path.abspath(folder_path)}")
    debug_folder_content(folder_path)
    
    try:
        results = process_files(folder_path)
        if results:
            # Calcola i totali per ogni tipo
            totali = defaultdict(int)
            for filename, counts in results.items():
                for tipo, valore in counts.items():
                    totali[tipo] += valore
            
            print("\n" + "="*80)
            print("RISULTATI DETTAGLIATI".center(80))
            print("="*80)
            print("{:<30}".format("File"), end="")
            for col in COLUMN_ORDER:
                print("{:>8}".format(col), end="")
            print("\n" + "-"*80)
            
            
            for filename, counts in results.items():
                print("{:<30}".format(filename[:30]), end="")
                for col in COLUMN_ORDER:
                    print("{:>8}".format(counts[col]), end="")
                print()
            
            
            print("-"*80)
            print("{:<30}".format("TOTALE"), end="")
            for col in COLUMN_ORDER:
                print("{:>8}".format(totali[col]), end="")
            print()
            print("="*80)
            
            
            write_to_excel(results, output_file, folder_path)

        else:
            print("\n Nessun dato valido trovato nei file")
    except Exception as e:
        print(f"\n Errore durante l'analisi: {str(e)}")

if __name__ == "__main__":
    main()