import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderRateLimited
import time
import re

csv_path = r"C:\Users\pc\OneDrive\Desktop\Proyecto integrador 2\bade_datos_accidentes\accidentes_verificados_actualizados.csv"

def clean_address(addr):
    if not isinstance(addr, str):
        return ""
    # Remove text in parenthesis like "(Casco Urbano / Sector en investigación)"
    addr = re.sub(r'\(.*?\)', '', addr)
    addr = addr.replace('Montería', '').strip()
    return addr

def geocode_address(geolocator, address, municipio):
    query = f"{address}, {municipio}, Córdoba, Colombia"
    query = query.replace(" ,", ",").replace(", ,", ",")
    try:
        location = geolocator.geocode(query, timeout=10)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderRateLimited) as e:
        if isinstance(e, GeocoderRateLimited):
            print("Límite de API alcanzado, esperando 10 segundos...")
            time.sleep(10)
    return None, None

def main():
    print("Leyendo CSV...")
    df = pd.read_csv(csv_path)
    
    geolocator = Nominatim(user_agent="simulador_aph_geocoder_monteria")
    
    # We only geocode if latitud is the default '8.7508' or empty/nan
    total_processed = 0
    total_found = 0
    
    for idx, row in df.iterrows():
        lat = str(row.get('latitud', ''))
        
        # Check if it has a default centroid latitud (8.7508) or no latitud
        if not lat or lat == 'nan' or '8.7508' in lat or '8.8844' in lat or '8.1722' in lat or '8.8786' in lat or '9.3736' in lat:
            
            # Prefer barrio_sector, then direccion_especifica, then direccion_lugar
            addr = ""
            if pd.notna(row.get('barrio_sector')) and str(row['barrio_sector']).strip():
                addr = str(row['barrio_sector'])
            elif pd.notna(row.get('direccion_especifica')) and str(row['direccion_especifica']).strip():
                addr = str(row['direccion_especifica'])
            elif pd.notna(row.get('direccion_lugar')) and str(row['direccion_lugar']).strip():
                addr = str(row['direccion_lugar'])
                
            addr_clean = clean_address(addr)
            
            if len(addr_clean) > 3:
                muni = str(row.get('municipio', 'Montería'))
                if pd.isna(muni) or not muni: muni = 'Montería'
                
                print(f"Geocodificando id {row['id']}: '{addr_clean}', {muni}")
                lat_new, lon_new = geocode_address(geolocator, addr_clean, muni)
                
                if lat_new and lon_new:
                    df.at[idx, 'latitud'] = lat_new
                    df.at[idx, 'longitud'] = lon_new
                    df.at[idx, 'precision_geo'] = 'Alta (Geocodificado OpenStreetMap)'
                    total_found += 1
                else:
                    df.at[idx, 'precision_geo'] = 'Baja (Sin Resultados en Mapa - ' + str(row['precision_geo']) + ')'
                
                total_processed += 1
                time.sleep(1.5)  # Respetar límite más estricto
                
    print(f"Completado. {total_found} de {total_processed} direcciones procesadas fueron encontradas.")
    df.to_csv(csv_path, index=False)
    print("CSV guardado y actualizado con éxito.")

if __name__ == '__main__':
    main()
