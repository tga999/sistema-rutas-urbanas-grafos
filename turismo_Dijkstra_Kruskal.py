import networkx as nx
import matplotlib.pyplot as plt
from math import radians, sin, cos, sqrt, atan2
import matplotlib.patches as mpatches


# ------------- COORDENADAS DE LOS NODOS -------------

coords = {
    # Nodos principales
    "Teatro Colón": (-34.6007594228903, -58.383330521437024),
    "Casa Rosada": (-34.60792525829755, -58.37023112707848),
    "Obelisco": (-34.60368733712313, -58.381618498483455),
    "Abasto Shopping Center": (-34.60236239059351, -58.41083491999935),
    "Museo Nacional de Bellas Artes": (-34.583856877892494, -58.392961489012954),
    "El Cabildo": (-34.60872374789531, -58.373712404352354),

    # Nodos secundarios
    "Rosedal de Palermo": (-34.570491690779214, -58.417268919089814),
    "Estadio Monumental": (-34.54550190200598, -58.44966608521886),
    "Plaza de Mayo": (-34.60823415696745, -58.37229395358708),
    "Barrio Chino": (-34.55614254848038, -58.45062427507607),
    "Puente de la Mujer": (-34.60788944636865, -58.3651535374229),

    # Nodos terciarios
    "Punto A": (-34.67168391883699, -58.70168490670971),  # Coordenadas Ateneo de padua
    "Punto B": (-34.67025280307836, -58.74599925886482), # Coordenadas Campus UNO
    "Punto C": (-34.65119582511954, -58.77667857263204), # Coordenadas Universidad de Moreno
    "Punto D": (-34.658026750214354, -58.653018007724434) # Coordenadas "Gorki Grana"
}

# ------------- NODOS DEL GRAFO -------------
nodo_central = "Obelisco"

# Los nodos principales representan los edificios emblemáticos de Buenos Aires
nodos_principales = ["Teatro Colón", "Casa Rosada", "Obelisco", "Abasto Shopping Center", "Museo Nacional de Bellas Artes", "El Cabildo"]

# Los nodos secundarios representan lugares turísticos populares
nodos_secundarios = ["Rosedal de Palermo", "Estadio Monumental", "Plaza de Mayo", "Barrio Chino", "Puente de la Mujer"]

# Los nodos terciarios representan algunos puntos específicos de zona oeste.
nodos_terciarios = ["Punto A", "Punto B", "Punto C", "Punto D"]

# !-------------- CAMINOS CERRADOS PARA LAS E-BIKES -------------
# Definimos los caminos cerrados para las e-bikes, que son los lugares donde no se puede circular.
caminos_cerrados = [("Teatro Colón", "Casa Rosada"),("Abasto Shopping Center", "Museo Nacional de Bellas Artes"),("El Cabildo", "Rosedal de Palermo")]



# ----- CALCULAR DISTANCIA ENTRE LOS NODOS -----
# Con las distancias entre los nodos, podemos calcular el costo de las aristas (edges) del grafo.

def haversine(coord1, coord2):
    """
    Calcula la distancia Haversine entre dos puntos de la Tierra especificados en grados.    
    :param coord1: Tuple con latitud y longitud del primer punto (lat1, lon1).
    :param coord2: Tuple con latitud y longitud del segundo punto (lat2, lon2).
    :return: Distancia entre los dos puntos en metros.
    """
    R = 6378000  # Radio de la Tierra en metros
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    
    # Calculamos las distancias a partir de la diferencia entre las latitudes y longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Aplicamos la fórmula Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return round(R * c)  # Distancía en metros

# Función booleana para verificar si dos nodos están dentro del radio
def es_cercano(coord1, coord2, radio):
    distancia = haversine(coord1,coord2)
    return distancia <= radio

# ------------- CREACIÓN DEL GRAFO -------------

# El costo de los nodos está determinado por la distancia entre ellos (metros)

# Los nodos proncipales estarán conectados entre sí

# Los nodos secundarios estarán conectados a los nodos principales más cercanos

# Las casas de los alumnos estarán conectadas a los nodos principales y secundarios más cercanos

def unir_casas_con_nodo_central(grafo, nodo_central, nodos_terciarios):
    for casa in nodos_terciarios:
        distancia = haversine(coords[nodo_central], coords[casa])
        grafo.add_edge(nodo_central, casa, weight=distancia)

def unir_nodos_principales_secundarios(grafo, nodos_principales, nodos_secundarios, radio):
    for nodo_sec in nodos_secundarios:
        for nodo_pri in nodos_principales:
            if es_cercano(coords[nodo_sec], coords[nodo_pri], radio):  
                distancia = haversine(coords[nodo_sec], coords[nodo_pri])
                grafo.add_edge(nodo_sec, nodo_pri, weight=distancia)



#--------------CREAR GRAFO CON RADIO -------------
def crear_grafo_con_radio(radio):
    grafo = nx.Graph()

    # Primero agregamos todos los nodos
    for nodo in coords:
        grafo.add_node(nodo)

    # Conectamos casas con nodo central
    unir_casas_con_nodo_central(grafo, nodo_central, nodos_terciarios)

    #Conectamos nodos secundarios con principales
    unir_nodos_principales_secundarios(grafo, nodos_principales, nodos_secundarios, radio)

    #Conectamos entre todos los nodos principales (completo entre ellos)
    for i in range(len(nodos_principales)):
        for j in range(i + 1, len(nodos_principales)):
            nodo1, nodo2 = nodos_principales[i], nodos_principales[j]
            if es_cercano(coords[nodo1], coords[nodo2], radio):
                distancia = haversine(coords[nodo1], coords[nodo2])
                grafo.add_edge(nodo1, nodo2, weight=distancia)

    return grafo


#--------------------------------------------------------------------------------------
# !--------------------- DIBUJAR GRAFO ---------------------

def dibujar_grafo(grafo, camino_optimo=None):
    """
    Dibuja el grafo con diferentes colores para los tipos de nodos y resalta caminos especiales.
    
    :param grafo: Grafo de NetworkX a dibujar
    :param camino_optimo: Lista de nodos que forman el camino óptimo (opcional)
    """
    # Usar coordenadas reales como posición de los nodos
    pos = {nodo: (coords[nodo][1], coords[nodo][0]) for nodo in grafo.nodes}  # (lon, lat)

    # Tamaño de la figura
    plt.figure(figsize=(14, 10))

    # Dibujar nodos con colores y tamaños personalizados
    colores_nodos = []
    tamaños_nodos = []
    
    for nodo in grafo.nodes:
        if nodo in nodos_principales:
            colores_nodos.append('red')
            tamaños_nodos.append(1800)
        elif nodo in nodos_secundarios:
            colores_nodos.append('blue')
            tamaños_nodos.append(1600)
        else:  # nodos terciarios (puntos)
            colores_nodos.append('green')
            tamaños_nodos.append(1400)

    # Dibujar todas las aristas accesibles en color gris claro
    aristas_accesibles = []
    aristas_cerradas = []
    
    for arista in grafo.edges():
        es_cerrada = False
        for camino_cerrado in caminos_cerrados:
            if arista == camino_cerrado or arista == (camino_cerrado[1], camino_cerrado[0]):
                es_cerrada = True
                break
        
        if es_cerrada:
            aristas_cerradas.append(arista)
        else:
            aristas_accesibles.append(arista)
    
    # Dibujar caminos accesibles en color gris claro
    if aristas_accesibles:
        nx.draw_networkx_edges(grafo, pos, edgelist=aristas_accesibles, 
                              edge_color='lightgray', width=2, alpha=0.7)
    
    # Dibujar caminos cerrados en color rojo con línea discontinua
    if aristas_cerradas:
        nx.draw_networkx_edges(grafo, pos, edgelist=aristas_cerradas, 
                              edge_color='red', width=3, alpha=0.8, style='dashed')
    
    # Si hay un camino óptimo, dibujarlo en color verde grueso
    if camino_optimo and len(camino_optimo) > 1:
        aristas_camino_optimo = [(camino_optimo[i], camino_optimo[i+1]) 
                                for i in range(len(camino_optimo)-1)]
        nx.draw_networkx_edges(grafo, pos, edgelist=aristas_camino_optimo, 
                              edge_color='darkgreen', width=4, alpha=0.9)

    # Dibujar nodos
    nx.draw_networkx_nodes(grafo, pos, node_color=colores_nodos, 
                          node_size=tamaños_nodos, alpha=0.8)
    
    # Dibujar etiquetas de nodos
    nx.draw_networkx_labels(grafo, pos, font_size=8, font_weight='bold')
    
    # Dibujar etiquetas de pesos en las aristas
    edge_labels = {(u, v): f"{d['weight']}m" for u, v, d in grafo.edges(data=True)}
    nx.draw_networkx_edge_labels(grafo, pos, edge_labels, font_size=6)
    
    # Crear leyenda
    leyenda_elementos = [
        mpatches.Patch(color='red', label='Nodos Principales'),
        mpatches.Patch(color='blue', label='Nodos Secundarios'), 
        mpatches.Patch(color='green', label='Puntos Terciarios'),
        mpatches.Patch(color='lightgray', label='Caminos Accesibles'),
        mpatches.Patch(color='red', label='Caminos Cerrados (E-bikes)'),
    ]
    
    if camino_optimo:
        leyenda_elementos.append(mpatches.Patch(color='darkgreen', label='Camino Óptimo'))
    
    plt.legend(handles=leyenda_elementos, loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.title("Sistema Inteligente de Rutas Urbanas para E-bikes en Buenos Aires")
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.tight_layout()
    plt.show()
#--------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------------

# ------------- MOSTRAR CASOS DE PRUEBA -------------
def mostrar_casos_de_prueba(grafo, nombre):

    print(f"\n⛳ Casos de prueba para: {nombre}")
    casos = [
        ("Punto D", "Casa Rosada"),
        ("Punto A", "Museo Nacional de Bellas Artes"),
        ("Barrio Chino", "Plaza de Mayo"),
    ]
    for origen, destino in casos:

        print(f"\n🔍 Evaluando camino desde {origen} hasta {destino}...")
        subgrafo = nx.Graph()
        subgrafo.add_nodes_from(grafo.nodes(data=True))  # 👈 Copiamos los nodos primero
        # Agregamos solo las aristas habilitadas
        # (es decir, aquellas que no están bloqueadas)
        for u, v, d in grafo.edges(data=True):
            if d.get("habilitado", True):
                subgrafo.add_edge(u, v, **d)

        # Intentamos encontrar el camino más corto usando Dijkstra:
        try:
            camino = nx.dijkstra_path(subgrafo, source=origen, target=destino, weight="weight")
            costo = nx.dijkstra_path_length(subgrafo, source=origen, target=destino, weight="weight")
            print(f"✅ Camino más corto encontrado: {camino}")
            print(f"🧮 Costo total del recorrido: {costo} metros")
            dibujar_grafo(grafo, camino_optimo=camino)
        except nx.NetworkXNoPath:
            print("❌ No hay un camino accesible entre estos dos puntos. La ruta está bloqueada o desconectada.")
            dibujar_grafo(grafo, camino_optimo=None)

        print("-" * 60)

#-----------------------------------------------------------------------------------------------------------------------

#aplicando kruskal para encontrar el arbol de expansion minima
def aplicar_kruskal(grafo):
    
    pos = nx.spring_layout(grafo)
    T = nx.minimum_spanning_tree(grafo, algorithm="kruskal")
    
    # Dibujar árbol
    nx.draw(T, pos, with_labels=True, node_color='lightgreen', node_size=1500, edge_color='orange', width=2)
    
    # Etiquetas de pesos en las aristas
    edge_labels = {(u, v): d['weight'] for u, v, d in T.edges(data=True)}
    nx.draw_networkx_edge_labels(T, pos, edge_labels=edge_labels)
    
    # Crear leyenda con mpatches
    nodo_patch = mpatches.Patch(color='lightgreen', label='Nodo')
    arista_patch = mpatches.Patch(color='orange', label='Arista MST')
    plt.legend(handles=[nodo_patch, arista_patch], loc='best')
    
    plt.title("Árbol de Expansión Mínima (Kruskal)")
    plt.axis('off')  # Opcional: ocultar ejes
    plt.show()

#-----------------------------------------------------------------------------------------------------------------------

#CREAMOS GRAFO 1 CON TODOS LOS NODOS Y RADIO DE 7000 METROS
grafo_1 = crear_grafo_con_radio(7000)
#CREAMOS GRAFO 2 CON TODOS LOS NODOS Y RADIO DE 5000 METROS
grafo_2 = crear_grafo_con_radio(5000)

#dibujamos el grafo 1
dibujar_grafo(grafo_1)
#aplicamos Kruskal para encontrar el árbol de expansión mínima
aplicar_kruskal(grafo_1)

#dibujamos el grafo 2
dibujar_grafo(grafo_2)
#aplicamos Kruskal para encontrar el árbol de expansión mínima
aplicar_kruskal(grafo_2)

#------ aplicamos casos de prueba para los dos grafos usando dikjstra teniendo en cuenta los caminos con bloqueos

#aplicamos 5 casos de prueba para el grafo 1
mostrar_casos_de_prueba(grafo_1, "Grafo 1 con radio de 7000 metros")
#aplicamos 4 casos de prueba para el grafo 2
mostrar_casos_de_prueba(grafo_2, "Grafo 2 con radio de 5000 metros")