import re
import curses
import time
from curses import wrapper
from argparse import ArgumentParser
import collector

KEY_UP = ('KEY_UP', 'K')
KEY_DOWN = ('KEY_DOWN', 'J')
KEY_SELECT = (' ', '\n')

MAIN_MENU_OPCIONES = ('Examen normal',
                      'Probar coleccion en orden',
                      'Examen personalizado',
                      'Salir')
MMO_IDENTACION_BASE = 5  # Posición horizontal de las opciones del menu
MMO_ALTURA_BASE = 30  # Altura a la que se empiezan a mostrar las opciones del menu
MMO_SEPARACION = 2    # Separacion entre las opciones del menu principal

def main(pantalla, preguntas):
    pantalla.nodelay(True)
    opcion = 0

    # Menu principal
    while True:
        pantalla.clear()
        try:
            seleccion = pantalla.getkey()
        except:
            seleccion = ''

        if seleccion.upper() in KEY_UP:
            opcion = opcion - 1 if opcion > 0 else 0
        elif seleccion.upper() in KEY_DOWN:
            opcion = opcion + 1 if opcion < len(MAIN_MENU_OPCIONES)-1 else len(MAIN_MENU_OPCIONES)-1
        elif seleccion in KEY_SELECT:
            # Gestión de selección
            if opcion == 0:
                pass
            if opcion == 1:
                pass
            if opcion == 2:
                pass
            if opcion == 3:
                break

        render_main_menu(pantalla, opcion)

        pantalla.refresh()
        time.sleep(0.1)

def render_main_menu(pantalla, opcion):
    indicacion = 'Seleccione una opción:'

    altura_opcion = MMO_ALTURA_BASE
    identacion_opcion = MMO_IDENTACION_BASE
    pantalla.addstr(altura_opcion, identacion_opcion, indicacion)
    for menu_opt in range(len(MAIN_MENU_OPCIONES)):
        altura_opcion += MMO_SEPARACION
        opt = f'> {menu_opt+1} {MAIN_MENU_OPCIONES[menu_opt]}'
        opt = opt if menu_opt == opcion else opt[1:]
        pantalla.addstr(altura_opcion, MMO_IDENTACION_BASE, opt)



def leer_preguntas(archivo, debug=False):
    preguntas = []
    r_pregunta = False

    pregunta_actual = None
    with open(archivo, 'r') as exam_data:
        print('Leyendo archivo {}\n'.format(archivo))
        for linea in exam_data.readlines():
            if debug:
                print('Leyendo línea:\n{}'.format(linea))

            if re.match(r'^[+-]>', linea):
                r_pregunta = False

            if r_pregunta:
                pregunta_actual.enunciado.append(linea)
                pass
            else:  # Esperando leer respuesta
                if re.match(r'\?>', linea):  # Viene una pregunta
                    if pregunta_actual:  # Guardamos la última pregunta leída
                        preguntas.append(pregunta_actual)

                    r_pregunta = True
                    pregunta_actual = collector.Pregunta()
                    continue
                else:
                    # Lectura de respuestas
                    if re.match(r'^->', linea):
                        pregunta_actual.respuestas.append(linea)
                    elif re.match(r'^\+>', linea):
                        pregunta_actual.respuestas.append(linea)
                        pregunta_actual.correctas .append(len(pregunta_actual.respuestas))
                    elif debug:
                        print('Leida línea inconsistente con el formato esperado:\n{}'
                              .format(linea))

        # Guardamos la última pregunta antes del EOF
        preguntas.append(pregunta_actual)

        collector.imprime_resultados(preguntas, debug)

    return preguntas


if (__name__ == '__main__'):
    entrada = ArgumentParser()
    entrada.add_argument('archivo', help='Archivo con colección de preguntas')
    entrada.add_argument('-d', '--debug', action='store_true', help='Activa la salida de depuración')

    args = entrada.parse_args()

    preguntas = leer_preguntas(args.archivo, args.debug)

    # Curses entrypoint
    wrapper(main, preguntas)
