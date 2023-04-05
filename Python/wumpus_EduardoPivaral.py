#----------------------------------------------------------------
#    HUNT THE WUMPUS - Eduardo Pivaral Leal https://github.com/Epivaral/scripts
#    -----------------------------------------------
#         ===== Descripcion del proyecto =====
#  
# * Tablero de 20X20, donde el jugador se puede mover arriba, derecha, abajo, izquierda, 
#   excepto en los bordes donde solo hay 3 movimientos posibles,
#   o en las esquinas donde solo hay 2 movimientos posibles
#
# * El Agente puede ganar de 2 maneras:
#       - Encontrando el oro
#       - Matando al Wumpus
# 
# * Informacion de los items (todos se colocan en posiciones aleatorias):
#   
#   - ORO (x1) : Al encontrarlo GANAS el juego. No hay notificacion de su ubicacion en ninguna habitacion contigua.
#
#   - WUMPUS (x1) : Si lo encuentras te come y PIERDES el juego. al estar en una habitacion contigua recibes el mensaje "Sientes un olor terrible"
#                   Al estar en una habitacion contigua puedes matarlo de un disparo, si aciertas GANAS el juego, 
#                   si fallas tendras que regresar y seguir explorando por otro camino.
#                   si ya no cuentas con disparos tendras que regresar y seguir explorando por otro camino.
#
#   - Agujero (x4) : Si lo encuentras caes en el y PIERDES el juego. al estar en una habitacion contigua recibes el mensaje "Sientes una brisa"
#                    Al estar en una habitacion contigua, regresas y sigues explorando por otro camino.
#    
#   - Murcielago (x8): Si lo encuentras, te atrapa y te teletransporta a una ubicacion aleatoria de la cueva.
#                      Al estar en una habitacion contigua recibes el mensaje "Escuchas un aleteo"
#                      En este caso, si es la primera vez que visitas la habitacion contigua, sigues adelante con la exploracion (con el peligro de ser teletransportado)
#                      Para siguientes ocasiones, evitas esa habitacion si debes volver a visitarla.
#                      Si un murcielago te teletransporta, todo tu historial de exploracion se borra y deberas explorar toda la cueva de nuevo, 
#                      excepto por las amenazas previamente marcadas, estas si podras evitarlas en tu nueva exploracion.
#  
# * El Agente no cuenta con ninguna informacion al principio del juego y empieza en una ubicacion aleatoria
#    
# * La cueva se explora usando un algoritmo Depth First Search, y cuando estamos en una habitacion contigua a un peligro, regresamos al nodo padre de nuestro arbol de exploracion.
# 
# * El Agente guarda la siguiente informacion, la cual se va llenando conforme avanza en la exploracion:
#   - Nodos explorados
#   - Stack de "nodo anterior" para el algoritmo DFS (para que sepa como regresar en el arbol de busqueda)
#   - Nodos contiguos "peligrosos" (se evitan estas casillas en el futuro para minimizar el peligro)
# 
# * En el caso en que nuestro arbol de exploracion este vacio (estamos en el nodo inicial), nos movemos hacia la siguiente casilla disponible, con el peligro de caer en un peligro y perder el juego.
#  
# * El agente cuenta con 2 disparos para matar al Wumpus en caso de encontrarse en una habitacion contigua, el disparo se realiza hacia una habitacion aleatoria y puede acertarse o fallarse.
#   que se hace en cada caso se discute en la seccion de Wumpus. 
#
# * Existe una probabilidad muy alta (mas del 90% segun 2,200+ juegos simulados) de ganar el juego, ya que el algoritmo DFS es un algoritmo completo, 
#   y el agente unicamente pierde el juego en estos casos:
#   - El nodo inicial esta contiguo a una amenaza y al no tener un historial de nodos peligrosos, debe continuar la exploracion y el agente puede encontrar el peligro.
#   - Al ser teletransportado por un murcielago se borra el arbol de busqueda y se inicia la exploracion de nuevo (caso similar al de arriba).
#   - Cuando la exploracion ya esta muy avanzada y el numero de nodos pendientes es muy pequeño, y el agente por fuerza deba arriesgarse a continuar la exploracion por un nodo posiblemente peligroso.
#
#
# * Al iniciar el juego se presentan unicamente al espectador, la ubicacion de las amenazas y el oro (fondo azul), esta informacion es ignorada por el Agente
# * Durante el juego se va presentando la casilla actual, proximas casillas y si hay algun peligro
# * Luego se muestra la decision que el agente tomo para cada casilla
# * Al finalizar el juego se muestran las estadisticas del juego. Luego tenemos la opcion de repetir el juego.
#
#----------------------------------------------------------------
import colorama
from colorama import Fore


from operator import truediv
import random

Cx = 1
cave ={} #cueva de 20X20 para el proyecto
while Cx <= 800:
    #Creamos una cueva de 20X20 con los nodos que pueden ser visitados
    caveitem = []
    #Arriba
    if Cx -40 >0:
        caveitem.append(Cx -20)
    #Derecha
    if Cx%40!=0:
        caveitem.append(Cx+1)
    #Abajo
    if Cx+40<=800:
        caveitem.append(Cx+20)
    #Izquierda
    if (Cx+39)%40!=0:
        caveitem.append(Cx-1)
    cave[Cx]=caveitem
    Cx = Cx +1


#estadisticas del juego (victorias y partidas)
class Estadisticas(object):
    def __init__(self):
        self.Juegos = 0
        self.Victorias = 0

    #devuelve porcentaje de victorias
    def porcentaje(self):
        if self.Victorias == 0:
            return 0
        else:
            return (self.Victorias/self.Juegos)*100
    
    

#-----------------------------------------------
#             Clase del Agente
#-----------------------------------------------


class Agente(object):
    def __init__(self):
        self.nodosExplorados =[]
        self.nodosPeligro ={} #lista de nodos peligrosos, evitamos navegar por estos.
        self.player_pos = -1 # Posicion actual del agente
        self.posicion_previa =   []  #un stack de posiciones previas, nos ayudan a implementar nuestro algoritmo depht first search, ya que si quedamos trabados, regresamos varios niveles hasta encontrar
                                    #otro camino
        self.vecesReset =0 # veces que hemos sido transportados por murcielagos (se resetea nuestra exploracion)
        self.exploracionAcumulada = 0
        self.disparosDisponibles = 2


    def visitarNodo(self,pos,peligro):  
        #implementacion de Depth First Search
        #
        #
        # pos >>> lugares posibles a los que nos podemos mover segun el nodo actual

        if peligro>0:
            #si el nodo actual es peligroso, regresamos al nodo anterior y probamos otro nodo

            self.nodosPeligro[self.player_pos] = peligro #marcamos el nodo actual como peligroso

            if peligro >= 50: 
                #--------------------------
                #  Posible Wumpus, nos vamos a arriesgar a disparar, solo tenemos disparos limitados
                #  * Si tenemos disparos disponibles, probamos un tiro hacia una de las posibles habitaciones, aleatoriamente
                #   - Si acertamos, termina el juego y ganamos.
                #   - Si fallamos, regresamos a la habitacion segura anterior y continuamos la exploracion por otro rumbo
                #  * Si no tenemos disparos disponibles, simplemente probamos otra ruta de exploracion 
                #---------------------------
                if self.disparosDisponibles > 0:
                    print(Fore.YELLOW+"Probaremos un disparo, disparos disponibles: ",self.disparosDisponibles)
                    disparo = random.choice(pos) #regresamos un nodo aleatorio
                    self.disparosDisponibles += -1
                    print (Fore.MAGENTA+"Disparamos a la habitacion: ",disparo)
                    if WG.threats.get(disparo) == 'wumpus':
                        print(Fore.GREEN+"Mataste al temible Wumpus!",end=' ')
                        print(Fore.WHITE)
                        return 1000 #hemos ganado, salimos del juego victoriosos
                    else:
                        print(Fore.YELLOW+"Fallaste tu disparo! >>> ",end=' ')
                        if len(self.posicion_previa)>0:
                            print(Fore.YELLOW+"El Wumpus se ha salvado por hoy! - Regresamos a la habitacion previa e intentaremos otra ruta",end=' ')
                            print(Fore.WHITE)
                            return self.posicion_previa.pop() #Marcamos el nodo actual como peligroso y regresamos al nodo previo
                else:
                    print(Fore.YELLOW+"No mas disparos disponibles... Continuamos la exploracion por otra ruta",end=' ')
                    print(Fore.WHITE)
                    if len(self.posicion_previa)>0:
                        return self.posicion_previa.pop() #Marcamos el nodo actual como peligroso y regresamos al nodo previo

            elif peligro > 10: #puede ser un agujero, asi que regresamos y no nos aventuramos
                if len(self.posicion_previa)>0:
                    print(Fore.YELLOW+"Habitacion peligrosa, regresamos a la habitacion previa y probamos otro tunel",end=' ')
                    print(Fore.WHITE)
                    return self.posicion_previa.pop() #Marcamos el nodo actual como peligroso y regresamos al nodo previo

            elif peligro ==10: # es una casilla de murcielago, solo marcamos la casilla como peligrosa y nos aventuramos
                print(Fore.MAGENTA+"No nos asustan los murcielagos y seguimos adelante, unicamente los evitaremos en el futuro",end=' ')
                print(Fore.WHITE)


        
        encontrado = 0 # nos indica si el nodo actual aun cuenta con nodos sin explorar a los cual movernos

        posls ={}

        posls = pos

        random.seed()
        random.shuffle(posls) #no hay prioridad de movimiento, recorremos los posibles nodos aleatoriamente y tomamos el primero disponible
        

        for nodo in posls: #damos primero la prioridad a nodos no explorados aun
            if (nodo not in self.nodosExplorados) and (nodo not in self.nodosPeligro): #nuestro agente es miedoso y evitamos rutas peligrosas
                self.nodosExplorados.append(nodo)
                encontrado = 1 # si pudimos encontrar un nodo sin explorar
                self.posicion_previa.append(self.player_pos) #Guardamos la posicion previa
                break
        
        if encontrado == 0: 
            #significa que ya han sido explorados todos los nodos
            # tendremos que regresar aun mas y verificar nodos seguros, si volvemos a encontrar el mismo problema regresamos aun mas
            # este es el "core" del DFS
            print(Fore.LIGHTYELLOW_EX+"Todas las opciones ya exploradas y solo hay peligro mas adelante: Regresamos y probamos otro camino",end=' ')
            print(Fore.WHITE)
            if len(self.posicion_previa)>0: #validamos que el stack no este vacio
                return self.posicion_previa.pop() #tomamos el nodo anterior del stack y regresamos
            else: #si el stack de posiciones previas esta vacio, tendremos que explorar un nodo aleatorio proximo (posibilidad de perder el juego)
                return random.choice(posls) #regresamos un nodo aleatorio

        return nodo 


#---------------------------------------------------------------------------------
#             Clase del juego de Wumpus
# Codigo original tomado de: https://rosettacode.org/wiki/Hunt_the_Wumpus#Python
# Varias modificaciones fueron hechas al codigo original para este proyecto
#  - Cueva 20X20
#  - 
#---------------------------------------------------------------------------------    
 
class WumpusGame(object):
    
 
    def __init__(self):
        self.cave = cave
        self.threats = {}
        self.oro = -1 # posicion del oro para ganar el juego
        self.player_pos = -1
 

 
    def get_safe_rooms(self):
        return list(set(self.cave.keys()).difference(self.threats.keys()))
 
 
    def populate_cave(self):
        # --------------------------
        # 8 murcielagos
        # 4 agujeros
        # 1 wumpus
        # Es posible agregar mas amenazas, simplemente hay que agregarlos en la lista abajo:
        # --------------------------
        for threat in ['bat', 'bat','bat', 'bat','bat','bat', 'bat','bat', 'pit', 'pit', 'pit', 'pit', 'wumpus']:
            pos = random.choice(self.get_safe_rooms())
            self.threats[pos] = threat
        self.player_pos = random.choice(self.get_safe_rooms())
        self.oro = random.choice(self.get_safe_rooms()) #colocamos el oro en una posicion segura aleatoria


 
    def enter_room(self, room_number):
        
        print("Entrando a la habitacion >>> {} -- ".format(room_number),end=' ')
        
        if self.threats.get(room_number) == 'bat':
            # -------------------------------------------------------------------------------------
            #  Si encontramos a un murcielago, este nos transporta a una habitacion aleatoria
            #  y perdemos nuestro historial de exploracion, asi como nuestro stack de posiciones previas (ya que obviamente iniciamos una nueva exploracion)
            #  tan solo conservamos nuestro listado de habitaciones peligrosas ya que esta informacion ya es conocida por el agente y puede probar
            #  nuevas rutas en la posicion nueva a donde el murcielago lo transporte.
            #  Ya que no tenemos historial de exploracion, es posible perder el juego al caer en una trampa
            # -------------------------------------------------------------------------------------
            print(Fore.RED+">>>> Encontraste un murcielago, este te transportara a una habitacion aleatoria, tu historial de exploracion se reiniciara, pero tu informacion de peligros se mantiene")
            print(Fore.WHITE)
            new_pos = random.choice(self.get_safe_rooms())
            
            resultadoMurcielago = self.enter_room(new_pos)

            # Ya que estamos en un nodo aleatorio, reseteamos los nodos explorados
            # y el stack de posiciones previas, unicamente guardamos las casillas con peligros,
            # asi que esto es como un "soft Reset", donde no tenemos informacion de exploracion, pero ya contamos con informacion de peligro

            AgenteWG.vecesReset += 1 #incrementamos el contador para las estadisticas
            AgenteWG.exploracionAcumulada += len(AgenteWG.nodosExplorados)

            #Borramos el historial de exploracion, ya que se reinicia
            AgenteWG.posicion_previa =[]
            AgenteWG.nodosExplorados =[]
            AgenteWG.player_pos =new_pos
                        
            return new_pos,resultadoMurcielago[1]
        
        elif self.threats.get(room_number) == 'wumpus':
            print(Fore.RED +"El Wumpus te ha comido")
            return -1,0 #Perdiste el juego

        elif self.threats.get(room_number) == 'pit':
            print(Fore.RED +"Caiste en un pozo")
            return -1,0 #Perdiste el juego

        elif room_number == self.oro:
            print(Fore.GREEN+"Has encontrado el oro")
            return 1000,0 #Ganaste el juego    

        
        puntaje =0 #variable que nos sirve para puntar la amenaza de una habitacion
 
        
        for i in self.cave[room_number]:
            threat = self.threats.get(i)
            if threat == 'bat':
                print(Fore.RED +"!!!! PELIGRO !!!! >>>> Escuchas un aleteo ",end=' ')
                puntaje = puntaje +10
            elif threat == 'pit':
                print(Fore.RED +"!!!! PELIGRO !!!! >>>> Sientes una brisa ",end=' ')
                puntaje = puntaje +20
            elif threat == 'wumpus':
                puntaje = puntaje +50
                print(Fore.RED +"!!!! PELIGRO !!!! >>>> Sientes un olor terrible ",end=' ')

        if puntaje>0:
            print(Fore.WHITE,end=' ')
        
        return room_number, puntaje
 
 
    
 
    def gameloop(self):
        
        self.populate_cave()
        print()	
        print(colorama.Back.BLUE)
        print(Fore.LIGHTWHITE_EX + "===============")

        print("HUNT THE WUMPUS")
        print()	
        print("DEBUG: Localizacion de las amenazas: {}".format(self.threats))
        print()
        print("DEBUG: El oro esta en la siguiente ubicacion: {}".format(self.oro))
        
        print("===============")
        print()	
        print(colorama.Style.RESET_ALL)


        resultado = self.enter_room(self.player_pos)

        AgenteWG.player_pos = self.player_pos
        AgenteWG.nodosExplorados.append(self.player_pos)
     
        while 1:
            print("Siguientes tuneles: ",end = ' ')
            print(self.cave[self.player_pos])
 
            #inpt = self.get_players_input()		# Modo Jugador
            inpt = AgenteWG.visitarNodo(self.cave[self.player_pos],resultado[1])  #modo Maquina
            if inpt !=1000:
                print("---")								# Visual separation of rounds.
                resultado = self.enter_room(inpt)
                self.player_pos = resultado[0]
                AgenteWG.player_pos = self.player_pos
            else:
                self.player_pos = inpt
            
            if self.player_pos == 1000: # Agente gano el juego
                EstadisticaWG.Victorias +=1
                print(' ')
                print(Fore.GREEN+"!!!!!!!!    G A N A S T E    !!!!!!!!")
            elif self.player_pos == -1:  #Agente perdio el juego
                print(' ')
                print(Fore.RED +"Perdiste! :( ")				

            if self.player_pos == 1000 or self.player_pos == -1:
                # Estadisticas del agente al finalizar el juego
                # ---------------------------------------------
                print(' ')
                print(Fore.LIGHTBLUE_EX+"*** Estadisticas del Agente ***")
                print('------------')
                print("Juegos totales: ",end=' ')
                print(EstadisticaWG.Juegos)
                print("Victorias: ",end=' ')
                print(EstadisticaWG.Victorias)
                print("Porcentaje exito: ",end=' ')
                print(f"{EstadisticaWG.porcentaje():.2f}%")
                print('------------')
                print("Nodos explorados (Ultima exploracion): ",end=' ')
                print(len(AgenteWG.nodosExplorados))
                print()
                print("Nodos explorados (Acumulado): ",end=' ')
                print(AgenteWG.exploracionAcumulada+len(AgenteWG.nodosExplorados))
                print()
                print("Disparos disponibles: ",end=' ')
                print(AgenteWG.disparosDisponibles)
                print()
                print(Fore.LIGHTRED_EX+"Veces que se reinicio la busqueda (Causado por Murcielagos): ",end=' ')
                print(AgenteWG.vecesReset)
                print()
                print(Fore.LIGHTYELLOW_EX+"Nodos Marcados como peligrosos: ",end=' ')
                print(AgenteWG.nodosPeligro)
                print()
                print(Fore.LIGHTBLUE_EX+"Stack de exploracion Depth firsth search: ",end=' ')
                print(len(AgenteWG.posicion_previa))
                print(AgenteWG.posicion_previa)
                print(Fore.WHITE)
                break 
 
        
#-----------------------------------------------------------
#                    Ciclo main
#-----------------------------------------------------------
 
if __name__ == '__main__':
# ciclo principal del juego
   # flag para repetir o no el juego
    repetir =1
    EstadisticaWG = Estadisticas()
    

    while repetir:

        EstadisticaWG.Juegos +=1

        AgenteWG = Agente() #instanciamos un nuevo agente

        WG = WumpusGame()
        WG.gameloop()
        
        while 1:
            print()
            print("-------------------------------------")
            inpt = input(colorama.Back.LIGHTWHITE_EX+Fore.BLACK+">>> Jugar de nuevo? Y/N >>> ")
            try:
                opcion = str(inpt).lower()
                assert opcion in ['y', 'n']
                break
            except (ValueError, AssertionError):
                print("Solo Y o N permitido")

        # Terminar el juego si no se desea repetir        
        if opcion == 'n':
            repetir =0
            break
