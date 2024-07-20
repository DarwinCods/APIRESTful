# Importamos librerias y modulos a utilizar
from abc import ABC, abstractmethod
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import sqlite3


# Creamos la conexion a la DB
try:
    conexion = sqlite3.connect("obras.db")
    cursor_pelicula = conexion.cursor() # Creamos el cursor para interactuar con la DB con la tabla de pelicula
    cursor_libro = conexion.cursor() # Creamos el cursor para interactuar con la DB con la tabla de libro
except sqlite3.Error as e:
    print(f"Ocurrio un error en la conexion: {e}")

# Creamos clase abstracta para las subclases de Libro y Pelicula
class Obra(BaseModel, ABC):
    # Definimos atributos relacionadas a las dos subclases
    titulo: str
    descripcion: Optional[str]
    precio: float

    # Creamos un metodo abstracto para ingresar datos a las tablas correspondientes
    @abstractmethod
    def insert_data(self):
        pass
    
    # Creamos un metodo abstracto para mostrar datos de manera general
    @abstractmethod
    def show_data():
        pass

# Creamos la subclase Libro que hereda de Obras
class Libro(Obra):

    # añadimos un atributo propio de la clase
    autor: str

    # Metodo para insertar datos
    def insert_data(self):
        try:
            cursor_libro.execute("INSERT INTO libros (titulo, descripcion, autor, precio) VALUES (?, ?, ?, ?)",
                        (self.titulo, self.descripcion, self.autor, self.precio))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al insertar el registro: {e}")
            return RedirectResponse("/", status_code=404)

    # Metodo para actualizar un dato
    def updata_data(self, id):
        try:
            cursor_pelicula.execute("UPDATE libros SET titulo = ?, descripcion = ?, autor = ? , precio = ? WHERE id = ?", 
                        (self.titulo, self.descripcion, self.autor,self.precio, id))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al actualizar el registro: {e}")

    # Metodo estatico para consultar a la tabla de libros
    @staticmethod
    def show_data():
        try:
            cursor_libro.execute("SELECT * FROM libros")
            return cursor_libro.fetchall()
        except sqlite3.Error as e:
            print(f"Error al mostrar los datos: {e}")
    
    # Metodo estatico para eliminar un dato
    @staticmethod
    def delete_data(id:int):
        try:
            cursor_libro.execute(f"DELETE FROM libros WHERE id = {id}")
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al eliminar registro: {e}")
    
    # Metodo para obtener un registro
    @staticmethod
    def specific_data(id:int):
        cursor_libro.execute(f"SELECT * FROM libros WHERE id = {id}")
        return cursor_libro.fetchone()
    

# Creamos la subclase Pelicula que hereda de la clase abstracta Obra
class Pelicula(Obra):
    # añadimos un atributo propio de Pelicula
    director: str

    # Metodo para insertar peliculas
    def insert_data(self):
        cursor_pelicula.execute("INSERT INTO peliculas (titulo, descripcion, director, precio) VALUES (?, ?, ?, ?)",
                       (self.titulo, self.descripcion, self.director, self.precio))
        conexion.commit()

    # Metodo para actualizar un dato
    def updata_data(self, id):
        cursor_pelicula.execute("UPDATE peliculas SET titulo = ?, descripcion = ?, director = ? , precio = ? WHERE id = ?", 
                       (self.titulo, self.descripcion, self.director,self.precio, id))
        conexion.commit()

    # Metodo estatico para eliminar un dato
    @staticmethod
    def delete_data(id:int):
        cursor_pelicula.execute(f"DELETE FROM peliculas WHERE id = {id}")
        conexion.commit()

    # Metodo estatico para mostrar las peliculas
    @staticmethod
    def show_data():
        cursor_pelicula.execute("SELECT * FROM peliculas")
        return cursor_pelicula.fetchall()
    
    @staticmethod
    def specific_data(id:int):
        cursor_pelicula.execute(f"SELECT * FROM peliculas WHERE id = {id}")
        return cursor_pelicula.fetchone()
    
# Creamos la app de FastApi
app = FastAPI()

# Usamos Jinja2 para usar templates con FastApi
templates = Jinja2Templates(directory="templates")

# Especificamos la carpeta de static para añadir estilos a nuestras estructuras HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

# Añadimos titulo a la documentacion de FastApi
app.title = "API RESTful con FastApi"

@app.get("/", tags=["Home"], response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/secciones/peliculas", tags=["Peliculas"], response_class=HTMLResponse)
async def movies(request: Request):
    try:
        message = Pelicula.show_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrio un error al consultar los registros: {str(e)}")
    return templates.TemplateResponse("peliculas.html", {"request":request, "message":message})

@app.get("/secciones/peliculas/insertar", tags=["Peliculas"], response_class=HTMLResponse)
async def movie_template(request: Request):
    return templates.TemplateResponse("form_peliculas.html",{"request":request})

@app.post("/secciones/peliculas/insertar/submit", tags=["Home"])
async def form_create_movie(titulo: str = Form(...), descripcion: str = Form(...), director: str = Form(...), precio: float = Form(...)):
    try:
        pelicula = Pelicula(titulo=titulo, descripcion=descripcion, director=director, precio=precio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        pelicula.insert_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return RedirectResponse("/secciones/peliculas", status_code=303)

@app.get("/secciones/peliculas/actualizar/{id:int}", tags=["Peliculas"], response_class=HTMLResponse)
async def form_update_movie(request:Request, id:int):
    try:
        info = Pelicula.specific_data(id)
        titulo = info[1]
        descripcion = info[2]
        director = info[3]
        precio = info[4]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("form_peliculas_act.html",{"request":request, "id":id, "titulo":titulo,"descripcion": descripcion, "director":director, "precio":precio})

"""
@app.put("/secciones/peliculas/actualizar/{id:int}/submit", tags=["Home"])
async def act_pelicula(id:int, titulo: str = Form(...), descripcion:str = Form(None), director:str= Form(...), precio:float=Form(...)):
    act = Pelicula(titulo=titulo,descripcion=descripcion,director=director,precio=precio)
    act.updata_data(id)
    return {"message": "Actualizacion realizada!"}
"""
@app.put("/secciones/peliculas/actualizar/{id:int}/submit", tags=["Peliculas"])
async def update_movie(id:int, pelicula:Pelicula):
    try:
        act = Pelicula(titulo=pelicula.titulo,descripcion=pelicula.descripcion,director=pelicula.director,precio=pelicula.precio)
        act.updata_data(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Actualizacion realizada!"}

@app.delete("/secciones/peliculas/eliminar/{id:int}/submit", tags=["Peliculas"])
async def delete_movie(id:int):
    Pelicula.delete_data(id)
    return RedirectResponse("/secciones/peliculas", status_code=200)

# Endpoints Books

@app.get("/secciones/libros", tags=["Libro"], response_class=HTMLResponse)
async def libros(request: Request):
    libros = Libro.show_data()
    return templates.TemplateResponse("libros.html", {"request": request, "libros": libros})

@app.get("/secciones/libros/insertar", tags=["Home"], response_class=HTMLResponse)
async def template_libro(request: Request):
    return templates.TemplateResponse("form_libros.html", {"request": request})

@app.post("/secciones/libros/insertar/submit", tags=["Libro"])
async def insertar_libros(titulo: str = Form(...), descripcion: str = Form(None), autor: str = Form(...), precio: float = Form(...)):
    item = Libro(titulo=titulo, descripcion=descripcion, autor=autor, precio=precio)
    item.insert_data()
    return RedirectResponse("/secciones/libros", status_code=303)

@app.get("/secciones/libros/actualizar/{id:int}", response_class=HTMLResponse)
async def form_update_book(request:Request, id:int):
    info = Libro.specific_data(id)
    titulo = info[1]
    descripcion = info[2]
    autor = info[3]
    precio = info[4]
    return templates.TemplateResponse("form_libros_act.html",{"request":request,"id":id ,"titulo":titulo, "descripcion":descripcion, "autor":autor, "precio":precio})

@app.put("/secciones/libros/actualizar/{id:int}/submit")
async def form_update_libro(id:int, libro:Libro):
    libro = Libro(titulo=libro.titulo,descripcion=libro.descripcion,autor=libro.autor,precio=libro.precio)
    libro.updata_data(id)
    return RedirectResponse("/secciones/libros", status_code=303)

@app.delete("/secciones/libros/eliminar/{id:int}/submit")
async def delete_book(id:int):
    Libro.delete_data(id)
    return RedirectResponse("/secciones/libros", status_code=303)
    


