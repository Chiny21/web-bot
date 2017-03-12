#SE IMPORTAN TODOS LOS MODULOS NECESARIOS PARA EL FUNCIONAMIENTO DE LA APLICACION
from flask import Flask, request, json, redirect, url_for, Response
from bson import ObjectId
from pymongo import MongoClient
from io import StringIO
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
    elURL = request.url_rule                                                                                                #SE GUARDA LA URL QUE MANDA EL USUARIO
    existe = False                                                                                                          #SE INICIALIZA UNA VARIABLE BOOLEANA
    for cadaDireccion in app.url_map.iter_rules():                                                                          #PARA CADA URL DEL MAPA DE URLS DE LA APLICACION
        if elURL == cadaDireccion:                                                                                          #SI EL URL DEL USUARIO COINCIDE CON ALGUN URL DE LA APLICACION
            existe = True                                                                                                   #LA VARIABLE EXISTE ES VERDADERA
    if existe == False:                                                                                                     #SI EL URL DEL USUARIO NO COINCIDE CON NINGUNA DIRECCION
        elUsuario = definaElUsuario()                                                                                       # DEFINE EL USUARIO
        elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Error 404"}     # DEFINE EL LOG
        laBaseDeDatos.Log_Operaciones.insert_one(elLog)

        elTexto = "Lo siento. No conozco esa ruta o el método es inválido."                                                 #SE CREA UNA RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                                                   #SE CONVIERTE A JSON
        return Response(laRespuesta, 404, mimetype="application/json")                                                      #SE RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS

@app.route('/', methods=['GET'])
def redirecciona():
    elUsuario = definaElUsuario()                                                                                           #DEFINE EL USUARIO
    elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Redireccion"}       #DEFINE EL LOG
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                         #INSERTA EL LOG A LA BASE DE DATOS
    return redirect(url_for('bienvenida'), 301)                                                                             #REDIRECCIONA A LA RUTA DE BIENVENIDA


@app.route('/api/web-bot/bienvenida', methods=['GET','POST'])
def bienvenida():
    try:
        if request.method == 'GET':
            elUsuario = definaElUsuario()                                                                                               #DEFINE EL USUARIO
            elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Bienvenida 'GET'"}      #DEFINE EL LOG
            laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                             #INSERTA EL LOG A LA BASE DE DATOS
            elTexto = '¡Bienvenido! ¡Soy W-Bot! ¿Cómo te llamas?'                                                                       #SE CREA LA RESPUESTA
            laRespuesta = json.dumps(elTexto)                                                                                           #SE CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")                                                              #SE RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS
        else:
            elArgumento = request.args                                                                                                  #TRAE LOS PARAMETROS ENVIADOS
            elNombre = elArgumento['miNombre']                                                                                          #BUSCA EL PARAMETRO BAJO LA LLAVE: MINOMBRE
            laDireccion = request.remote_addr                                                                                           #RECIBE LA DIRECCION IP DEL USUARIO
            elUsuario = {'_id': laDireccion, "Nombre": elNombre}                                                                        #DEFINE AL USUARIO CON AMBOS ATRIBUTOS

            if laBaseDeDatos.Usuarios.find({"_id": laDireccion}).count() == 0:                                                          #SI NO EXISTE EL USUARIO EN LA BASE DE DATOS
                laBaseDeDatos.Usuarios.insert_one(elUsuario)                                                                            #INSERTA EL USUARIO
            else:
                laBaseDeDatos.Usuarios.update({"_id": laDireccion}, {"Nombre": elNombre})                                               #ACTUALIZA EL NOMBRE

            elLog = {"_id": str(ObjectId()), "Usuario": elNombre, "Fecha": datetime.datetime.now(), "Accion": "Bienvenida 'POST'"}      #DEFINE EL LOG
            laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                             #INSERTA EL LOG A LABASE DE DATOS
            elTexto = '¡Hola ' + elNombre + '! ¿En qué puedo ayudarte?'                                                                 #SE CREA LA RESPUESTA
            laRespuesta = json.dumps(elTexto)                                                                                           #SE CONVIERTE A JSON
            return Response(laRespuesta, 200, mimetype="application/json")                                                              #SE RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS
    except Exception as e:
        return formateeElError(e)

@app.route('/api/web-bot/operaciones', methods=['GET'])
def mostrarOperaciones():
    elResultado = {}                                                                                                            #DEFINE UN DICCIONARIO VACIO
    elContador = 1                                                                                                              #DEFINE UN CONTADOR
    losLogs = laBaseDeDatos.Log_Operaciones.find()                                                                              #OBTIENE TODOS LOS LOGS DE OPERACIONES
    for cadaLog in losLogs:                                                                                                     #PARA CADA LOG QUE TRAE
        elJSON = json.dumps(cadaLog)                                                                                            #LO CONVIERTE A JSON
        elResultado["Operacion_"+str(elContador)] = elJSON                                                                      #AGREGA CADA VALOR AL DICCIONARIO
        elContador += 1                                                                                                         #AUMENTA EL CONTADOR

    elUsuario = definaElUsuario()                                                                                               #DEFINE EL USUARIO
    elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Operaciones"}           #DEFINE EL LOG
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                             #INSERTA EL LOG A LA BASE DE DATOS
    laRespuesta = json.dumps(elResultado)                                                                                       #CONVERTE EL DICCIONARIO A JSON
    return Response(laRespuesta, 200, mimetype="application/json")                                                              #RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS

@app.route('/api/web-bot/memoria', methods=['GET'])
def mostrarMemoria():
    elResultado = {}                                                                                                            #DEFINE UN DICCIONARIO VACIO
    elContador = 1                                                                                                              #DEFINE UN CONTADOR
    laMemoria = laBaseDeDatos.Memoria_Aprendizaje.find()                                                                        #OBTIENE LO QUE HA APRENDIDO
    for cadaMemoria in laMemoria:                                                                                               #PARA CADA COSA QUE SABE
        elJSON = json.dumps(cadaMemoria)                                                                                        #LO CONVIERTE A JSON
        elResultado["Memoria_"+str(elContador)] = elJSON                                                                        #AGREGA LOS DOS VALORES AL RESULTADO
        elContador += 1                                                                                                         ##AUMENTA EL CONTADOR

    elUsuario = definaElUsuario()                                                                                               #DEFINE EL USUARIO
    elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Memoria"}               #DEFINE EL LOG
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                             #INSERTA EL LOG A LA BASE DE DATOS
    laRespuesta = json.dumps(elResultado)                                                                                       #CONVERTE EL DICCIONARIO A JSON
    return Response(laRespuesta, 200, mimetype="application/json")                                                              #RETORNA LA RESPUESTA CON LOS DATOS NECESARIOS

@app.route('/api/web-bot/aprender', methods=['POST'])
def aprender():
    laInformacion = request.json                                                                                                                            #OBTIENE EL JSON ENVIADO
    elJSON = json.dumps(laInformacion)                                                                                                                      #LO CONVIERTE A JSON
    elParseo = json.loads(elJSON)                                                                                                                           #LO CARGA PARA PERMITIR PARSEAR
    elNombre = elParseo["Nombre"]                                                                                                                           #OBTIENE EL VALOR DEL CAMPO NOMBRE

    if laBaseDeDatos.Memoria_Aprendizaje.find({"Nombre": elNombre}).count() > 0:                                                                            #SI YA SABE HACER LA ACCION
        elUsuario = definaElUsuario()                                                                                                                       # DEFINE EL USUARIO
        elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Aprender: " + elNombre + " (Ya existente)"}     #DEFINE EL LOG
        laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                                     #INSERTA EL LOG A LA BASE DE DATOS
        elTexto = "Lo lamento. Ya sé cómo: " + elNombre                                                                                                     #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                                                                                   #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                                                                                      #RETORNA UN MENSAJE NEGATIVO ADECUADO

    laInformacion['_id'] = str(ObjectId())                                                                                                                  #LE AGREGA UN ID A LO QUE APRENDE
    laBaseDeDatos.Memoria_Aprendizaje.insert_one(laInformacion)                                                                                             #AGREGA LA ACCION A LA BASE DE DATOS

    elUsuario = definaElUsuario()                                                                                                                           #DEFINE EL USUARIO
    elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Aprender: " + elNombre}                             #DEFINE EL LOG
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                                         #INSERTA EL LOG A LA BASE DE DATOS
    elTexto = "He aprendido a: " + elNombre                                                                                                                 #GENERA EL TEXTO DE RESPUESTA
    laRespuesta = json.dumps(elTexto)                                                                                                                       #LO CONVIERTE A JSON
    return Response(laRespuesta, 200, mimetype="application/json")                                                                                          #RETORNA UN MENSAJE POSITIVO ADECUADO

@app.route('/api/web-bot/olvidar', methods=['POST'])
def olvidar():
    elArgumento = request.args                                                                                                                  #OBTIENE LOS PARAMETROS ENVIADOS
    laAccion = elArgumento['laAccion']                                                                                                          #OBTIENE EL VALOR DEL CAMPO ACCION
    elConocimiento = laBaseDeDatos.Memoria_Aprendizaje.find_one({'Nombre':laAccion})                                                            #BUSCA SI LA ACCION EXISTE
    if elConocimiento != None:                                                                                                                  #SI EXISTE
        laBaseDeDatos.Memoria_Aprendizaje.delete_one({'Nombre': laAccion})                                                                      #LA BORRA DE LA BASE DE DATOS
    else:                                                                                                                                       #SI NO
        elUsuario = definaElUsuario()                                                                                                           # DEFINE EL USUARIO
        elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Olvidar: " + laAccion + " (N/A)"}   #DEFINE EL LOG
        laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                         #LO INSERTA EN LA BASE DE DATOS
        elTexto = "No puedo olvidar algo que nunca supe hacer..."                                                                               #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                                                                       #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                                                                          #RETORNA UN MENSAJE NEGATIVO ADECUADO

    elUsuario = definaElUsuario()                                                                                                               #DEFINE EL USUARIO
    elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Olvidar: " + laAccion}                  #DEFINE EL LOG
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                             #LO INSERTA EN LA BASE DE DATOS
    elTexto = "He olvidado: " + laAccion                                                                                                        #GENERA EL TEXTO DE RESPUESTA
    laRespuesta = json.dumps(elTexto)                                                                                                           #LO CONVIERTE A JSON
    return Response(laRespuesta, 200, mimetype="application/json")                                                                              #RETORNA UN MENSAJE POSITIVO ADECUADO

@app.route('/api/web-bot/hacer/<accion>', methods=['GET', 'POST'])
def realizarAccion(accion):
    if request.method == 'POST':                                                                                                                    #SI EL METODO ES POST
        losParametros = request.args                                                                                                                #OBTIENE LOS PARAMETROS ENVIADOS
        losParametrosComoDiccionario = dict(losParametros)                                                                                          #LOS CONVIERTE EN UN DICCIONARIO
        laCantidadDeParametros = len(losParametrosComoDiccionario)                                                                                  #CUENTA LA CANTIDAD DE PARAMETROS

        if laCantidadDeParametros >= 1:                                                                                                             #SI ES UNO O MAS PARAMETROS
            Parametro1 = losParametros['Parametro1']                                                                                                #OBTIENE EL PRIMER PARAMETRO
            if Parametro1.isnumeric():                                                                                                              #SI EL PARAMETRO ES UN NUMERO
                Parametro1 = int(Parametro1)                                                                                                        #LO CONVIERTE A UN NUMERO
        if laCantidadDeParametros >= 2:                                                                                                             #SI SON DOS O MAS PARAMETROS
            Parametro2 = losParametros['Parametro2']                                                                                                #OBTIENE EL SEGUNDO PARAMETRO
            if Parametro2.isnumeric():                                                                                                              #SI EL PARAMETROS ES UN NUMERO
                Parametro2 = int(Parametro2)                                                                                                        #LO CONVIERTE A UN NUMERO
        if laCantidadDeParametros >= 3:                                                                                                             #SI SON TRES O MAS PARAMETROS
            Parametro3 = losParametros['Parametro3']                                                                                                #OBTIENE EL TERCER PARAMETROS
            if Parametro3.isnumeric():                                                                                                              #SI EL PARAMETRO ES UN NUMERO
                Parametro3 = int(Parametro3)                                                                                                        #LO CONVIERTE A UN NUMERO

    laAccion = laBaseDeDatos.Memoria_Aprendizaje.find_one({"Nombre": accion})                                                                       #BUSCA SI LA ACCION EXISTE
    if laAccion != None:                                                                                                                            #SI EXISTE
        elJSON = json.dumps(laAccion)                                                                                                               #LA CONVIERTE A JSON
        elParseo = json.loads(elJSON)                                                                                                               #LA CARGA PARA PERMITIR PARSEAR
        elCodigo = elParseo['Instruccion']                                                                                                          #OBTIENE EL VALOR DEL CAMPO INSTRUCCION
    else:                                                                                                                                           #SI NO
        elUsuario = definaElUsuario()                                                                                                               # DEFINE EL USUARIO
        elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Realizar: " + accion + " (N/A)"}        #DEFINE EL LOG
        laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                             #INSERTA EL LOG A LA BASE DE DATOS
        elTexto = "Lo lamento. No sé cómo: " + accion                                                                                               #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                                                                           #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                                                                              #RETORNA UN MENSAJE NEGATIVO ADECUADO

    elResultado = StringIO()                                                                                                                        #VARIABLE ESPECIAL PARA GUARDAR TEXTO
    sys.stdout = elResultado                                                                                                                        #LO QUE IMPRIMA, LO GUARDA EN LA VARIABLE
    exec(elCodigo)                                                                                                                                  #EJECUTAMOS EL CODIGO DE LA INSTRUCCION
    sys.stdout = sys.__stdout__                                                                                                                     #LO QUE IMPRIMA, LO IMPRIME EN CONSOLA

    elUsuario = definaElUsuario()                                                                                                                   #DEFINE EL USUARIO
    elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Realizar: " + accion}                       #DEFINE EL LOG
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                                 #INSERTA EL LOG A LA BASE DE DATOS
    elTexto = elResultado.getvalue()                                                                                                                #GENERA EL TEXTO DE RESPUESTA
    laRespuesta = json.dumps(elTexto)                                                                                                               #LO CONVIERTE A JSON
    return Response(laRespuesta, 200, mimetype="application/json")                                                                                  #RETORNA UN MENSAJE POSITIVO ADECUADO


@app.route('/api/web-bot/ejecutar/<accion>', methods=['GET','POST'])
def ejecutarAccion(accion):
    if request.method == 'POST':                                                                                                                    #SI EL METODO ES POST
        losParametros = request.args                                                                                                                #OBTIENE LOS PARAMETROS
        losParametrosComoDiccionario = dict(losParametros)                                                                                          #LOS CONVIERTE EN UN DICCIONARIO
        laCantidadDeParametros = len(losParametrosComoDiccionario)                                                                                  #CUENTA LA CANTIDAD DE PARAMETROS

        if laCantidadDeParametros >= 1:                                                                                                             #SI ES UNO O MAS PARAMETROS
            Parametro1 = losParametros['Parametro1']                                                                                                #OBTIENE EL PRIMER PARAMETRO
            if Parametro1.isnumeric():                                                                                                              #SI EL PARAMETROS ES UN NUMERO
                Parametro1 = int(Parametro1)                                                                                                        #LO CONVIERTE A NUMERO
        if laCantidadDeParametros >= 2:                                                                                                             #SI SON DOS O MAS PARAMETROS
            Parametro2 = losParametros['Parametro2']                                                                                                #OBTIENE EL SEGUNDO PARAMETROS
            if Parametro2.isnumeric():                                                                                                              #SI EL PARAMETROS ES UN NUMERO
                Parametro2 = int(Parametro2)                                                                                                        #LO CONVIERTE A NUMERO
        if laCantidadDeParametros >= 3:                                                                                                             #SI SON TRES O MAS PARAMETROS
            Parametro3 = losParametros['Parametro3']                                                                                                #OBTIENE EL TERCER PARAMETRO
            if Parametro3.isnumeric():                                                                                                              #SI EL PARAMETROS ES UN NUMERO
                Parametro3 = int(Parametro3)                                                                                                        #LO CONVIERTE A NUMERO

    laAccion = laBaseDeDatos.Memoria_Aprendizaje.find_one({"Nombre": accion})                                                                       #BUSCA SI LA ACCION EXISTE
    if laAccion != None:                                                                                                                            #SI EXISTE
        elJSON = json.dumps(laAccion)                                                                                                               #LA CONVIERTE A JSON
        elParseo = json.loads(elJSON)                                                                                                               #LA CARGA PARA PERMITIR PARSEO
        elCodigo = elParseo['Instruccion']                                                                                                          #OBTIENE EL VALOR DEL CAMPO INSTRUCCION
    else:                                                                                                                                           #SI NO
        elUsuario = definaElUsuario()                                                                                                               #DEFINE EL USUARIO
        elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Ejecutar: " + accion + " (N/A)"}        #DEFINE EL LOG
        laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                             #INSERTA EL LOG A LA BASE DE DATOS
        elTexto = "Lo lamento. No sé cómo: " + accion                                                                                               #GENERA EL TEXTO DE RESPUESTA
        laRespuesta = json.dumps(elTexto)                                                                                                           #LO CONVIERTE A JSON
        return Response(laRespuesta, 200, mimetype="application/json")                                                                              #RETORNA UN MENSAJE NEGATIVO ADECUADO

    exec(elCodigo)                                                                                                                                  #EJECUTA EL CODIGO DE LA INSTRUCCION

    elUsuario = definaElUsuario()                                                                                                                   #DEFINE EL USUARIO
    elLog = {"_id": str(ObjectId()), "Usuario": elUsuario, "Fecha": datetime.datetime.now(), "Accion": "Ejecutar: " + accion}                       #DEFINE EL LOG
    laBaseDeDatos.Log_Operaciones.insert_one(elLog)                                                                                                 #INSERTA EL LOG A LA BASE DE DATOS
    elTexto = "Ejecutando: " + accion                                                                                                               #GENERA EL TEXTO DE RESPUESTA
    laRespuesta = json.dumps(elTexto)                                                                                                               #LO CONVIERTE A JSON
    return Response(laRespuesta, 200, mimetype="application/json")                                                                                  #RETORNA UN MENSAJE POSITIVO ADECUADO

def definaElUsuario():
    elUsuario = request.remote_addr                                     #OBTIENE LA DIRECCION IP DEL USUARIO
    laSolicitud = laBaseDeDatos.Usuarios.find_one({"_id": elUsuario})   #REVISA SI LA DIRECCION YA EXISTE
    if laSolicitud != None:                                             #SI EXISTE
        elUsuario = laSolicitud["Nombre"]                               #OBTIENE EL NOMBRE DEL USUARIO
    return elUsuario                                                    #RETORNA EL NOMBRE O LA DIRECCION DEL USUARIO

def formateeElError(e):
    elErrorComoTexto = str(e)
    elEnunciado = "Lo lamento. Ha ocurrido un error " + elErrorComoTexto
    elEnunciadoComoJSON = json.dumps(elEnunciado)
    elErrorHTTP = elErrorComoTexto[:3]
    return Response(elEnunciadoComoJSON, elErrorHTTP, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

#TODO: HACER TRY-CATCH PARA CUALQUIER ERROR EN CADA METODO
#TODO: COMENTAR LAS NUEVAS LINEAS
#TODO: REVISAR LA VERIFICACION DE RUTAS
#TODO: RAISE ERROR EN CUENTA DE PARAMETROS