import argparse
import re
from html.parser import HTMLParser


class Pregunta():

    def __init__(self):
        self.enunciado = []
        self.respuestas = []
        self.correcta = None


class Collector(HTMLParser):
    preguntas = []
    pregunta_actual = 0
    fase_enunciado = False
    fase_respuesta = False
    leyendo_linea = False
    p_count = 0
    span_count = 0

    def handle_starttag(self, tag, attrs):
        if (tag == 'div'):
            question_regexp = r".*que\s.*"
            for att in attrs:

                # Detección de preguntas
                if (att[0] == 'class' and re.match(question_regexp, att[1])):
                    self.pregunta_actual += 1
                    self.respuesta_actual = 0
                # Detección de enunciado
                elif (att[0] == 'class' and att[1] == "qtext"):
                    self.fase_enunciado = True
                # Para simplificar la detección del fin del bloque respuestas,
                # detectamos el div de 'feedback'
                elif (att[0] == 'class' and re.match(r'.*outcome.*', att[1])):
                    self.fase_respuesta = False
                    self.fase_respuesta_correcta = False
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

        if (self.fase_enunciado and tag == 'div'):
            self.fase_enunciado = False
            self.p_count = 0
        if (tag == 'p'):
            if (self.leyendo_linea):
                self.leyendo_linea = False
                self.p_count += 1
                self.span_count = 0
        if (tag == 'span'):
            self.span_count += 1

    def handle_data(self, data):
        # Lectura de preguntas
        if (self.leyendo_linea and self.fase_enunciado):
            if (len(self.preguntas) < self.pregunta_actual):
                print("guardando pregunta {0}...".format(self.pregunta_actual))
                self.preguntas.append(Pregunta())
            p = self.preguntas[self.pregunta_actual-1]
            if (self.span_count and len(p.enunciado) >= self.p_count):
                p.enunciado[self.p_count-1] = p.enunciado[self.p_count-1] + data
            else:
                p.enunciado.append(data)
            print("guardando linea en {0}, datos: {1}".format(self.pregunta_actual, data))

        # Lectura de respuestas
        elif (self.leyendo_linea and self.fase_respuesta):
            p = self.preguntas[self.pregunta_actual-1]
            if (self.span_count and p.respuestas and len(p.respuestas) >= self.respuesta_actual):
                p.respuestas[self.respuesta_actual-1] = p.respuestas[self.respuesta_actual-1] + data
            else:
                p.respuestas.append(data)
            print("guardando respuesta {0}, en pregunta {1}, datos: {2}".format(self.respuesta_actual, self.pregunta_actual, data))

        elif (self.leyendo_linea and self.fase_respuesta_correcta):
            p = self.preguntas[self.pregunta_actual-1]
            for index in range(len(p.respuestas)):
                if (p.respuestas[index] == data):
                    p.correcta = index
                    print("respuesta_correcta: {0}".format(p.correcta))



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

def parsear_html():
    print("Iniciando análisis de html...")

