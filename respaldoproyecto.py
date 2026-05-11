import os
import json
import csv
import math
import random
import osmnx as ox
import networkx as nx
import folium
import plotly.express as px
import plotly.graph_objects as go
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
    try:
        lat, lon = ox.geocode(query)
        return lat, lon
    except Exception as e:
        print(f"  [AVISO] No se pudo geocodificar '{query}': {e}")
        return None, None

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
vehiculos = [
    {
        "id"               : 1,
        "nombre"           : "Tesla Model S AWD",
        "gama"             : "alta",
        "autonomia_km"     : 590,
        "bateria_kwh"      : 95.0,
        "consumo_kwh_km"   : round(95.0 / 590, 4),  # 0.1610 kWh/km
        "nivel_recarga_min": 10,                     # % mínimo de batería
        "nivel_recarga_max": 20,                     # % máximo de batería
        "bateria_actual"   : 100.0,                  # estado inicial
        "total_recargas"   : 0,
        "km_recorridos"    : 0.0
    },
    {
        "id"               : 2,
        "nombre"           : "BYD Dolphin 60.4 kWh",
        "gama"             : "baja",
        "autonomia_km"     : 350,
        "bateria_kwh"      : 58.0,
        "consumo_kwh_km"   : round(58.0 / 350, 4),  # 0.1657 kWh/km
        "nivel_recarga_min": 10,
        "nivel_recarga_max": 20,
        "bateria_actual"   : 100.0,
        "total_recargas"   : 0,
        "km_recorridos"    : 0.0
    }
]
geocodificar_electrolineras()
geocodificar_puntos()
# -------------------------------------------------------
# VARIABLE GLOBAL DEL GRAFO
# Se llena cuando el usuario escoge la opción 3
# -------------------------------------------------------
grafo = None

# -------------------------------------------------------
# FUNCIONES DEL GRAFO
# -------------------------------------------------------

def cargar_grafo():
    """Descarga la red vial del área metropolitana de Bucaramanga."""
    print("\nDescargando red vial del área metropolitana...")
    print("Esto puede tardar unos segundos...\n")

    lugares = [
        "Bucaramanga, Santander, Colombia",
        "Floridablanca, Santander, Colombia",
        "Giron, Santander, Colombia",
        "Piedecuesta, Santander, Colombia"
    ]

    lista_grafos = []
    for lugar in lugares:
        try:
            g = ox.graph_from_place(lugar, network_type="drive")
            lista_grafos.append(g)
            print(f"  ✓ {lugar} cargado")
        except Exception as e:
            print(f"  ✗ No se pudo cargar {lugar}: {e}")

    if not lista_grafos:
        print("  [ERROR] No se pudo cargar ningún grafo.")
        return None

    grafo_completo = nx.compose_all(lista_grafos)
    print(f"\n  ✓ Grafo completo:")
    print(f"    Nodos (intersecciones) : {len(grafo_completo.nodes)}")
    print(f"    Aristas (vías)         : {len(grafo_completo.edges)}")
    return grafo_completo


def nodo_mas_cercano(grafo, latitud, longitud):
    """Retorna el nodo del grafo más cercano a unas coordenadas dadas."""
    return ox.nearest_nodes(grafo, longitud, latitud)


def asignar_nodos(grafo):
    """Asigna a cada electrolinera y punto de recorrido su nodo más cercano en el grafo."""
    print("\n  Asignando nodos a electrolineras...")
    for e in electrolineras:
        if e["latitud"] is not None:
            e["nodo"] = nodo_mas_cercano(grafo, e["latitud"], e["longitud"])
            print(f"    ✓ [{e['id']}] {e['nombre']} → nodo {e['nodo']}")
        else:
            e["nodo"] = None
            print(f"    ✗ [{e['id']}] {e['nombre']} → sin coordenadas")

    print("\n  Asignando nodos a puntos de recorrido...")
    for p in puntos_recorrido:
        if p["latitud"] is not None:
            p["nodo"] = nodo_mas_cercano(grafo, p["latitud"], p["longitud"])
            print(f"    ✓ [{p['id']}] {p['abreviatura']} → nodo {p['nodo']}")
        else:
            p["nodo"] = None
            print(f"    ✗ [{p['id']}] {p['abreviatura']} → sin coordenadas")
opcion = 0
while opcion != 9:
    print("   SISTEMA DE ELECTROLINERAS - BGA")
    print("1. Ver electrolineras y puntos de recorrido")
    print("2. Ver vehículos registrados")
    print("3. Cargar grafo de la red vial")
    print("4. Ejecutar simulación de recorridos")
    print("5. Ver estadísticas de recargas")
    print("6. Predecir nuevas ubicaciones (IA)")
    print("7. Visualizar mapa")
    print("8. Guardar datos en archivos")
    print("9. Salir")
    opcion = int(input("Escoja una opcion 1-9: "))
    match opcion:
        case 1:
            print(f"\nElectrolineras: {len(electrolineras)}")
            for e in electrolineras:
                if e["latitud"] is not None:
                    print(f"  [{e['id']}] {e['nombre']} - {e['municipio']} ({e['latitud']:.4f}, {e['longitud']:.4f})")
                else:
                    print(f"  [{e['id']}] {e['nombre']} - {e['municipio']} (sin coordenadas)")
            print(f"\nPuntos de recorrido: {len(puntos_recorrido)}")
            for p in puntos_recorrido:
                if p["latitud"] is not None:
                    print(f"  [{p['id']}] {p['abreviatura']} - {p['nombre']} ({p['latitud']:.4f}, {p['longitud']:.4f})")
                else:
                    print(f"  [{p['id']}] {p['abreviatura']} - {p['nombre']} (sin coordenadas)")
        case 2:
            print("\nVehículos:")
            for v in vehiculos:
                print(f"  [{v['id']}] {v['nombre']} | {v['gama']} gama | {v['autonomia_km']} km")
        case 3:
            grafo = cargar_grafo()
            if grafo is not None:
                asignar_nodos(grafo)
                print("\n  ✓ Red vial lista para la simulación.")
        case 9:
            print("Hasta luego!")
        case _:
            print("Opción no válida, intente de nuevo")
            