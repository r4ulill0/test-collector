import argparse
import re
from html.parser import HTMLParser


class Pregunta():

    def __init__(self):
        self.enunciado = []
        self.respuestas = []
        self.correctas = []


class Collector(HTMLParser):
    preguntas = []
    pregunta_actual = 0
    fase_enunciado = False
    fase_respuesta = False
    fase_respuesta_correcta = False
    respuesta_correcta_actual = ''
    leyendo_linea = False
    p_count = 0
    span_count = 0

    def handle_starttag(self, tag, attrs):
        if (tag == 'div'):
            for att in attrs:

                # Detección de preguntas
                # Detección de enunciado
                if (att[0] == 'class' and att[1] == "qtext"):
                    self.fase_enunciado = True
                    self.span_count = 0
                    print('RESPUESTAS CORRECTAS LEIDAS')
                    print(self.respuesta_correcta_actual)
                    self.respuesta_correcta_actual = ''
                    self.pregunta_actual += 1
                    self.respuesta_actual = 0
                # Para simplificar la detección del fin del bloque respuestas,
                # detectamos el div de 'feedback'
                elif (att[0] == 'class' and re.match(r'.*outcome.*', att[1])):
                    self.fase_respuesta = False
                # Detección de respuestas
                elif (att[0] == 'data-region' and att[1] == "answer-label"):
                    self.respuesta_actual += 1
                    self.fase_enunciado = False
                    self.fase_respuesta = True
                elif (att[0] == 'class' and att[1] == 'rightanswer'):
                    self.fase_respuesta_correcta = True
        elif (tag == 'p'):
            self.leyendo_linea = True

    def handle_endtag(self, tag):
        if (tag == 'div' and self.fase_respuesta_correcta):
            self.fase_respuesta_correcta = False
        if (tag == 'div' and self.fase_enunciado):
            self.fase_enunciado = False
            self.p_count = 0

        if (self.fase_enunciado and tag == 'p'):
            if (self.leyendo_linea):
                self.leyendo_linea = False
                self.p_count += 1
                self.span_count = 0
        if (tag == 'span'):
            self.span_count += 1

    def handle_data(self, data):
        data = data.replace("\n", " ")
#        print("datooos")
#        print(data)
#        print(self.span_count)
#        print("leyendo_linea: {}".format(self.leyendo_linea))
#        print("fase_enunciado: {}".format(self.fase_enunciado))
#        print("fase_respuesta: {}".format(self.fase_respuesta))
#        print("fase_respuesta_correcta: {}".format(self.fase_respuesta_correcta))
#        print("p_count: {}".format(self.p_count))
        # Lectura de preguntas
        if (self.leyendo_linea and self.fase_enunciado):
            if (len(self.preguntas) < self.pregunta_actual):
                print("guardando pregunta {0}...".format(self.pregunta_actual))
                self.preguntas.append(Pregunta())
            p = self.preguntas[self.pregunta_actual-1]
            if (self.span_count > 0 ):
                p.enunciado[self.p_count-1] = "".join([p.enunciado[self.p_count-1], data])
            else:
                p.enunciado.append(data)
            print("guardando linea en {0}, <p> {4}, span {2}, segmentos acumlados {3}, datos: {1}"
                  .format(self.pregunta_actual, data, self.span_count, len(p.enunciado), self.p_count))

        # Lectura de respuestas
        elif (self.leyendo_linea and self.fase_respuesta):
            p = self.preguntas[self.pregunta_actual-1]
            if (self.span_count and p.respuestas and len(p.respuestas) >= self.respuesta_actual):
                p.respuestas[self.respuesta_actual-1] = p.respuestas[self.respuesta_actual-1] + data
            else:
                p.respuestas.append(data)
            print("guardando respuesta {0}, en pregunta {1}, datos: {2}"
                  .format(self.respuesta_actual, self.pregunta_actual, data))

        elif (self.leyendo_linea and self.fase_respuesta_correcta):
            print("tratando correcta {}".format(data))
            self.respuesta_correcta_actual = self.respuesta_correcta_actual + data
            p = self.preguntas[self.pregunta_actual-1]
            for index in range(len(p.respuestas)):
                print("Esta {0} en {1}\n? {2}".format(data, p.respuestas[index], data in p.respuestas[index]))
                print("Filter difference {}".format(len(p.respuestas[index]) - len(data)))
                if (abs(len(p.respuestas[index]) - len(data)) < 10  # Filtro de precisión
                        and data in p.respuestas[index]):
                    p.correctas.append(index)
                    print("respuesta_correcta: {0}".format(index))



if (__name__ == "__main__"):
    entrada = argparse.ArgumentParser()
    entrada.add_argument("archivo", help="archivo html a parsear")
    args = entrada.parse_args()
    parser = Collector()
    with open(args.archivo, "r") as raw_html:
        parser.feed(raw_html.read())

    print("Analizadas {0} preguntas".format(len(parser.preguntas)))
    print(len(parser.preguntas[0].enunciado))
    print(len(parser.preguntas[1].enunciado))
    print("Son iguales: {0}".format(parser.preguntas[0].enunciado == parser.preguntas[1].enunciado))

    print("\nRESULTADOS DEL ESCANEO\n########\n#######")
    for pregunta in parser.preguntas:
        for enunciado in pregunta.enunciado:
            print(enunciado, flush=True)
        for index in range(len(pregunta.respuestas)):
            if (index in pregunta.correctas):
                print("+ {}".format(pregunta.respuestas[index]), flush=True)
            else:
                print("- {}".format(pregunta.respuestas[index]), flush=True)


    print(parser.preguntas[1].enunciado)


def parsear_html():
    print("Iniciando análisis de html...")

