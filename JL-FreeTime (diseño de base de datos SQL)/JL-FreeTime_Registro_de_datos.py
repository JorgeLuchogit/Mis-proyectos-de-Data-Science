import sqlite3
import pandas as pd
from datetime import datetime

'''-----------------------------------------------------------------------
                     FUNCIONES PREELIMINARES
-----------------------------------------------------------------------'''

def queries_function(query, commit=False):
	"""-------------------------------------------------------------------
	Función para hacer queries.

	query:  Código SQL. 
	commit: Indica que debe hacerse un commit cuando toma al valor True.
	-------------------------------------------------------------------"""
	cursor = conn.cursor()
	cursor.execute(query)
	
	if commit == True:
		conn.commit()
		
	cursor.close()

def validar_sino(input_mensaje):
    """------------------------------------------------------------------- 
    Función para hacer y validar un input de tipo 1:si y 0:no. El resultado
    debe asignarse a una variable:

    variable = validar_sino('Ingrese el valor de variable')
    --------------------------------------------------------------------"""
    while True:
        try: 
            aux = int(input(f'\n{input_mensaje}\n'))
            if aux != 1 and aux != 0:
                print('El valor tiene que ser 0 o 1')
                continue    
        except ValueError as e: print(f'\nNo se ingresó un valor entero\nERROR: {e}')
        else: break       
    return aux

def validar_time(input_mensaje):
    """------------------------------------------------------------------- 
    Función para hacer y validar un input de tipo entero. El resultado
    debe asignarse a una variable:

    variable = validar_time('Ingrese el valor de variable')
    --------------------------------------------------------------------"""
    while True:
        try: 
            aux = int(input(f'\n{input_mensaje}\n'))
            if aux < 0:
                print('Se requieren valores positivos')
                continue
        except ValueError as e: print(f'\nNo se ingresó un valor entero\nERROR: {e}')
        else: break
    return aux 

def mostrar(nombre_tabla, campos='*'):
    """------------------------------------------------------------------- 
    Función para imprimir una tabla de la base de datos.

    nombre_tabla:  nombre de la tabla deseada
    campos:        string con los nombres de los campos separados por comas
    --------------------------------------------------------------------"""
    query = f''' 
            SELECT {campos} FROM {nombre_tabla};
        '''
    Tabla_info = pd.read_sql_query(query, conn)
    print(f'\nRegistro de {nombre_tabla}:\n\n{Tabla_info}')

def obtener_ultimo(tabla, campo):
    """------------------------------------------------------------------- 
    Función para obtener el último valor registrado en una tabla
    --------------------------------------------------------------------"""
    query = f''' 
        SELECT {campo} from {tabla} ORDER BY {campo} DESC
        LIMIT 1
    ''' 
    return pd.read_sql_query(query, conn).iloc[0].iloc[0]

def sesion_primera(nombre_tabla):
    """------------------------------------------------------------------- 
    Función que determina si es el primer registro del día en una tabla
    --------------------------------------------------------------------"""
    Id_fecha_sesion = obtener_ultimo(tabla=nombre_tabla, campo='Id_fecha')
    return (primer == True or (primer == False and Id_fecha != Id_fecha_sesion))
    
def Objetivo_completado(tabla, id_va, id_va_nombre ):
    """------------------------------------------------------------------- 
    Función para marcar una tarea completada

    tabla:          nombre de la tabla
    id_va_nombre:   campo de la tabla
    id_va:          valor del campo
    --------------------------------------------------------------------"""
    query =f''' 
                UPDATE {tabla}
                SET Completado = 1
                WHERE {id_va_nombre} = {id_va}
            '''
    queries_function(query=query)

'''-------------------------------------------------------------------'''
'''-----------RUTINA PARA REGISTRAR SESIÓN DE MÚSICA------------------'''
def registrar_cancion(id_banda, nombre_cancion, duracion, completado):
    """------------------------------------------------------------------- 
    Función para registrar la información de una sesión musical
    --------------------------------------------------------------------"""
    cursor = conn.cursor()
    query = f''' 
        INSERT INTO Canciones (Id_banda, Nombre_canción, Duración, Completado)
        VALUES ({id_banda}, ?, ?, ?);
    '''
    cursor.execute(query, (nombre_cancion, duracion, completado))
    conn.commit()
    cursor.close()

def sesion_musica():    
    print('\n<< Registro de sesión musical >>')
    
    teo = validar_time('Minutos de Teoría:')
    pra = validar_time('Minutos de prácrtica:')
    apr = validar_time('Minutos aprendiendo una nueva canción:')
    
    if sesion_primera('Música') == True:
        print('\n--> Es la primer sesión del día\n')   
        query = f'''
            INSERT INTO Música (Id_fecha, Teoría, Práctica, Aprender_canción)
            VALUES ({Id_fecha}, {teo}, {pra}, {apr});
        '''
    else:
        print('\n--> No es la primer sesión del día\n')

        query = f'''
            UPDATE Música
            SET Teoría = Teoría + {teo}, 
                Práctica = Práctica + {pra},
                Aprender_canción = Aprender_canción + {apr}
            WHERE Id_fecha = {Id_fecha}
        '''
    queries_function(query=query)
    Id_musica = obtener_ultimo(tabla='Música', campo='Id_música')

    if apr > 0:
        mostrar('canciones')
        nueva_cancion = validar_sino('¿Lo que aprendiste es de una canción no registrada? (1:si, 0:no):')

        if nueva_cancion == 1:
            mostrar('Bandas')
            nueva_banda = validar_sino('¿La canción es de una banda no registrada? (1:si, 0:no):')

            if nueva_banda == 1:
                nombre_banda = input('\nIngresa el nombre de la banda:\n')
                genero = input('\nsu género musical:\n')
                pais = input('\nde qué país es:\n')

                query = f''' 
                    INSERT INTO Bandas (Nombre_banda, Género, País)
                    VALUES ('{nombre_banda}', '{genero}', '{pais}')
                '''
                queries_function(query=query)
                Id_banda = obtener_ultimo(tabla='Bandas', campo='Id_banda')

            else: Id_banda = validar_time('\nSegún la tabla, ¿Cuál es el Id de la banda?\n')
            
            nombre_cancion = input('\nIngresa el nombre de la canción:\n')
            duracion = validar_time('\nsu duración:\n')

            registrar_cancion(id_banda=Id_banda, nombre_cancion=nombre_cancion, duracion=duracion, completado=0)
            Id_cancion = obtener_ultimo(tabla='Canciones', campo='Id_canción')

        else: Id_cancion = validar_time('Según la tabla, ¿Cuál es el Id de la canción?\n')

        query = f''' 
            INSERT INTO Música_detalles (Id_música, Id_canción, Id_aspecto)
            VALUES ({Id_musica}, {Id_cancion}, 3)
        '''
        queries_function(query=query)

    if pra > 0:    
        print('\n--> Respecto a lo practiado:\n')
        mostrar('Canciones')

        Id_cancion = input('\nSegún la tabla, ¿Cuál es el Id de la canción que practicaste?\n')

        query = f''' 
            INSERT INTO Música_detalles (Id_música, Id_canción, Id_aspecto)
            VALUES ({Id_musica}, {Id_cancion}, 2)
        '''
        queries_function(query=query)
        
        if validar_sino('\n¿Lograste dominarla por completo? (1:si, 0:no)\n') == 1:
            Objetivo_completado(tabla='Canciones', id_va = Id_cancion, id_va_nombre='id_canción')

    print('\nTerminó el registro de sesión músical\n')
     
'''---------RUTINA PARA REGISTRAR SESIÓN DE ACTIVIDAD FÍSICA----------'''
def sesion_ejercicio():
    print('\n<< Registro de sesión de actividad física >>\n')

    fue = validar_time('Minutos dedicados a la fuerza:')
    fle = validar_time('Minutos dedicados a la flexibilidad:')
    res = validar_time('Minutos dedicados a la resistencia:')
    tec = validar_time('Minutos dedicados a la técnica:')
    
    if sesion_primera('Actividad_física') == True:
        print('\n--> Es la primer sesión del día')
        query = f'''
            INSERT INTO Actividad_física (Id_fecha, Fuerza, Flexibilidad, Resistencia, Técnica)
            VALUES ({Id_fecha}, {fue}, {fle}, {res}, {tec});
        '''
    else:
        print('\n--> No es la primer sesión del día')
        query = f'''
            UPDATE Actividad_física
            SET Fuerza = Fuerza + {fue}, 
                Flexibilidad = Flexibilidad + {fle},
                Resistencia = Resistencia + {res},
                Técnica = Técnica + {tec}
            WHERE Id_fecha = {Id_fecha}
        '''
    queries_function(query=query)
    Id_actividad_física = obtener_ultimo(tabla='Actividad_física', campo='Id_actividad_física')
    Id_actividad_física_progreso = obtener_ultimo(tabla='Progreso', campo='Id_actividad_física')

    if Id_actividad_física == Id_actividad_física_progreso:
        print('\nEl progreso de hoy ya se registró\n')
    else:
        if validar_sino('¿Quieres registrar tu progreso? (1:si, 0:no):') == 1:
            abds = validar_time('Máximo de abdominales sin parar:')
            sent = validar_time('Máximo de sentadillas:')
            laga = validar_time('Máximo de lagartijas:')
            resi = validar_time('Segundos en los que hiciste la rutina de resistencia:')

            query = f''' 
                    INSERT INTO Progreso (Id_actividad_física, Abdominales, Sentadillas, Lagartijas, Rutina_de_resistencia)
                    VALUES ({Id_actividad_física}, {abds}, {sent}, {laga}, {resi})
                 '''
            queries_function(query=query)

          
    print('\n Terminó el registro de sesión de actividad física')

'''---------RUTINA PARA REGISTRAR SESIÓN DE ESTUDIO-------------------'''
def sesion_estudio():
    print('\n<< Registro de sesión de Estudio >>')
    
    fis = validar_time('Minutos dedicados a Física:')
    mat = validar_time('Minutos dedicados a Matemáticas:')
    bio = validar_time('Minutos dedicados a las Ciencias Biológicas:')
    otr = validar_time('Minutos dedicados a otra rama:')
    lista_var =[fis, mat, bio, otr]
    lista_var_nom =['Física', 'Matemáticas', 'Ciencias biológicas', 'Otro']
    
    if sesion_primera('Estudio') == True:
        print('\n--> Es la primer sesión del día\n')   
        query = f'''
            INSERT INTO Estudio (Id_fecha, Física, Matemáticas, Ciencias_Biológicas, Otro)
            VALUES ({Id_fecha}, {fis}, {mat}, {bio}, {otr});
        '''
    else:
        print('\n--> No es la primer sesión de estudio del día\n')
        query = f'''
            UPDATE Estudio
            SET Física = Física + {fis}, 
                Matemáticas = Matemáticas + {mat},
                Ciencias_Biológicas = Ciencias_Biológicas + {bio},
                Otro = Otro + {otr}
            WHERE Id_fecha = {Id_fecha}
        '''
    queries_function(query=query)
    Id_estudio = obtener_ultimo(tabla='Estudio', campo='Id_estudio') 
    mostrar('materias')

    for i in range(len(lista_var)): 

        if lista_var[i] > 0:
            nueva_materia = validar_sino(f'\n¿Estudiaste una materia de {lista_var_nom[i]} no registrada? (1:si, 0:no):')
 
            if nueva_materia == 1:

                if i == 3:
                    mostrar('Ramas')
                    nueva_rama = validar_sino('¿La rama de estudio es nueva? (1:si, 0:no):')

                    if nueva_rama == 1:
                        nombre_rama = input('\nIngresa el nombre de la rama:\n')
                        cursor = conn.cursor()
                        query = f''' 
                            INSERT INTO Ramas (Nombre_rama)
                            VALUES (?)
                        '''
                        cursor.execute(query, (nombre_rama,))
                        cursor.close()

                        Id_rama = obtener_ultimo(tabla='Ramas', campo='Id_rama')

                    else: Id_rama = validar_time('\nSegún la tabla, ¿Cuál es el Id de la rama?\n')
                
                else: Id_rama = i+1
                
                nombre_materia = input('\nIngresa el nombre de la materia :\n')

                cursor = conn.cursor()
                query = f''' 
                INSERT INTO Materias (Id_rama, Nombre_materia)
                VALUES ({Id_rama}, ?)
                '''
                cursor.execute(query, (nombre_materia,))
                cursor.close()

                Id_materia = obtener_ultimo(tabla='Materias', campo='Id_materia ')

            else: Id_materia = validar_time('Según la tabla, ¿Cuál es el Id de la materia que estudiaste?')

            query = f''' 
                    INSERT INTO Estudio_detalles (Id_estudio, Id_materia)
                    VALUES ({Id_estudio}, {Id_materia})
                    '''
            queries_function(query=query)
  
    print('\nTerminó el registro de sesión de estudio\n')
    
'''---------RUTINA PARA REGISRAR SESIÓN DE LECTURA--------------------'''
def sesion_lectura():
    print('\n<< Registro de sesión de lectura >>')

    tiempo = validar_time('¿Cuántos minútos leíste?')
    mostrar('Libros')

    if validar_sino('Terminaste un libro hoy? (1:si, 0:no)') == 1:
        Id_libro = validar_time('Según la tabla ¿Cuál es el id del libro que terminaste?')
        Objetivo_completado(tabla='Libros', id_va= Id_libro, id_va_nombre='Id_libro')
    else:
        if validar_sino('¿Comenzaste un libro nuevo? (1:si, 0:no)') == 1:
            Tit = input('\n¿Cuál es el titulo?\n')
            aut = input('\n¿El autor?\n')

            cursor = conn.cursor()
            query = f''' 
                INSERT INTO Libros (Nombre_libro, Autor, Completado)
                VALUES (?,?,0)
            '''
            cursor.execute(query, (Tit, aut))
            cursor.close()
            Id_libro = obtener_ultimo(tabla='Libros', campo='Id_libro')

        else:
            Id_libro = validar_time('Según la tabla ¿Cuál es el id del libro que leíste?')

    if sesion_primera('Lectura') == True: 
        print('\n--> Es la primer sesión del día')  
        query = f''' 
            INSERT INTO Lectura (Id_fecha, Id_libro, Tiempo)
            VALUES ({Id_fecha}, {Id_libro}, {tiempo})
        ''' 
    else: 
        print('\n--> No es la primer sesión del día')
        query = f'''
            UPDATE Lectura
            SET Tiempo = Tiempo + {tiempo}
            WHERE Id_fecha = {Id_fecha}
        '''
    queries_function(query=query)
    print('\nTerminó el registro de sesión de lectura\n')

'''---------RUTINA PARA REGISTRAR SESIÓN DE IDIOMA--------------------'''
def sesion_idioma():
    print('\n<< Registro de sesión de Idioma >>')

    mostrar('Idiomas')

    if validar_sino('¿Comenzaste con un nuevo idioma? (1:si, 0:no)') == 1:
        idio = input('\n¿Qúe idioma?\n')
        cursor = conn.cursor()
        query = f''' 
                    INSERT INTO Idiomas (Idioma)
                    VALUES (?)
                '''
        cursor.execute(query, (idio,))
        cursor.close()
        Id_idioma = obtener_ultimo(tabla='Idiomas', campo='Id_idioma')

    else: Id_idioma = validar_time('Según la tabla ¿Cuál es el id del idioma que practicaste?')

    hab = validar_time('¿Cuántos minútos dedicaste a la habilidad de hablarlo?')
    oir = validar_time('¿Cuántos a la de oírlo?')
    lee = validar_time('¿Cuántos a la de Leerlo?')
    esc = validar_time('¿Cuántos a la de escribirlo?')
    gra = validar_time('¿Cuántos a la de aprender su gramática?')

    if sesion_primera('Aprender_idiomas') == True: 
        print('\n--> Es la primer sesión del día')   
        query = f''' 
            INSERT INTO Aprender_idiomas (Id_fecha, Id_idioma, Hablar, Escuchar, Leer, Escribir, Gramática)
            VALUES ({Id_fecha}, {Id_idioma}, {hab}, {oir}, {lee}, {esc}, {gra})
        '''
    else: 
        print('\n--> No es la primer sesión del día\n')
        query = f'''
            UPDATE Aprender_idiomas
            SET Hablar = Hablar + {hab}, 
                Escuchar = Escuchar + {oir},
                Leer = Leer + {lee},
                Escribir = Escribir + {esc},
                Gramática = Gramática + {gra}
            WHERE Id_idioma = {Id_idioma}
        '''
    queries_function(query=query)
    print('\nTerminó el registro de sesión de idioma\n')

'''---------RUTINA PARA REGISTRAR SESIÓN DE PROGRAMACIÓN--------------'''
def sesion_programacion():
    print('\n<< Registro de sesión de programación >>')
    
    teo = validar_time('Minutos de Teoría:')
    pra = validar_time('Minutos de prácrtica:')

    if sesion_primera('Programación') == True:
        print('\n--> Es la primer sesión del día\n')   
        query = f'''
            INSERT INTO Programación (Id_fecha, Teoría, Práctica)
            VALUES ({Id_fecha}, {teo}, {pra});
        '''
    else:
        print('\n--> No es la primer sesión del día')
        query = f'''
            UPDATE Programación
            SET Teoría = Teoría + {teo}, 
                Práctica = Práctica + {pra}
            WHERE Id_fecha = {Id_fecha}
        '''
    queries_function(query=query)
    Id_programacion = obtener_ultimo(tabla='Programación', campo='Id_programación')

    mostrar('Lenguajes')

    if teo > 0:
        aprender = validar_sino('¿Empezaste a aprender un nuevo lenguaje? (1:si, 0:no):')
        if aprender == 0:
            Id_lenguaje = validar_time('\nSegún la tabla, ¿Cuál es el Id del lenguaje que estudiaste?\n')
        else:
            leng = input('\n¿Cuál lenguaje?:\n')
            cursor = conn.cursor()
            query = f''' 
                INSERT INTO Lenguajes (Nombre_lenguaje)
                VALUES (?)
            '''
            cursor.execute(query, (leng,))
            cursor.close()
            Id_lenguaje = obtener_ultimo(tabla='Lenguajes', campo='Id_lenguaje')

        query = f''' 
            INSERT INTO Programación_detalles (Id_Programación, Id_lenguaje, Id_aspecto, Tiempo)
            VALUES ({Id_programacion}, {Id_lenguaje}, 1, {teo})
        '''
        queries_function(query=query)

    if pra > 0:    
        aplicar = validar_sino('¿Empezaste a programar en un nuevo lenguaje? (1:si, 0:no):')
        if aplicar == 0:
            Id_lenguaje = validar_time('\nSegún la tabla, ¿Cuál es el Id del lenguaje en el que programaste?')
        else:
            leng = input('\n¿Cuál lenguaje?:\n')
            cursor = conn.cursor()
            query = f''' 
                INSERT INTO Lenguajes (Nombre_lenguaje)
                VALUES (?)
            '''
            cursor.execute(query, (leng,))
            cursor.close()
            Id_lenguaje = obtener_ultimo(tabla='Lenguajes', campo='Id_lenguaje')

        query = f''' 
            INSERT INTO Programación_detalles (Id_Programación, Id_lenguaje, Id_aspecto, Tiempo)
            VALUES ({Id_programacion}, {Id_lenguaje}, 2, {pra})
        '''
        queries_function(query=query)

    print('\nTerminó el registro de sesión de programación\n')

'''---------------RUTINA PARA REGISTRAR SESIÓN DE DIBUJO--------------'''

def sesion_dibujo():
    print('\n<< Registro de sesión de dibujo >>')
    
    teo = validar_time('Minutos de Teoría:')
    pra = validar_time('Minutos de prácrtica:')

    if sesion_primera('Dibujo') == True:
        print('\n--> Es la primer sesión del día\n')   
        query = f'''
            INSERT INTO Dibujo (Id_fecha, Teoría, Práctica)
            VALUES ({Id_fecha}, {teo}, {pra});
        '''
    else:
        print('\n--> No es la primer sesión del día')
        query = f'''
            UPDATE Dibujo
            SET Teoría = Teoría + {teo}, 
                Práctica = Práctica + {pra}
            WHERE Id_fecha = {Id_fecha}
        '''
    queries_function(query=query)
    Id_dibujo = obtener_ultimo(tabla='Programación', campo='Id_programación')

    mostrar('Obras')

    if teo > 0:
        query = f''' 
            INSERT INTO Dibujo_detalles (Id_dibujo, Id_obra, Id_aspecto)
            VALUES ({Id_dibujo}, 1, 1)
        '''
        queries_function(query=query)

    if pra > 0:    
        if validar_sino('Terminaste una obra hoy? (1:si, 0:no)') == 1:
            Id_obra = validar_time('Según la tabla ¿Cuál es su id?')
            Objetivo_completado(tabla='Obras', id_va= Id_obra, id_va_nombre='Id_obra')
        else:
            aplicar = validar_sino('¿Empezaste a una nueva obra? (1:si, 0:no):')
            if aplicar == 0:
                Id_obra = validar_time('\nSegún la tabla, ¿Cuál es el Id de la obra en la que trabajaste?\n')
            else:
                titu = input('\n¿Cuál es el título?\n')
                tecn = input('\n¿Qué técnica usarás?\n')
                cursor = conn.cursor()
                query = f''' 
                    INSERT INTO Obras (Título, Técnica)
                    VALUES (?, ?)
                '''
                cursor.execute(query, (titu, tecn))
                cursor.close()
                Id_obra = obtener_ultimo(tabla='Obras', campo='Id_obra')

            query = f''' 
                INSERT INTO Dibujo_detalles (Id_dibujo, Id_obra, Id_aspecto)
                VALUES ({Id_dibujo}, {Id_obra}, 2)
            '''
            queries_function(query=query)

    print('\nTerminó el registro de sesión de programación\n')  

'''-------------------------------------------------------------------'''

conn = sqlite3.connect('JL-FreeTime.db')   
print('\n|| Inicia el registro de actividad ||\n')
input('Presione enter para comenzar:\n')
primer = True
query = ''' 
    SELECT Día, Id_fecha FROM Fecha ORDER BY Id_fecha DESC
    LIMIT 1
'''
dia_reg, Id_fecha = pd.read_sql_query(query, conn).iloc[0]
año = datetime.now().strftime("%Y")
mes = datetime.now().strftime("%m")
dia = int(datetime.now().strftime("%d"))

if dia == dia_reg:
    print('--> No es el primer registro del día.\n')
    primer = False
else:
    print('--> Primer registro del día.\n')
    query = f''' 
        INSERT INTO Fecha (Año, Mes, Día)
        VALUES ({año}, {mes}, {dia});
    '''
    queries_function(query=query, commit=True)
    Id_fecha += 1

funciones = {
    '1': sesion_musica,
    '2': sesion_ejercicio,
    '3': sesion_estudio,
    '4': sesion_lectura,
    '5': sesion_idioma,
    '6': sesion_programacion,
    '7': sesion_dibujo
}
print('Qué actividad hiciste:\n\n1: Música\n2:Actividad Física\n3:Estudio\n4:Lectura\n5:Idioma\n6:Programación\n7:Dibujo\n')
entrada = input("Ingresa los números separados por comas (por ejemplo, 1,3,5):\n")
numeros_funciones = entrada.split(',')

for numero in numeros_funciones:
    funcion = funciones.get(numero.strip())
    if funcion:
        funcion()
    else:
        print(f"No se encontró la función {numero.strip()}")

cambios = validar_sino('Asentar cambios (1:si, 0:no): ')
if cambios == 1: conn.commit(); print('los cambios se asentaron correctamente')
else: print('Los cambios no se guardaron')