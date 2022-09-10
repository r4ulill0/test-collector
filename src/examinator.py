import re
from curses import wrapper
from argparse import ArgumentParser
import collector


def main(pantalla, preguntas):
    pass


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
