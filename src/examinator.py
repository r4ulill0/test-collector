import re
import time
from curses import wrapper
from argparse import ArgumentParser
from random import shuffle
import collector

KEY_UP = ('KEY_UP', 'K')
KEY_DOWN = ('KEY_DOWN', 'J')
KEY_SELECT = (' ', '\n')

MAIN_MENU_OPCIONES = ('Examen normal',
                      'Probar coleccion en orden',
                      'Examen personalizado',
                      'Salir')
EXAM_MENU_OPCIONES = ('Anterior',
                      'Siguiente',
                      'Terminar examen',
                      'Marcar pregunta',
                      'Salir')
MMO_IDENTACION_BASE = 5  # Posición horizontal de las opciones del menu
MMO_ALTURA_BASE = 5  # Altura a la que se empiezan a mostrar las opciones del menu
MMO_SEPARACION = 2    # Separacion entre las opciones del menu principal

EXM_PREGUNTA_ALTURA_BASE = 5
EXM_PREGUNTA_IDENTACION_BASE = 10
EXM_RESPUESTA_ALTURA_BASE = 20
EXM_RESPUESTA_IDENTACION_BASE = 10
EXM_RELOJ_ALTURA = 1
EXM_RELOJ_IDENTACION = 80
EXM_MENU_ALTURA_BASE = 30
EXM_MENU_IDENTACION_BASE = 20
EXM_SEPARACION_WIDGET = 4
EXM_SEPARACION_RESPUESTAS = 2


def main(pantalla, preguntas):
    pantalla.nodelay(True)
    opcion = 0

    # Copiamos porque shuffle trabaja con la propia lista
    copia_preguntas = preguntas.copy()

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
                # TODO hacer método que haga un shuffle de respuestas
                # manteniendo la referencia a la respuesta correcta
                shuffle(copia_preguntas)
                examen(pantalla, copia_preguntas)
            if opcion == 1:
                pass
            if opcion == 2:
                pass
            if opcion == 3:
                break

        render_main_menu(pantalla, opcion)

        pantalla.refresh()
        time.sleep(0.1)

def examen(pantalla, preguntas, duracion = None):
    examinandose = True
    comienzo = time.time()
    pregunta_seleccionada = 0
    # TODO implementar seleccion
    seleccion = 0
    while examinandose:
        pantalla.clear()
        render_enunciado_examen(pantalla, preguntas[pregunta_seleccionada])
        render_tiempo_examen(pantalla, comienzo, duracion)
        render_respuestas_examen(pantalla, preguntas[pregunta_seleccionada])
        render_menu_examen(pantalla, seleccion)

        pantalla.refresh()


def render_enunciado_examen(pantalla, pregunta):
    alto = EXM_PREGUNTA_ALTURA_BASE
    ancho = EXM_PREGUNTA_IDENTACION_BASE
    for linea in pregunta.enunciado:
        pantalla.addstr(alto,
                        ancho,
                        linea)
        # TODO arreglar problema de renderizado cuando
        # una linea ocupa varias filas en pantalla
        alto += 1
        ancho += 1


def render_tiempo_examen(pantalla, comienzo, final):
    linea = 'Sin tiempo límite'
    if final:
        tiempo = final - comienzo
        linea = time.ctime(tiempo)

    pantalla.addstr(EXM_RELOJ_ALTURA,
                    EXM_RELOJ_IDENTACION,
                    linea)

# TODO
def render_respuestas_examen(pantalla, pregunta):
    pass

def render_menu_examen(pantalla, seleccion):
    if seleccion is not None and (seleccion < 0
                                  or seleccion > len(EXAM_MENU_OPCIONES)):
        raise Exception(f'Seleccion en menu examen inválida: {seleccion}')
    menu = ''
    for i in range(len(EXAM_MENU_OPCIONES)):
        opt = f'{EXAM_MENU_OPCIONES[i]}     ' if seleccion != i \
            else f'>{EXAM_MENU_OPCIONES[i]}<     '

        menu += opt
    pantalla.addstr(EXM_MENU_ALTURA_BASE,
                    EXM_MENU_IDENTACION_BASE,
                    menu)


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
