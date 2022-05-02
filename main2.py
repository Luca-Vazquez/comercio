
import tkinter as tk
from tkinter import messagebox
import time
from click import command
import requests
import sys
import sqlite3


def guardarVentas(lista):
    conn = sqlite3.connect("comercio.sqlite")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ventas VALUES (null, ?, ?, ?, ?, ?, ?, ?)", (lista))
    except:
        cursor.execute("""CREATE TABLE ventas 
        ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            fecha TEXT,
            ComboS INT,
            ComboD INT,
            ComboT INT,
            Flurby INT,
            total REAL
        )
        """)
        cursor.execute("INSERT INTO ventas VALUES (null, ?, ?, ?, ?, ?, ?, ?)", (lista))
    conn.commit()
    conn.close()

def guardarEncargado(data):
    dataIN = (data["nombre"], data["ingreso"], "IN", 0)
    dataOUT = (data["nombre"], data["egreso"], "OUT", data["facturado"])
    conn = sqlite3.connect("comercio.sqlite")
    cursor = conn.cursor()
    try:
        if data["egreso"] == 0:
            cursor.execute("INSERT INTO registro VALUES (null,?,?,?,?)", dataIN)
        else:
            cursor.execute("INSERT INTO registro VALUES (null,?,?,?,?)", dataOUT)
    except sqlite3.OperationalError:
        cursor.execute("""CREATE TABLE registro 
        ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encargado TEXT,
            fecha TEXT,
            evento TEXT,
            caja REAL
        )
        """)
        if data["egreso"] == 0:
            cursor.execute("INSERT INTO registro VALUES (null,?,?,?,?)", dataIN)
        else:
            cursor.execute("INSERT INTO registro VALUES (null,?,?,?,?)", dataOUT)
    conn.commit()
    conn.close



def borrar():
    combo1caja.delete(0, tk.END)
    combo2caja.delete(0,tk.END)
    combo3caja.delete(0,tk.END)
    postrecaja.delete(0,tk.END)
    clientecaja.delete(0,tk.END)

def cancelar_pedido():
    respuesta = messagebox.askyesno(title="Cancelar", message=("Desea cancelar el pedido?"))
    if respuesta:
        borrar()

def cotizar():
    try:
        r = requests.get("https://api-dolar-argentina.herokuapp.com/api/dolaroficial")
        valor = r.json()["venta"]
        valor = round(float(valor))
        return valor
    except:
        messagebox.showerror(title="Error grave", message="Sin internet para cotizar. Terminado")
        sys.exit()

def int_val(dato):
	try:
		dato = int(dato)
		return dato
	except ValueError:
		return -1

def pedir():
    cantc1 = combo1caja.get()
    cantc1 = int_val(cantc1)
    cantc2 = combo2caja.get()
    cantc2 = int_val(cantc2)
    cantc3 = combo3caja.get()
    cantc3 = int_val(cantc3)
    cantpostre = postrecaja.get()
    cantpostre = int_val(cantpostre)
    dolar = cotizar()
    if cantc1>=0 and cantc2>=0 and cantc3>=0 and cantpostre>=0:
        nombre_cliente = clientecaja.get()
        encargado1 = datosEncargado["nombre"]
        encargado = encargadocaja.get()
        if nombre_cliente and encargado:
            respuesta = messagebox.askyesno(title="Pregunta", message="¿Confirma el pedido?")
            if respuesta:
                totald = ((cantc1*precios["ComboSimple"]) + (cantc2*precios["ComboDoble"]) + (cantc3*precios["ComboTriple"]) + (cantpostre*precios["Flurby"]))
                total = totald * dolar
                fecha = time.asctime()
                pedido = [nombre_cliente, fecha, cantc1, cantc2, cantc3, cantpostre, total]
                messagebox.showinfo(title="A pagar", message="$"+str(total))
                guardarVentas(pedido)
                messagebox.showinfo(title="Información", message="Pedido Exitoso")
                if  datosEncargado["nombre"] != encargado and datosEncargado["egreso"] == "" :
                    datosEncargado["nombre"] = encargado
                    datosEncargado["egreso"] = 0
                    datosEncargado["facturado"] += total
                    guardarEncargado(datosEncargado)
                elif encargado == encargado1:
                    datosEncargado["facturado"] += total 
                else:
                    datosEncargado["egreso"] = fecha
                    guardarEncargado(datosEncargado) 
                    
                    datosEncargado["nombre"] = encargado
                    datosEncargado["Ingreso"] = fecha
                    datosEncargado["facturado"] = 0
                    datosEncargado["facturado"] += total
                    datosEncargado["egreso"] = 0
                    guardarEncargado(datosEncargado)
                borrar()
            else:
                messagebox.showinfo(title="Información", message="Pedido en pausa")
        else:
            messagebox.showwarning(title="Advertencia", message="Error, ingrese bien los datos")
    else:
        messagebox.showwarning(title="Advertencia", message="Por favor, ingrese valores válidos.")
  
def salir():
    respuesta = messagebox.askyesno(title="Pregunta", message="¿Desea salir?")
    if respuesta:
        datosEncargado["egreso"] = time.asctime()
        guardarEncargado(datosEncargado)
        sys.exit()




#######################################################################

precios = {"ComboSimple":5,"ComboDoble":6,"ComboTriple":7,"Flurby":2}
datosEncargado = {"nombre":"","ingreso":time.asctime(),"egreso":"","facturado":0}

######################################################
ventana_principal = tk.Tk()
ventana_principal.title("Comercio")
ventana_principal.config(width=400, height=500)
#####################################################
#Etiquetas
pedidolabel = tk.Label(text="----Pedido----")
pedidolabel.place(x=155, y=0)

encargadolabel = tk.Label(text="Nombre Encargado:")
encargadolabel.place(x=30, y=90)

combo1label = tk.Label(text= "Combo S cantidad:")
combo1label.place(x=30, y=130)

combo2label = tk.Label(text="Combo D cantidad:")
combo2label.place(x=30, y=170)

combo3label = tk.Label(text="Combo T cantidad:")
combo3label.place(x=30, y=210)

postrelabel = tk.Label(text="Postre cantidad:")
postrelabel.place(x=30, y=250)

clientelabel = tk.Label(text="Nombre del cliente:")
clientelabel.place(x=30, y=290)

#Botones
botonsalir = tk.Button(text="Salir seguro", command=salir)
botonsalir.place(x = 30 , y = 330, height=40, width = 100)

botoncancelar = tk.Button(text="Cancelar pedido", command=cancelar_pedido)
botoncancelar.place(x = 150 , y = 330, height=40, width = 100)

botonpedido = tk.Button(text="Hacer Pedido", command=pedir)
botonpedido.place(x = 270 , y = 330, height=40, width = 100)

#Cajas
encargadocaja = tk.Entry()
encargadocaja.place(x=230, y=90)

combo1caja = tk.Entry()
combo1caja.place(x=230, y=130)

combo2caja = tk.Entry()
combo2caja.place(x=230, y=170)

combo3caja = tk.Entry()
combo3caja.place(x=230, y=210)

postrecaja = tk.Entry()
postrecaja.place(x=230, y=250)

clientecaja = tk.Entry()
clientecaja.place(x=230, y=290)


ventana_principal.mainloop()