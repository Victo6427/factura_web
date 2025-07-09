import os
import webbrowser
from flask import Flask, render_template, request, send_file
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
FACTURAS_DIR = os.path.join(BASE_DIR, 'facturas')
os.makedirs(FACTURAS_DIR, exist_ok=True)

app = Flask(__name__, template_folder=TEMPLATES_DIR)

# Función para convertir tildes a formato RTF
def convertir_rtf(texto):
    rtf_dict = {
        "á": "\\'e1", "é": "\\'e9", "í": "\\'ed", "ó": "\\'f3", "ú": "\\'fa",
        "Á": "\\'c1", "É": "\\'c9", "Í": "\\'cd", "Ó": "\\'d3", "Ú": "\\'da",
        "ñ": "\\'f1", "Ñ": "\\'d1"
    }
    return ''.join(rtf_dict.get(c, c) for c in texto)

@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/generar', methods=['POST'])
def generar():
    cliente = request.form['cliente']
    cedula = request.form['cedula']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    fecha_factura = request.form['fecha_factura']
    fecha_vencimiento = request.form['fecha_vencimiento']
    forma_pago = request.form['forma_pago']

    productos = []
    for i in range(1, 6):
        desc = request.form.get(f'descripcion{i}', '')
        if desc.strip() == "":
            continue
        unidades = int(request.form.get(f'unidades{i}', 0))
        precio = float(request.form.get(f'precio{i}', 0.0))
        productos.append((desc, unidades, precio))

    subtotal = sum(u * p for _, u, p in productos)
    iva = subtotal * 0.12
    total = subtotal + iva

    nombre_archivo = os.path.join(FACTURAS_DIR, f"factura_{cliente.replace(' ', '')}{datetime.now().strftime('%Y%m%d%H%M%S')}.rtf")

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("{\\rtf1\\ansi\\deff0\n")
        f.write("\\fs32\\b COMPUCELL TECHNOLOGY\\b0\\fs20\\line\n")
        f.write("Direcci\\'f3n: Av. Leopoldo Freire y Washington, local 593\\line\n")
        f.write("Ciudad: Riobamba, Chimborazo, Ecuador\\line\n")
        f.write("Tel\\'e9fono: 0982443963\\line\n")
        f.write("Email: compucelltech@gmail.com\\line\n")
        f.write("Factura No.: 001-001-00001234\\line\n")
        f.write("\\line\n")

        f.write("\\b DATOS DEL CLIENTE\\b0\\line\n")
        f.write(f"Nombre: {convertir_rtf(cliente)}\\line\n")
        f.write(f"C\\'e9dula/RUC: {convertir_rtf(cedula)}\\line\n")
        f.write(f"Direcci\\'f3n: {convertir_rtf(direccion)}\\line\n")
        f.write(f"Tel\\'e9fono: {convertir_rtf(telefono)}\\line\n")
        f.write(f"Fecha de Factura: {convertir_rtf(fecha_factura)}\\line\n")
        f.write(f"Fecha de Vencimiento: {convertir_rtf(fecha_vencimiento)}\\line\n")
        f.write("\\line\n")

        f.write("\\b DETALLE DE PRODUCTOS\\b0\\line\n")
        f.write("Descripci\\'f3n\\tab Unidades\\tab Precio Unitario\\tab Total\\line\n")
        f.write("\\line\n")
        for d, u, p in productos:
            total_linea = u * p
            f.write(f"{convertir_rtf(d)}\\tab {u}\\tab ${p:.2f}\\tab ${total_linea:.2f}\\line\n")
        f.write("\\line\n")

        f.write(f"\\b Subtotal:\\b0\\tab ${subtotal:.2f}\\line\n")
        f.write(f"\\b IVA (12%):\\b0\\tab ${iva:.2f}\\line\n")
        f.write(f"\\b Total a pagar:\\b0\\tab ${total:.2f}\\line\n")
        f.write(f"\\b Forma de pago:\\b0\\tab {convertir_rtf(forma_pago)}\\line\n")
        f.write("\\line\n")

        f.write("Gracias por su compra. \\u161?Esperamos volver a verte pronto!\\line\n")
        f.write("}")

    return send_file(nombre_archivo, as_attachment=True)

if __name__ == '__main__':
    webbrowser.open("http://localhost:5000")
    app.run(debug=True, use_reloader=False)