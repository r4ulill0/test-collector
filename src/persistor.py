import os

MSG_SOBREESCRITURA = 'Se ha encontrado el archivo \
{}.\n¿Desea sobreescribirlo? (y/N)'


class Persistor:

    def __init__(self):
        self.base_dir = os.getcwd()

    def persiste_preguntas(self, preguntas, nombre_guardado='test-collection'):

        if (os.path.isfile(nombre_guardado)):
            continuar = input(MSG_SOBREESCRITURA.format(nombre_guardado))
            if not continuar:
                return

        with open(nombre_guardado, 'w', encoding='utf-8') as archivo:
            for pregunta in preguntas:
                archivo.write('?>\n')
                for linea_enunciado in pregunta.enunciado:
                    archivo.write('{}\n'.format(linea_enunciado))

                archivo.write('\n')

                for index in range(len(pregunta.respuestas)):
                    prefijo = '+>' if index in pregunta.correctas else '->'
                    archivo.write('{}{}\n'
                                  .format(prefijo, pregunta.respuestas[index]))

                archivo.write('\n\n\n')
