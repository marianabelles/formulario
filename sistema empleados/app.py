from flask import Flask 
from flask import render_template,request,redirect,url_for,flash
from flaskext.mysql import MySQL 
import os
from datetime import datetime #Nos permitirá darle el nombre a la foto
from flask import send_from_directory 



app = Flask(__name__)
app.secret_key="ClaveSecreta" 
mysql = MySQL()


app.config['MYSQL_DATABASE_HOST']='localhost' 
app.config['MYSQL_DATABASE_USER']='root' 
app.config['MYSQL_DATABASE_PASSWORD']='' 
app.config['MYSQL_DATABASE_DB']='sistema' 
mysql.init_app(app) 

CARPETA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>') 
def uploads(nombreFoto): 
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/') 
def index(): 
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT * FROM `sistema`.`empleados`;" 
    cursor.execute(sql)
    empleados=cursor.fetchall()
    print(empleados)
    conn.commit()
    cursor.close()
    conn.close()
    
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT foto FROM `sistema`.`empleados` WHERE id=%s", id) 
    fila= cursor.fetchall() 
    
    if fila [0]:
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) 
    cursor.execute("DELETE FROM `sistema`.`empleados` WHERE id=%s", (id))
    conn.commit()
    
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    # Ejecuta la consulta para obtener el empleado por ID
    cursor.execute("SELECT * FROM `sistema`.`empleados` WHERE id=%s", (id,))
    empleados = cursor.fetchall()
    
    # Cierra el cursor y la conexión
    cursor.close()
    conn.close()

    # Verifica si se encontró el empleado
    if not empleados:
        flash('Empleado no encontrado.')
        return redirect(url_for('index'))  # Cambia 'index' al nombre de tu ruta principal si es diferente

    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']
    
    sql = "UPDATE `sistema`.`empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;"
    datos=(_nombre,_correo,id)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    
    now= datetime.now() 
    tiempo= now.strftime("%Y%H%M%S")
    
    if _foto.filename!='': 
        nuevoNombreFoto=tiempo+_foto.filename 
        _foto.save("uploads/"+nuevoNombreFoto) 
    
        cursor.execute("SELECT foto FROM `sistema`.`empleados` WHERE id=% s", id) 
        fila= cursor.fetchall() 
 
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))  
        cursor.execute("UPDATE `sistema`.`empleados` SET foto=%s WHERE id =%s;", (nuevoNombreFoto, id)) 
        conn.commit() 

    cursor.execute(sql,datos)
    conn.commit()
    
    return redirect('/')

# Ruta para crear empleado
@app.route('/create')
def create():
    return render_template('empleados/create.html')


# Ruta para almacenar empleado
@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    if _nombre == '' or _correo == '' or _foto =='': 
        flash('Recuerda llenar los datos de los campos') 
        return redirect(url_for('create')) 

    now= datetime.now() #obtuvimos la fecha y hora actual
    tiempo= now.strftime("%Y%H%M%S")
    if _foto.filename!='': #si hay una foto adjuntada, entonces que se genere el nuevo nombre de la foto, concatenando el tiempo en el que fue subida con su nombre.
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        
        # Guardar datos en la base de datos
        sql = "INSERT INTO `sistema`.`empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
        datos=(_nombre,_correo,nuevoNombreFoto)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, datos)
        conn.commit()

    cursor.close()
    conn.close()
    
    return redirect('/') 

if __name__=='__main__': 
    app.run(debug=True)