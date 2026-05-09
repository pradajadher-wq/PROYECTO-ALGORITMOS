# =============================================================================
# PROYECTO INTEGRADOR 2026-1
# Sistema de electrolineras - Área metropolitana de Bucaramanga
# =============================================================================

# -------------------------------------------------------
# LIBRERÍAS
# -------------------------------------------------------

# Manejo de datos y archivos
import os
import json
import csv
import math
import random

# Grafos y mapa vial
import osmnx as ox
import networkx as nx

# Visualización
import folium
import plotly.express as px
import plotly.graph_objects as go

# Inteligencia Artificial
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

# -------------------------------------------------------
# CONFIGURACIÓN DE OSMnx
# -------------------------------------------------------
ox.settings.log_console = False   # No mostrar logs internos
ox.settings.use_cache   = True    # Guardar consultas en caché
ox.settings.timeout     = 60      # Tiempo máximo de espera (segundos)

# -------------------------------------------------------
# ELECTROLINERAS
# Cada una es un diccionario con sus datos principales.
# Las coordenadas se obtienen más adelante con OSMnx.
# -------------------------------------------------------

electrolineras = [
    {"id": 1, "nombre": "Homecenter Bucaramanga",                  "municipio": "Bucaramanga",   "latitud": None, "longitud": None, "recargas": 0},
    {"id": 2, "nombre": "Centro Comercial Quinta Etapa",           "municipio": "Floridablanca", "latitud": 7.115271,   "longitud": -73.107654,  "recargas": 0},
    {"id": 3, "nombre": "Centro Comercial Cacique",                "municipio": "Bucaramanga",   "latitud": None, "longitud": None, "recargas": 0},
    {"id": 4, "nombre": "Centro Comercial Canaveral",              "municipio": "Floridablanca", "latitud": None, "longitud": None, "recargas": 0},
    {"id": 5, "nombre": "Estacion de Servicio Terpel Piedecuesta", "municipio": "Piedecuesta",   "latitud": 6.9980135,  "longitud": -73.0521321, "recargas": 0},
    {"id": 6, "nombre": "Exito de la Rosita",                      "municipio": "Bucaramanga",   "latitud": 7.114483,   "longitud": -73.122846,  "recargas": 0},
    {"id": 7, "nombre": "Centro Comercial La Florida",             "municipio": "Floridablanca", "latitud": None,       "longitud": None,         "recargas": 0},
    {"id": 8, "nombre": "Promotores del Oriente via a Giron",      "municipio": "Giron",         "latitud": 7.085378,   "longitud": -73.164541,  "recargas": 0},
]

# -------------------------------------------------------
# GEOCODIFICACIÓN CON OSMnx
# ox.geocode() consulta Nominatim (OpenStreetMap) y
# retorna (latitud, longitud) para un lugar dado.
# -------------------------------------------------------

def geocodificar_lugar(query):
    """Retorna (latitud, longitud) de un lugar. Si falla retorna (None, None)."""
    try:
        lat, lon = ox.geocode(query)
        return lat, lon
    except Exception as e:
        print(f"  [AVISO] No se pudo geocodificar '{query}': {e}")
        return None, None


# -------------------------------------------------------
# PUNTOS FIJOS DE RECORRIDO
# Origen y destino de los vehículos en la simulación.
# -------------------------------------------------------

puntos_recorrido = [
    {"id": 1,  "abreviatura": "UIS-CC",  "nombre": "Universidad Industrial de Santander Campus Central",   "municipio": "Bucaramanga",   "latitud": 7.140911,  "longitud": -73.119400},
    {"id": 2,  "abreviatura": "UIS-CF",  "nombre": "Universidad Industrial de Santander Campus Florida",   "municipio": "Floridablanca", "latitud": 7.061456,  "longitud": -73.088661},
    {"id": 3,  "abreviatura": "UIS-PTG", "nombre": "Parque Tecnologico Guatiguara Piedecuesta",            "municipio": "Piedecuesta",   "latitud": 6.994364,  "longitud": -73.065715},
    {"id": 4,  "abreviatura": "UIS-BUC", "nombre": "Universidad Industrial de Santander Bucarica",         "municipio": "Bucaramanga",   "latitud": 7.119359,  "longitud": -73.123479},
    {"id": 5,  "abreviatura": "CENFER",  "nombre": "CENFER Bucaramanga",                                   "municipio": "Bucaramanga",   "latitud": None, "longitud": None},
    {"id": 6,  "abreviatura": "UNAB",    "nombre": "Universidad Autonoma de Bucaramanga",                  "municipio": "Bucaramanga",   "latitud": None, "longitud": None},
    {"id": 7,  "abreviatura": "UTS",     "nombre": "Unidades Tecnologicas de Santander",                   "municipio": "Bucaramanga",   "latitud": None, "longitud": None},
    {"id": 8,  "abreviatura": "UPB",     "nombre": "Universidad Pontificia Bolivariana Bucaramanga",       "municipio": "Bucaramanga",   "latitud": 7.0381473, "longitud": -73.0747789},
    {"id": 9,  "abreviatura": "PTAR",    "nombre": "Planta de Tratamiento Aguas Residuales Rio Frio",      "municipio": "Floridablanca", "latitud": 7.063217,    "longitud": -73.130492,  },
    {"id": 10, "abreviatura": "CATAY",   "nombre": "Sede Recreacional Catay",                              "municipio": "Giron",         "latitud": 6.9758282,   "longitud": -73.0537166, },
]


def geocodificar_electrolineras():
    """Llena las coordenadas de cada electrolinera consultando OpenStreetMap.
    Si ya tiene coordenadas asignadas manualmente, las respeta."""
    print("Geocodificando electrolineras...")
    for e in electrolineras:
        if e["latitud"] is not None:
            print(f"  ✓ [{e['id']}] {e['nombre']} → ({e['latitud']:.4f}, {e['longitud']:.4f}) [manual]")
            continue
        query = f"{e['nombre']}, {e['municipio']}, Colombia"
        lat, lon = geocodificar_lugar(query)
        e["latitud"]  = lat
        e["longitud"] = lon
        if lat:
            print(f"  ✓ [{e['id']}] {e['nombre']} → ({lat:.4f}, {lon:.4f})")


def geocodificar_puntos():
    """Llena las coordenadas de cada punto de recorrido consultando OpenStreetMap.
    Si ya tiene coordenadas asignadas manualmente, las respeta."""
    print("\nGeocodificando puntos de recorrido...")
    for p in puntos_recorrido:
        if p["latitud"] is not None:
            print(f"  ✓ [{p['id']}] {p['abreviatura']} → ({p['latitud']:.4f}, {p['longitud']:.4f}) [manual]")
            continue
        query = f"{p['nombre']}, {p['municipio']}, Colombia"
        lat, lon = geocodificar_lugar(query)
        p["latitud"]  = lat
        p["longitud"] = lon
        if lat:
            print(f"  ✓ [{p['id']}] {p['abreviatura']} → ({lat:.4f}, {lon:.4f})")
        else:
            print(f"  ✗ [{p['id']}] {p['abreviatura']} → NO ENCONTRADO (poner manual)")


# -------------------------------------------------------
# VERIFICACIÓN
# -------------------------------------------------------
if __name__ == "__main__":
    print("Librerías cargadas correctamente ✓")
    print(f"Electrolineras definidas: {len(electrolineras)}\n")
    geocodificar_electrolineras()