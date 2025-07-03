import requests
import json
import os

# Configuración de la API
ORS_API_KEY = os.getenv('ORS_API_KEY', '5b3ce3597851110001cf6248ac6288334c9d47229f55815c7f18bad5')  # Usa tu API key de OpenRouteService
ORS_BASE_URL = "https://api.openrouteservice.org"

def geocode_ciudad(nombre_ciudad, pais=None):
    """Convierte un nombre de ciudad en coordenadas usando geocodificación"""
    params = {
        'api_key': ORS_API_KEY,
        'text': nombre_ciudad,
        'boundary.country': pais or ['CL', 'AR'],
        'size': 1
    }
    try:
        response = requests.get(f"{ORS_BASE_URL}/geocode/search", params=params)
        response.raise_for_status()
        data = response.json()
        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            return {'coordenadas': coords, 'nombre': data['features'][0]['properties']['name']}
        return None
    except Exception as e:
        print(f"Error en geocodificación: {str(e)}")
        return None

def calcular_ruta(origen_coord, destino_coord, transporte):
    """Calcula la ruta entre dos puntos usando el transporte especificado"""
    perfiles = {
        '1': 'driving-car',
        '2': 'cycling-regular',
        '3': 'foot-walking'
    }
    url = f"{ORS_BASE_URL}/v2/directions/{perfiles.get(transporte, 'driving-car')}"
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [origen_coord, destino_coord],
        "instructions": "true",
        "language": "es"
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al calcular ruta: {str(e)}")
        return None

def procesar_resultados_ruta(data_ruta):
    """Extrae y formatea los resultados de la ruta"""
    if not data_ruta or 'routes' not in data_ruta:
        return None
    
    resumen = data_ruta['routes'][0]['summary']
    distancia_km = resumen['distance'] / 1000
    distancia_millas = distancia_km * 0.621371
    duracion_segundos = resumen['duration']
    horas = int(duracion_segundos // 3600)
    minutos = int((duracion_segundos % 3600) // 60)
    
    narrativa = []
    for segmento in data_ruta['routes'][0]['segments']:
        for paso in segmento['steps']:
            narrativa.append(f"{paso['instruction']} ({paso['distance']:.0f} m)")
    
    return {
        'distancia_km': distancia_km,
        'distancia_millas': distancia_millas,
        'duracion': f"{horas}h {minutos}min",
        'narrativa': narrativa
    }

def main():
    print("Calculadora de Rutas Chile - Argentina")
    print("Presione 's' en cualquier momento para salir\n")
    
    while True:
        # Solicitar ciudades
        origen = input("Ciudad de Origen (Chile): ").strip()
        if origen.lower() == 's': return
        
        destino = input("Ciudad de Destino (Argentina): ").strip()
        if destino.lower() == 's': return
        
        # Selección de transporte
        print("\nMedios de transporte disponibles:")
        print("1: Automóvil")
        print("2: Bicicleta")
        print("3: Caminando")
        transporte = input("Seleccione opción (1-3): ").strip()
        if transporte.lower() == 's': return
        
        # Geocodificación
        coord_origen = geocode_ciudad(origen, ['CL'])
        coord_destino = geocode_ciudad(destino, ['AR'])
        
        if not coord_origen or not coord_destino:
            print("\nError: No se pudo encontrar una o ambas ciudades")
            continue
        
        # Cálculo de ruta
        ruta = calcular_ruta(
            coord_origen['coordenadas'],
            coord_destino['coordenadas'],
            transporte
        )
        
        if not ruta:
            print("\nError: No se pudo calcular la ruta")
            continue
        
        # Procesar resultados
        resultados = procesar_resultados_ruta(ruta)
        if not resultados:
            print("\nError: Datos de ruta inválidos")
            continue
        
        # Mostrar resultados
        print("\n" + "="*50)
        print(f"Ruta: {coord_origen['nombre']} (Chile) → {coord_destino['nombre']} (Argentina)")
        print(f"Distancia: {resultados['distancia_km']:.2f} km ({resultados['distancia_millas']:.2f} millas)")
        print(f"Duración del viaje: {resultados['duracion']}")
        
        print("\nNarrativa del viaje:")
        for i, paso in enumerate(resultados['narrativa'], 1):
            print(f"{i}. {paso}")
        
        print("="*50 + "\n")

if __name__ == "__main__":
    main()