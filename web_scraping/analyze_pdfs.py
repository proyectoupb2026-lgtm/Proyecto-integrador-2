import os
import glob
import re
from pypdf import PdfReader
import pandas as pd

base_dir = r'c:\Users\pc\OneDrive\Desktop\Proyecto integrador 2\Base_datos'
pdfs = sorted(glob.glob(os.path.join(base_dir, '*.pdf')))

print(f"Total PDFs encontrados en Base_datos: {len(pdfs)}")

data = []
doi_pattern = re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')

for pdf_path in pdfs:
    fname = os.path.basename(pdf_path)
    
    # Extraer año del nombre del archivo (ej. _2020_, _2025_)
    year_match = re.search(r'_(19\d{2}|20\d{2})_', fname)
    year = int(year_match.group(1)) if year_match else None
    
    # Extraer editorial / fuente del nombre del archivo
    source_match = re.search(r'_(19\d{2}|20\d{2})_(.+)\.pdf$', fname)
    publisher = source_match.group(2).replace('-', ' ') if source_match else 'Desconocida'

    title_approx = fname.split('_')[0].replace('-', ' ')

    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        full_text = ''
        for p in reader.pages[:min(4, num_pages)]:
            full_text += (p.extract_text() or '') + '\n'
            
        # Buscar DOI en el texto completo
        dois = doi_pattern.findall(full_text)
        cleaned_dois = [d.rstrip('.,;)') for d in dois]
        doi = cleaned_dois[0] if cleaned_dois else None
        
        # Buscar año en el texto si no está en el nombre
        if not year:
            years_found = [int(y) for y in re.findall(r'\b(20[0-2]\d)\b', full_text)]
            year = max(years_found) if years_found else 2020
            
        data.append({
            'filename': fname,
            'titulo': title_approx,
            'year': year,
            'editorial': publisher,
            'num_pages': num_pages,
            'doi': doi,
            'has_doi': doi is not None,
            'text_sample': full_text[:500].replace('\n', ' ')
        })
    except Exception as e:
        data.append({
            'filename': fname,
            'titulo': title_approx,
            'year': year or 2020,
            'editorial': publisher,
            'num_pages': 0,
            'doi': None,
            'has_doi': False,
            'error': str(e)
        })

df = pd.DataFrame(data)

print(f"\n--- ANÁLISIS DE AÑOS (ÍNDICE DE PRICE) ---")
print(df['year'].value_counts().sort_index(ascending=False))

# Últimos 5 años (2022 a 2026)
recientes = df[df['year'] >= 2022]
price_index = (len(recientes) / len(df)) * 100
print(f"\nÍndice de Price (Artículos 2022-2026): {price_index:.2f}% ({len(recientes)} / {len(df)} artículos)")

print(f"\n--- ANÁLISIS DE DOIs ---")
print(f"Con DOI detectable: {df['has_doi'].sum()} / {len(df)}")
print(f"Sin DOI visible: {len(df) - df['has_doi'].sum()}")

missing_doi = df[~df['has_doi']]['filename'].tolist()
print("\nPDFs sin DOI visible identificado automáticamente:")
for m in missing_doi:
    print(f" - {m}")
