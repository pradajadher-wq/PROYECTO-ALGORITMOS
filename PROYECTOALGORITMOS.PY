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
ox.settings.log_console = False
ox.settings.use_cache   = True
ox.settings.timeout     = 60

# -------------------------------------------------------
# ELECTROLINERAS
# -------------------------------------------------------
electrolineras = [
    {"id": 1, "nombre": "Homecenter Bucaramanga",                  "municipio": "Bucaramanga",   "latitud": None,      "longitud": None,        "recargas": 0},
    {"id": 2, "nombre": "Centro Comercial Quinta Etapa",           "municipio": "Floridablanca", "latitud": 7.115271,  "longitud": -73.107654,  "recargas": 0},
    {"id": 3, "nombre": "Centro Comercial Cacique",                "municipio": "Bucaramanga",   "latitud": None,      "longitud": None,         "recargas": 0},
    {"id": 4, "nombre": "Centro Comercial Canaveral",              "municipio": "Floridablanca", "latitud": None,      "longitud": None,         "recargas": 0},
    {"id": 5, "nombre": "Estacion de Servicio Terpel Piedecuesta", "municipio": "Piedecuesta",   "latitud": 6.9980135, "longitud": -73.0521321, "recargas": 0},
    {"id": 6, "nombre": "Exito de la Rosita",                      "municipio": "Bucaramanga",   "latitud": 7.114483,  "longitud": -73.122846,  "recargas": 0},
    {"id": 7, "nombre": "Centro Comercial La Florida",             "municipio": "Floridablanca", "latitud": None,      "longitud": None,         "recargas": 0},
    {"id": 8, "nombre": "Promotores del Oriente via a Giron",      "municipio": "Giron",         "latitud": 7.085378,  "longitud": -73.164541,  "recargas": 0},
]

# -------------------------------------------------------
# PUNTOS DE RECORRIDO
# -------------------------------------------------------
puntos_recorrido = [
    {"id": 1,  "abreviatura": "UIS-CC",  "nombre": "Universidad Industrial de Santander Campus Central",  "municipio": "Bucaramanga",   "latitud": 7.140911,  "longitud": -73.119400},
    {"id": 2,  "abreviatura": "UIS-CF",  "nombre": "Universidad Industrial de Santander Campus Florida",  "municipio": "Floridablanca", "latitud": 7.061456,  "longitud": -73.088661},
    {"id": 3,  "abreviatura": "UIS-PTG", "nombre": "Parque Tecnologico Guatiguara Piedecuesta",           "municipio": "Piedecuesta",   "latitud": 6.994364,  "longitud": -73.065715},
    {"id": 4,  "abreviatura": "UIS-BUC", "nombre": "Universidad Industrial de Santander Bucarica",        "municipio": "Bucaramanga",   "latitud": 7.119359,  "longitud": -73.123479},
    {"id": 5,  "abreviatura": "CENFER",  "nombre": "CENFER Bucaramanga",                                  "municipio": "Bucaramanga",   "latitud": None,      "longitud": None},
    {"id": 6,  "abreviatura": "UNAB",    "nombre": "Universidad Autonoma de Bucaramanga",                 "municipio": "Bucaramanga",   "latitud": None,      "longitud": None},
    {"id": 7,  "abreviatura": "UTS",     "nombre": "Unidades Tecnologicas de Santander",                  "municipio": "Bucaramanga",   "latitud": None,      "longitud": None},
    {"id": 8,  "abreviatura": "UPB",     "nombre": "Universidad Pontificia Bolivariana Bucaramanga",      "municipio": "Bucaramanga",   "latitud": 7.0381473, "longitud": -73.0747789},
    {"id": 9,  "abreviatura": "PTAR",    "nombre": "Planta de Tratamiento Aguas Residuales Rio Frio",     "municipio": "Floridablanca", "latitud": 7.063217,  "longitud": -73.130492},
    {"id": 10, "abreviatura": "CATAY",   "nombre": "Sede Recreacional Catay",                             "municipio": "Giron",         "latitud": 6.9758282, "longitud": -73.0537166},
]

# -------------------------------------------------------
# VEHICULOS
# -------------------------------------------------------
vehiculos = [
    {
        "id"               : 1,
        "nombre"           : "Tesla Model S AWD",
        "gama"             : "alta",
        "autonomia_km"     : 590,
        "bateria_kwh"      : 95.0,
        "consumo_kwh_km"   : round(95.0 / 590, 4),
        "nivel_recarga_min": 10,
        "nivel_recarga_max": 20,
        "bateria_actual"   : 100.0,
        "total_recargas"   : 0,
        "km_recorridos"    : 0.0
    },
    {
        "id"               : 2,
        "nombre"           : "BYD Dolphin 60.4 kWh",
        "gama"             : "baja",
        "autonomia_km"     : 350,
        "bateria_kwh"      : 58.0,
        "consumo_kwh_km"   : round(58.0 / 350, 4),
        "nivel_recarga_min": 10,
        "nivel_recarga_max": 20,
        "bateria_actual"   : 100.0,
        "total_recargas"   : 0,
        "km_recorridos"    : 0.0
    }
]

# -------------------------------------------------------
# GEOCODIFICACION
# -------------------------------------------------------
def geocodificar_lugar(query):
    try:
        lat, lon = ox.geocode(query)
        return lat, lon
    except Exception as e:
        print(f"  [AVISO] No se pudo geocodificar '{query}': {e}")
        return None, None

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

geocodificar_electrolineras()
geocodificar_puntos()

# -------------------------------------------------------
# MENU PRINCIPAL
# -------------------------------------------------------
G = None
historial_recargas = []

opcion = 0
while opcion != 9:
    print("\n   SISTEMA DE ELECTROLINERAS - BGA")
    print("1. Ver electrolineras y puntos de recorrido")
    print("2. Ver vehiculos registrados")
    print("3. Cargar grafo de la red vial")
    print("4. Ejecutar simulacion de recorridos")
    print("5. Ver estadisticas de recargas")
    print("6. Predecir nuevas ubicaciones (IA)")
    print("7. Visualizar mapa")
    print("8. Guardar datos en archivos")
    print("9. Salir")

    opcion = input("Escoge una opcion 1-9: ").strip()
    if opcion.isdigit():
        opcion = int(opcion)
    else:
        print("Ingresa un numero valido")
        opcion = 0

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
            print("\nVehiculos:")
            for v in vehiculos:
                print(f"  [{v['id']}] {v['nombre']} | {v['gama']} gama | {v['autonomia_km']} km")

        case 3:
            print("\nCargando grafo del area metropolitana de Bucaramanga...")
            lugares = [
                "Bucaramanga, Santander, Colombia",
                "Floridablanca, Santander, Colombia",
                "Giron, Santander, Colombia",
                "Piedecuesta, Santander, Colombia"
                ]
            G = ox.graph_from_place(lugares, network_type="drive")
            print(f"Grafo cargado: {len(G.nodes)} nodos, {len(G.edges)} aristas")

        case 4:
            if G is None:
                print("\nPrimero debes cargar el grafo (opcion 3)")
            else:
                n = input("\nCuantos recorridos quieres simular por vehiculo?: ")
                if n.isdigit():
                    n = int(n)
                else:
                    print("Valor no valido, se usaran 5 recorridos por defecto")
                    n = 5

                print("\nIniciando simulacion de recorridos...")
                historial_recargas = []
                puntos_validos = [p for p in puntos_recorrido if p["latitud"] is not None]

                for vehiculo in vehiculos:   #Para tesla y BYD
                    vehiculo["bateria_actual"] = 100.0
                    vehiculo["total_recargas"] = 0
                    vehiculo["km_recorridos"] = 0.0
                    print(f"\n--vehiculo:{vehiculo['nombre']} ({vehiculo['gama']} gama)--")

                    for i in range(n):
                        origen  = random.choice(puntos_validos)
                        destino = random.choice(puntos_validos)

                        if origen["id"] == destino["id"]:
                            continue

                        #Convertir coordenadas a nodos
                        nodo_origen = ox.distance.nearest_nodes(G, origen["longitud"],  origen["latitud"])
                        nodo_destino = ox.distance.nearest_nodes(G, destino["longitud"], destino["latitud"])

                        #Calcular ruta mas corta
                        try:
                            distancia_m = nx.shortest_path_length(G, nodo_origen, nodo_destino, weight="length")
                            distancia_km = distancia_m / 1000
                            vehiculo["km_recorridos"] += distancia_km

                            #Descontar bateria
                            consumo = distancia_km * vehiculo["consumo_kwh_km"]
                            vehiculo["bateria_actual"] -= (consumo / vehiculo["bateria_kwh"]) * 100
                            print(f"  Recorrido {i+1}: {origen['abreviatura']} -- {destino['abreviatura']} | {distancia_km:.2f} km | Bateria: {vehiculo['bateria_actual']:.1f}%")

                            if vehiculo["bateria_actual"] <= random.uniform(10, 20):
                                elec_validas = [e for e in electrolineras if e["latitud"] is not None]
                                mas_cercana = min(elec_validas, key=lambda e: math.sqrt(
                                    (e["latitud"]  - destino["latitud"])**2 +
                                    (e["longitud"] - destino["longitud"])**2))
                                mas_cercana["recargas"] += 1
                                vehiculo["total_recargas"] += 1
                                vehiculo["bateria_actual"] = 100.0
                                print(f"  Recarga en: {mas_cercana['nombre']} | Recargas totales: {vehiculo['total_recargas']}")
                                historial_recargas.append({
                                    "vehiculo" : vehiculo["nombre"],
                                    "electrolinera": mas_cercana["nombre"],
                                    "municipio" : mas_cercana["municipio"],
                                    "latitud" : mas_cercana["latitud"],
                                    "longitud" : mas_cercana["longitud"]
                                })
                        except Exception:
                            print(f"  No se encontro ruta entre {origen['abreviatura']} y {destino['abreviatura']}")

                    print(f"\n  Total km recorridos: {vehiculo['km_recorridos']:.2f} km")
                    print(f"  Total recargas: {vehiculo['total_recargas']}")

        case 5:
            print("\n--- Estadisticas de recargas por electrolinera ---")
            for e in electrolineras:
                print(f"  {e['nombre']}: {e['recargas']} recargas")
            print("\n--- Estadisticas por vehiculo ---")
            for v in vehiculos:
                print(f"  {v['nombre']}: {v['total_recargas']} recargas | {v['km_recorridos']:.2f} km recorridos")
        case 9:
            print("Hasta luego!")

        case _:
            print("Opcion no valida, intente de nuevo")