#SE IMPORTAN TODOS LOS MODULOS NECESARIOS PARA EL FUNCIONAMIENTO DE LA APLICACION
from flask import Flask, request, json, redirect, url_for, Response
from bson import ObjectId
from pymongo import MongoClient
from io import StringIO
import werkzeug.exceptions as we
import sys
import hashlib
import datetime

#SE DEFINEN TODOS LOS ATRIBUTOS DEL BOT
elCreador = "Joshua Campos Chiny"
laFechaDeCreacion = datetime.date(2017,2,16)
elNombre = "W-Bot"
elHash = hashlib.md5(str(laFechaDeCreacion).encode())
laIdentificacion = elHash.hexdigest()

#SE DEFINE Y SE INICIALIZA LA BASE DE DATOS LOCAL DE MONGODB, UTILIZANDO EL MODULO PARA PYTHON: PYMONGO
clienteMongo = MongoClient('localhost', 27017)
laBaseDeDatos = clienteMongo.MongoDB

app = Flask(__name__)

@app.before_request
def verifiqueRutas():
    elURL = request.url_rule                                                    #SE GUARDA LA URL QUE MANDA EL USUARIO
    if elURL == None:                                                           #SI EL URL DEL USUARIO NO COINCIDE CON NINGUNA DIRECCION
        laAccion = "404: Not Found"                                             #DEFINE LA ACCION PARA EL LOG
        ingreseElLog(laAccion)                                                  #INGRESA EL LOG CORRESPONDIENTE
        elTexto = "Lo siento. No conozco esa ruta o el método es inválido."     #SE CREA UNA RESPUESTA
        laRespuesta = json.dumps(elTexto)                                       #SE CONVIERTE A JSON
        return Response(laRespuesta, 404, mimetype="application/json")          #SE RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS

@app.route('/', methods=['GET'])
def redirecciona():
    laAccion = "Redireccion"                             #DEFINE LA ACCION PARA EL LOG
    ingreseElLog(laAccion)                               #INGRESA EL LOG CORRESPONDIENTE
    return redirect(url_for('bienvenida'), 301)          #REDIRECCIONA A LA RUTA DE BIENVENIDA


@app.route('/api/web-bot/bienvenida', methods=['GET','POST'])
def bienvenida():
    try:
        if request.method == 'GET':
            laAccion = "Bienvenida 'GET'"                                                       #DEFINE LA ACCION PARA EL LOG
            ingreseElLog(laAccion)                                                              #INGRESA EL LOG CORRESPONDIENTE
            elTexto = '¡Bienvenido! ¡Soy W-Bot! ¿Cómo te llamas?'                               #SE CREA LA RESPUESTA
            laRespuesta = json.dumps(elTexto)                                                   #SE CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")                      #SE RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS
        else:
            elArgumento = request.args                                                          #TRAE LOS PARAMETROS ENVIADOS
            elNombre = elArgumento['miNombre']                                                  #BUSCA EL PARAMETRO BAJO LA LLAVE: MINOMBRE
            laDireccion = request.remote_addr                                                   #RECIBE LA DIRECCION IP DEL USUARIO
            elUsuario = {'_id': laDireccion, "Nombre": elNombre}                                #DEFINE AL USUARIO CON AMBOS ATRIBUTOS

            if laBaseDeDatos.Usuarios.find({"_id": laDireccion}).count() == 0:                  #SI NO EXISTE EL USUARIO EN LA BASE DE DATOS
                laBaseDeDatos.Usuarios.insert_one(elUsuario)                                    #INSERTA EL USUARIO
            else:
                laBaseDeDatos.Usuarios.update({"_id": laDireccion}, {"Nombre": elNombre})       #ACTUALIZA EL NOMBRE

            laAccion = "Bienvenida 'POST'"                                      #DEFINE LA ACCION PARA EL LOG
            ingreseElLog(laAccion)                                              #INGRESA EL LOG CORRESPONDIENTE
            elTexto = '¡Hola ' + elNombre + '! ¿En qué puedo ayudarte?'         #SE CREA LA RESPUESTA
            laRespuesta = json.dumps(elTexto)                                   #SE CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")      #SE RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS
    except Exception as e:                                                      #ATRAPA CUALQUIER EXCEPCION
        return formateeElError(e)                                               #LA RETORNA FORMATEADA

@app.route('/api/web-bot/operaciones', methods=['GET'])
def mostrarOperaciones():
    elResultado = {}                                            #DEFINE UN DICCIONARIO VACIO
    elContador = 1                                              #DEFINE UN CONTADOR
    losLogs = laBaseDeDatos.Log_Operaciones.find()              #OBTIENE TODOS LOS LOGS DE OPERACIONES
    for cadaLog in losLogs:                                     #PARA CADA LOG QUE TRAE
        elJSON = json.dumps(cadaLog)                            #LO CONVIERTE A JSON
        elResultado["Operacion_"+str(elContador)] = elJSON      #AGREGA CADA VALOR AL DICCIONARIO
        elContador += 1                                         #AUMENTA EL CONTADOR

    laAccion = "Operaciones"                                            #DEFINE LA ACCION PARA EL LOG
    ingreseElLog(laAccion)                                              #INGRESA EL LOG CORRESPONDIENTE
    laRespuesta = json.dumps(elResultado)                               #CONVERTE EL DICCIONARIO A JSON
    return Response(laRespuesta, 200, mimetype="application/json")      #RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS

@app.route('/api/web-bot/memoria', methods=['GET'])
def mostrarMemoria():
    elResultado = {}                                                #DEFINE UN DICCIONARIO VACIO
    elContador = 1                                                  #DEFINE UN CONTADOR
    laMemoria = laBaseDeDatos.Memoria_Aprendizaje.find()            #OBTIENE LO QUE HA APRENDIDO
    for cadaMemoria in laMemoria:                                   #PARA CADA COSA QUE SABE
        elJSON = json.dumps(cadaMemoria)                            #LO CONVIERTE A JSON
        elResultado["Memoria_"+str(elContador)] = elJSON            #AGREGA LOS DOS VALORES AL RESULTADO
        elContador += 1                                             #AUMENTA EL CONTADOR

    laAccion = "Memoria"                                            #DEFINE LA ACCION PARA EL LOG
    ingreseElLog(laAccion)                                          #INGRESA EL LOG CORRESPONDIENTE
    laRespuesta = json.dumps(elResultado)                           #CONVERTE EL DICCIONARIO A JSON
    return Response(laRespuesta, 200, mimetype="application/json")  #RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS

@app.route('/api/web-bot/aprender', methods=['POST'])
def aprender():
    try:
        laInformacion = request.json                                                        #OBTIENE EL JSON ENVIADO
        elJSON = json.dumps(laInformacion)                                                  #LO CONVIERTE A JSON
        elParseo = json.loads(elJSON)                                                       #LO CARGA PARA PERMITIR PARSEAR
        if "Nombre" not in elParseo:                                                        #SI NO ESTA LA LLAVE NOMBRE
            raise we.BadRequest()                                                           #LEVANTA UN ERROR
        elif "Instruccion" not in elParseo:                                                 #SI NO ESTA LA LLAVE INSTRUCCION
            raise we.BadRequest()                                                           #LEVANTA UN ERROR
        elif len(elParseo) > 2:                                                             #SI HAY MAS DE DOS LLAVES
            raise we.BadRequest()                                                           #LEVANTA UN ERROR

        elNombre = elParseo["Nombre"]                                                       #OBTIENE EL VALOR DEL CAMPO NOMBRE
        if laBaseDeDatos.Memoria_Aprendizaje.find({"Nombre": elNombre}).count() > 0:        #SI YA SABE HACER LA ACCION
            laAccion = "Error: Aprender_" + elNombre                                        #DEFINE LA ACCION PARA EL LOG
            ingreseElLog(laAccion)                                                          #INGRESA EL LOG CORRESPONDIENTE
            elTexto = "Lo lamento. Ya sé cómo: " + elNombre                                 #GENERA EL TEXTO DE RESPUESTA
            laRespuesta = json.dumps(elTexto)                                               #LO CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")                  #RETORNA UN MENSAJE NEGATIVO ADECUADO

        laInformacion['_id'] = str(ObjectId())                                              #LE AGREGA UN ID A LO QUE APRENDE
        laBaseDeDatos.Memoria_Aprendizaje.insert_one(laInformacion)                         #AGREGA LA ACCION A LA BASE DE DATOS

        laAccion = "Aprender: " + elNombre                                                  #DEFINE LA ACCION PARA EL LOG
        ingreseElLog(laAccion)                                                              #INGRESA EL LOG CORRESPONDIENTE
        elTexto = "He aprendido a: " + elNombre                                             #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                   #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                      #RETORNA UN MENSAJE POSITIVO ADECUADO
    except Exception as e:                                                                  #ATRAPA CUALQUIER EXCEPCION
        return formateeElError(e)                                                           #LA RETORNA FORMATEADA

@app.route('/api/web-bot/olvidar', methods=['POST'])
def olvidar():
    try:
        elArgumento = request.args                                                              #OBTIENE LOS PARAMETROS ENVIADOS
        elNombre = elArgumento['laAccion']                                                      #OBTIENE EL VALOR DEL CAMPO ACCION
        elConocimiento = laBaseDeDatos.Memoria_Aprendizaje.find_one({'Nombre':elNombre})        #BUSCA SI LA ACCION EXISTE
        if elConocimiento != None:                                                              #SI EXISTE
            laBaseDeDatos.Memoria_Aprendizaje.delete_one({'Nombre': elNombre})                  #LA BORRA DE LA BASE DE DATOS
        else:                                                                                   #SI NO
            laAccion = "Error: Olvidar_" + elNombre                                             #DEFINE LA ACCION PARA EL LOG
            ingreseElLog(laAccion)                                                              #INGRESA EL LOG CORRESPONDIENTE
            elTexto = "No puedo olvidar algo que nunca supe hacer..."                           #GENERA EL TEXTO DE RESPUESTA
            laRespuesta = json.dumps(elTexto)                                                   #LO CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")                      #RETORNA UN MENSAJE NEGATIVO ADECUADO

        laAccion = "Olvidar: " + elNombre                                                       #DEFINE LA ACCION PARA EL LOG
        ingreseElLog(laAccion)                                                                  #INGRESA EL LOG CORRESPONDIENTE
        elTexto = "He olvidado: " + elNombre                                                    #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                       #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                          #RETORNA UN MENSAJE POSITIVO ADECUADO
    except Exception as e:                                                                      #ATRAPA CUALQUIER EXCEPCION
        return formateeElError(e)                                                               #LA RETORNA FORMATEADA

@app.route('/api/web-bot/hacer/<accion>', methods=['GET', 'POST'])
def realizarAccion(accion):
    try:
        if request.method == 'POST':                                                            #SI EL METODO ES POST
            losParametros = request.args                                                        #OBTIENE LOS PARAMETROS ENVIADOS
            losParametrosComoDiccionario = dict(losParametros)                                  #LOS CONVIERTE EN UN DICCIONARIO
            laCantidadDeParametros = len(losParametrosComoDiccionario)                          #CUENTA LA CANTIDAD DE PARAMETROS

            if laCantidadDeParametros >= 1:                                                     #SI ES UNO O MAS PARAMETROS
                Parametro1 = losParametros['Parametro1']                                        #OBTIENE EL PRIMER PARAMETRO
                if Parametro1.isnumeric():                                                      #SI EL PARAMETRO ES UN NUMERO
                    Parametro1 = int(Parametro1)                                                #LO CONVIERTE A UN NUMERO
            if laCantidadDeParametros >= 2:                                                     #SI SON DOS O MAS PARAMETROS
                Parametro2 = losParametros['Parametro2']                                        #OBTIENE EL SEGUNDO PARAMETRO
                if Parametro2.isnumeric():                                                      #SI EL PARAMETROS ES UN NUMERO
                    Parametro2 = int(Parametro2)                                                #LO CONVIERTE A UN NUMERO
            if laCantidadDeParametros >= 3:                                                     #SI SON TRES O MAS PARAMETROS
                Parametro3 = losParametros['Parametro3']                                        #OBTIENE EL TERCER PARAMETROS
                if Parametro3.isnumeric():                                                      #SI EL PARAMETRO ES UN NUMERO
                    Parametro3 = int(Parametro3)                                                #LO CONVIERTE A UN NUMERO

        laAccion = laBaseDeDatos.Memoria_Aprendizaje.find_one({"Nombre": accion})               #BUSCA SI LA ACCION EXISTE
        if laAccion != None:                                                                    #SI EXISTE
            elJSON = json.dumps(laAccion)                                                       #LA CONVIERTE A JSON
            elParseo = json.loads(elJSON)                                                       #LA CARGA PARA PERMITIR PARSEAR
            elCodigo = elParseo['Instruccion']                                                  #OBTIENE EL VALOR DEL CAMPO INSTRUCCION
        else:                                                                                   #SI NO
            laActividad = "Error: Realizar_" + accion                                           #DEFINE LA ACCION PARA EL LOG
            ingreseElLog(laActividad)                                                           #INGRESA EL LOG CORRESPONDIENTE
            elTexto = "Lo lamento. No sé cómo: " + accion                                       #GENERA EL TEXTO DE RESPUESTA
            laRespuesta = json.dumps(elTexto)                                                   #LO CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")                      #RETORNA UN MENSAJE NEGATIVO ADECUADO

        elResultado = StringIO()                                                                #VARIABLE ESPECIAL PARA GUARDAR TEXTO
        sys.stdout = elResultado                                                                #LO QUE IMPRIMA, LO GUARDA EN LA VARIABLE
        exec(elCodigo)                                                                          #EJECUTAMOS EL CODIGO DE LA INSTRUCCION
        sys.stdout = sys.__stdout__                                                             #LO QUE IMPRIMA, LO IMPRIME EN CONSOLA

        laActividad = "Realizar: " + accion                                                     #DEFINE LA ACCION PARA EL LOG
        ingreseElLog(laActividad)                                                               #INGRESA EL LOG CORRESPONDIENTE
        elTexto = elResultado.getvalue()                                                        #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                       #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                          #RETORNA UN MENSAJE POSITIVO ADECUADO
    except Exception as e:                                                                      #SE ATRAPA CUALQUIER EXCEPCION
        return formateeElError(e)                                                               #SE RETORNA FORMATEADA


@app.route('/api/web-bot/ejecutar/<accion>', methods=['GET','POST'])
def ejecutarAccion(accion):
    try:
        if request.method == 'POST':                                                            #SI EL METODO ES POST
            losParametros = request.args                                                        #OBTIENE LOS PARAMETROS
            losParametrosComoDiccionario = dict(losParametros)                                  #LOS CONVIERTE EN UN DICCIONARIO
            laCantidadDeParametros = len(losParametrosComoDiccionario)                          #CUENTA LA CANTIDAD DE PARAMETROS

            if laCantidadDeParametros >= 1:                                                     #SI ES UNO O MAS PARAMETROS
                Parametro1 = losParametros['Parametro1']                                        #OBTIENE EL PRIMER PARAMETRO
                if Parametro1.isnumeric():                                                      #SI EL PARAMETROS ES UN NUMERO
                    Parametro1 = int(Parametro1)                                                #LO CONVIERTE A NUMERO
            if laCantidadDeParametros >= 2:                                                     #SI SON DOS O MAS PARAMETROS
                Parametro2 = losParametros['Parametro2']                                        #OBTIENE EL SEGUNDO PARAMETROS
                if Parametro2.isnumeric():                                                      #SI EL PARAMETROS ES UN NUMERO
                    Parametro2 = int(Parametro2)                                                #LO CONVIERTE A NUMERO
            if laCantidadDeParametros >= 3:                                                     #SI SON TRES O MAS PARAMETROS
                Parametro3 = losParametros['Parametro3']                                        #OBTIENE EL TERCER PARAMETRO
                if Parametro3.isnumeric():                                                      #SI EL PARAMETROS ES UN NUMERO
                    Parametro3 = int(Parametro3)                                                #LO CONVIERTE A NUMERO

        laAccion = laBaseDeDatos.Memoria_Aprendizaje.find_one({"Nombre": accion})               #BUSCA SI LA ACCION EXISTE
        if laAccion != None:                                                                    #SI EXISTE
            elJSON = json.dumps(laAccion)                                                       #LA CONVIERTE A JSON
            elParseo = json.loads(elJSON)                                                       #LA CARGA PARA PERMITIR PARSEO
            elCodigo = elParseo['Instruccion']                                                  #OBTIENE EL VALOR DEL CAMPO INSTRUCCION
        else:                                                                                   #SI NO
            laActividad = "Error: Ejecutar_" + accion                                           #DEFINE LA ACCION PARA EL LOG
            ingreseElLog(laActividad)                                                           #INGRESA EL LOG CORRESPONDIENTE
            elTexto = "Lo lamento. No sé cómo: " + accion                                       #GENERA EL TEXTO DE RESPUESTA
            laRespuesta = json.dumps(elTexto)                                                   #LO CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")                      #RETORNA UN MENSAJE NEGATIVO ADECUADO

        exec(elCodigo)                                                                          #EJECUTA EL CODIGO DE LA INSTRUCCION
        laActividad = "Ejecutar: " + accion                                                     #DEFINE LA ACCION PARA EL LOG
        ingreseElLog(laActividad)                                                               #INGRESA EL LOG CORRESPONDIENTE
        elTexto = "Ejecutando: " + accion                                                       #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                       #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                          #RETORNA UN MENSAJE POSITIVO ADECUADO
    except Exception as e:                                                                      #ATRAPA CUALQUIER EXCEPCION
        return formateeElError(e)                                                               #LA RETORNA FORMATEADA

def definaElUsuario():
    elUsuario = request.remote_addr                                     #OBTIENE LA DIRECCION IP DEL USUARIO
    laSolicitud = laBaseDeDatos.Usuarios.find_one({"_id": elUsuario})   #REVISA SI LA DIRECCION YA EXISTE
    if laSolicitud != None:                                             #SI EXISTE
        elUsuario = laSolicitud["Nombre"]                               #OBTIENE EL NOMBRE DEL USUARIO
    return elUsuario                                                    #RETORNA EL NOMBRE O LA DIRECCION DEL USUARIO

def ingreseElLog(laAccion):
    elUsuario = definaElUsuario()                       #DEFINE EL USUARIO
    elLog = {                                           #DEFINE EL LOG
        "_id": str(ObjectId()),
        "Usuario": elUsuario,
        "Fecha": datetime.datetime.now(),
        "Accion": laAccion
    }
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)     #INSERTA EL LOG A LA BASE DE DATOS

def formateeElError(e):
    elErrorComoTexto = str(e)                                                           #CONVIERTE EL MENSAJE DE ERROR A TEXTO
    elEnunciado = "Lo lamento. Ha ocurrido un error " + elErrorComoTexto                #LO AGREGA A UN ENUNCIADO
    elEnunciadoComoJSON = json.dumps(elEnunciado)                                       #LO CONVIERTE A JSON
    elErrorHTTP = elErrorComoTexto[:3]                                                  #OBTIENE EL NUMERO DE ERROR HTTP
    laActividad = elErrorComoTexto                                                      #DEFINE LA ACCION PARA EL LOG
    ingreseElLog(laActividad)                                                           #INGRESA EL LOG CORRESPONDIENTE
    return Response(elEnunciadoComoJSON, elErrorHTTP, mimetype="application/json")      #RETORNA LA RESPUESTA ADECUADA

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')