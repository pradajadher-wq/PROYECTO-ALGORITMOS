import os
import json
import csv
import math
import random
import osmnx as ox
import networkx as nx
import folium
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
# VARIABLES DE CONTROL GLOBAL
# -------------------------------------------------------
G = None
historial_recargas = []
viajes_simulados = []  

opcion = 0
while opcion != 9:
    print("\n   SISTEMA DE ELECTROLINERAS - BGA")
    print("1. Ver electrolineras y puntos de recorrido")
    print("2. Ver vehiculos registrados")
    print("3. Cargar grafo de la red vial")
    print("4. Ejecutar simulacion de recorridos")
    print("5. Ver estadisticas de recargas")
    print("6. Predecir nuevas ubicaciones (IA)")
    print("7. Visualizar mapa geografico interactivo con Pesos (HTML)")
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
                viajes_simulados = []  
                puntos_validos = [p for p in puntos_recorrido if p["latitud"] is not None]

                G_undirected = G.to_undirected()

                for vehiculo in vehiculos:
                    vehiculo["bateria_actual"] = 100.0
                    vehiculo["total_recargas"] = 0
                    vehiculo["km_recorridos"] = 0.0
                    print(f"\n--vehiculo:{vehiculo['nombre']} ({vehiculo['gama']} gama)--")

                    for i in range(n):
                        origen  = random.choice(puntos_validos)
                        destino = random.choice(puntos_validos)

                        if origen["id"] == destino["id"]:
                            continue

                        nodo_origen = ox.distance.nearest_nodes(G, origen["longitud"],  origen["latitud"])
                        nodo_destino = ox.distance.nearest_nodes(G, destino["longitud"], destino["latitud"])

                        try:
                            ruta_nodos = nx.shortest_path(G_undirected, nodo_origen, nodo_destino, weight="length")
                            distancia_m = nx.shortest_path_length(G_undirected, nodo_origen, nodo_destino, weight="length")
                            
                            distancia_km = distancia_m / 1000
                            vehiculo["km_recorridos"] += distancia_km

                            viajes_simulados.append({
                                "tipo": "principal",
                                "origen_lbl": origen["abreviatura"],
                                "destino_lbl": destino["abreviatura"],
                                "peso_km": round(distancia_km, 2),
                                "nodos": ruta_nodos
                            })

                            consumo = distancia_km * vehiculo["consumo_kwh_km"]
                            vehiculo["bateria_actual"] -= (consumo / vehiculo["bateria_kwh"]) * 100
                            print(f"  Recorrido {i+1}: {origen['abreviatura']} -- {destino['abreviatura']} | {distancia_km:.2f} km | Bateria: {vehiculo['bateria_actual']:.1f}%")

                            umbral = random.uniform(10, 20)
                            if vehiculo["bateria_actual"] <= umbral:
                                elec_validas = [e for e in electrolineras if e["latitud"] is not None]
                                mas_cercana = min(elec_validas, key=lambda e: math.sqrt(
                                    (e["latitud"]  - destino["latitud"])**2 +
                                    (e["longitud"] - destino["longitud"])**2))
                                
                                mas_cercana["recargas"] += 1
                                vehiculo["total_recargas"] += 1
                                vehiculo["bateria_actual"] = 100.0
                                
                                nodo_elec = ox.distance.nearest_nodes(G, mas_cercana["longitud"], mas_cercana["latitud"])
                                ruta_recarga_nodos = nx.shortest_path(G_undirected, nodo_destino, nodo_elec, weight="length")
                                dist_recarga_km = nx.shortest_path_length(G_undirected, nodo_destino, nodo_elec, weight="length") / 1000
                                
                                viajes_simulados.append({
                                    "tipo": "recarga",
                                    "origen_lbl": destino["abreviatura"],
                                    "destino_lbl": " ".join(mas_cercana["nombre"].split()[:2]),
                                    "peso_km": round(dist_recarga_km, 2),
                                    "nodos": ruta_recarga_nodos
                                })

                                print(f"  -> ¡Desvío por Batería Baja! Ruta más corta a electrolinera: {dist_recarga_km:.2f} km")
                                print(f"  Recarga en: {mas_cercana['nombre']} | Recargas totales: {vehiculo['total_recargas']}")
                                historial_recargas.append({
                                    "vehiculo" : vehiculo["nombre"],
                                    "electrolinera": mas_cercana["nombre"],
                                    "municipio" : mas_cercana["municipio"],
                                    "latitud" : mas_cercana["latitud"],
                                    "longitud" : mas_cercana["longitud"]
                                })
                        except nx.NetworkXNoPath:
                            print(f"  No se encontro ruta topologica entre {origen['abreviatura']} y {destino['abreviatura']}")
                        except Exception as e:
                            print(f"  Error en simulacion: {e}")

                    print(f"\n  Total km recorridos: {vehiculo['km_recorridos']:.2f} km")
                    print(f"  Total recargas: {vehiculo['total_recargas']}")

        case 5:
            simulacion_hecha = any(v["total_recargas"] > 0 or v["km_recorridos"] > 0 for v in vehiculos)
            if not simulacion_hecha:
                print("\nPrimero debes ejecutar la simulacion (opcion 4)")
            else:
                print("\n--- Estadisticas de recargas por electrolinera ---")
                for e in electrolineras:
                    print(f"  {e['nombre']}: {e['recargas']} recargas")
                print("\n--- Estadisticas por vehiculo ---")
                for v in vehiculos:
                    print(f"  {v['nombre']}: {v['total_recargas']} recargas | {v['km_recorridos']:.2f} km recorridos")

        case 6:
            print("\n--- Modelo Predictivo de Demanda (IA) ---")
            if not historial_recargas:
                print("  Primero ejecuta la simulacion (opcion 4)")
            else:
                conteo = {}
                for r in historial_recargas:
                    n = r["electrolinera"]
                    conteo[n] = conteo.get(n, 0) + 1

                X, y, nombres = [], [], []
                for e in electrolineras:
                    if e["latitud"] is not None:
                        uso = conteo.get(e["nombre"], 0)
                        X.append([e["latitud"], e["longitud"], uso])
                        y.append(uso)
                        nombres.append(e["nombre"])

                if len(X) < 4:
                    print("  Se necesitan mas datos. Simula mas recorridos.")
                else:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

                    scaler = StandardScaler()
                    X_train_s = scaler.fit_transform(X_train)
                    X_test_s  = scaler.transform(X_test)

                    rf = RandomForestRegressor(n_estimators=100, random_state=42)
                    rf.fit(X_train, y_train)
                    pred_rf = rf.predict(X_test)

                    lr = LinearRegression()
                    lr.fit(X_train, y_train)
                    pred_lr = lr.predict(X_test)

                    svm = SVR(kernel="rbf")
                    svm.fit(X_train_s, y_train)
                    pred_svm = svm.predict(X_test_s)

                    print("\n  Resultados de modelos:")
                    print(f"  Random Forest   - MAE: {mean_absolute_error(y_test, pred_rf):.3f}")
                    print(f"  Regresion Lineal- MAE: {mean_absolute_error(y_test, pred_lr):.3f}")

                    print("\n  Prediccion de demanda futura (x2 vehiculos):")
                    X_futuro = [[x[0], x[1], x[2]*2] for x in X]
                    pred_futuro = rf.predict(X_futuro)
                    for nombre, p in sorted(zip(nombres, pred_futuro), key=lambda x: x[1], reverse=True):
                        print(f"  {nombre:<40}: {int(p)} recargas estimadas")

        case 7:
            print("\n--- Visualizacion: Mapa Geografico con Pesos de Rutas (HTML) ---")
            if G is None:
                print("  Primero debes cargar el grafo (opcion 3)")
            else:
                print("  Generando mapa vial completo con pesos de aristas...")
                nodos_gdf, aristas_gdf = ox.graph_to_gdfs(G)

                mapa = aristas_gdf.explore(
                    color="#FFFFFFBB",
                    style_kwds={"weight": 1.0, "opacity": 0.4},
                    tiles="CartoDB positron",
                    tooltip=False,
                    popup=False
                )

                coords_puntos = {p["abreviatura"]: (p["latitud"], p["longitud"]) for p in puntos_recorrido if p["latitud"] is not None}
                for e in electrolineras:
                    if e["latitud"] is not None:
                        coords_puntos[" ".join(e["nombre"].split()[:2])] = (e["latitud"], e["longitud"])

                if viajes_simulados:
                    for v in viajes_simulados:
                        coordenadas_linea = []
                        
                        if v["origen_lbl"] in coords_puntos:
                            coordenadas_linea.append(coords_puntos[v["origen_lbl"]])
                        
                        if v["nodos"]:
                            for nodo in v["nodos"]:
                                coordenadas_linea.append((G.nodes[nodo]['y'], G.nodes[nodo]['x']))
                        
                        if v["destino_lbl"] in coords_puntos:
                            coordenadas_linea.append(coords_puntos[v["destino_lbl"]])

                        if len(coordenadas_linea) >= 2:
                            color_ruta = "#859FF6" if v["tipo"] == "principal" else "#FF75FF"
                            
                            folium.PolyLine(
                                locations=coordenadas_linea,  
                                color=color_ruta,
                                weight=3.5,
                                opacity=0.4
                            ).add_to(mapa)

                            mid_idx = len(coordenadas_linea) // 2
                            lat_mid, lon_mid = coordenadas_linea[mid_idx]

                            texto_peso = f"{v['peso_km']} km"
                            folium.map.Marker(
                                [lat_mid, lon_mid],
                                icon=folium.features.DivIcon(
                                    html=f'<div style="font-size: 10pt; font-weight: bold; color: {color_ruta}; '
                                         f'white-space: nowrap; background: transparent; border: none; box-shadow: none; '
                                         f'text-shadow: -1px -1px 0 #FFF, 1px -1px 0 #FFF, -1px 1px 0 #FFF, 1px 1px 0 #FFF;">'
                                         f'{texto_peso}</div>',
                                    icon_size=(60, 20),
                                    icon_anchor=(30, 10),
                                    class_name=""
                                )
                            ).add_to(mapa)

                for e in electrolineras:
                    if e["latitud"] is not None:
                        folium.Marker(
                            location=[e["latitud"], e["longitud"]],
                            popup=f"<b>{e['nombre']}</b><br>Recargas: {e['recargas']}",
                            tooltip=e["nombre"],
                            icon=folium.Icon(color="green", icon="bolt", prefix="fa")
                        ).add_to(mapa)

                for p in puntos_recorrido:
                    if p["latitud"] is not None:
                        folium.CircleMarker(
                            location=[p["latitud"], p["longitud"]],
                            radius=6,
                            color="#FF4500",
                            fill=True,
                            fill_color="#FF8C00",
                            fill_opacity=0.9,
                            popup=p["nombre"],
                            tooltip=p["abreviatura"]
                        ).add_to(mapa)

                mapa.save("mapa_electrolineras.html")
                print("  ✓ Archivo HTML guardado exitosamente: mapa_electrolineras.html")

                nombres_e = [" ".join(e["nombre"].split()[:2]) for e in electrolineras]
                recargas_e = [e["recargas"] for e in electrolineras]
                fig = go.Figure(go.Bar(x=nombres_e, y=recargas_e, marker_color="green"))
                fig.update_layout(title="Recargas por Electrolinera", xaxis_title="Electrolinera", yaxis_title="Numero de Recargas")
                fig.show()

        case 8:
            if not historial_recargas:
                print("\nNo hay datos para guardar. Ejecuta la simulacion (opcion 4) primero.")
            else:
                print("\n--- Guardar Datos en Archivos ---")
                os.makedirs("resultados", exist_ok=True)

                with open("resultados/recargas.csv", "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["vehiculo", "electrolinera", "municipio", "latitud", "longitud"])
                    for r in historial_recargas:
                        writer.writerow([r["vehiculo"], r["electrolinera"], r["municipio"], r["latitud"], r["longitud"]])
                print("  Guardado: resultados/recargas.csv")

                with open("resultados/electrolineras.json", "w", encoding="utf-8") as f:
                    json.dump(electrolineras, f, ensure_ascii=False, indent=2)
                print("  Guardado: resultados/electrolineras.json")

                with open("resultados/estadisticas.txt", "w", encoding="utf-8") as f:
                    f.write("ESTADISTICAS DEL SISTEMA\n=" * 40 + "\n")
                    for e in electrolineras: f.write(f"{e['nombre']}: {e['recargas']} recargas\n")
                    f.write("\n")
                    for v in vehiculos: f.write(f"{v['nombre']}: {v['total_recargas']} recargas | {v['km_recorridos']:.2f} km\n")
                print("  Guardado: resultados/estadisticas.txt")
                
                try:
                    import openpyxl
                    wb=openpyxl.Workbook()
                    ws1 = wb.active; ws1.title = "Recargas"
                    ws1.append(["Vehiculo", "Electrolinera", "Municipio", "Latitud", "Longitud"])
                    for r in historial_recargas: ws1.append([r["vehiculo"], r["electrolinera"], r["municipio"], r["latitud"], r["longitud"]])
                    
                    ws2 = wb.create_sheet("Estadisticas")
                    ws2.append(["Electrolinera", "Municipio", "Recargas"])
                    for e in electrolineras: ws2.append([e["nombre"], e["municipio"], e["recargas"]])
                    
                    ws3 = wb.create_sheet("Vehiculos")
                    ws3.append(["Vehiculo", "Gama", "Total Recargas", "Km Recorridos"])
                    for v in vehiculos: ws3.append([v["nombre"], v["gama"], v["total_recargas"], round(v["km_recorridos"], 2)])
                    
                    wb.save("resultados/datos.xlsx")
                    print("  Guardado: resultados/datos.xlsx")
                except ImportError:
                    print("Para guardar xlsx instala openpyxl: pip install openpyxl")
                print("\n  Todos los archivos guardados en 'resultados/'")        

        case 9:
            print("Hasta luego!")
        case _:
            print("Opcion no valida, intente de nuevo")
    
