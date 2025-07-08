from flask import Flask, render_template, request, send_file
from datetime import datetime
import os

app = Flask(__name__)

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

    # Obtener productos
    productos = []
    for i in range(1, 6):  # soporta hasta 5 productos
        desc = request.form.get(f'descripcion{i}', '')
        if desc.strip() == "":
            continue
        unidades = int(request.form.get(f'unidades{i}', 0))
        precio = float(request.form.get(f'precio{i}', 0.0))
        productos.append((desc, unidades, precio))

    # Calcular totales
    subtotal = sum(u * p for _, u, p in productos)
    iva = subtotal * 0.12
    total = subtotal + iva

    nombre_archivo = f"facturas/factura_{cliente.replace(' ', '')}{datetime.now().strftime('%Y%m%d%H%M%S')}.rtf"
    with open(nombre_archivo, "w") as f:
        f.write("{\\rtf1\\ansi\n")
        f.write("\\b COMPUCELL TECHNOLOGY \\b0\\line\n")
        f.write("Dirección: Av. Leopoldo Freire y Washington, local 593\\line\n")
        f.write("Ciudad: Riobamba, Chimborazo, Ecuador\\line\n")
        f.write("Teléfono: 0982443963\\line\n")
        f.write("Email: compucelltech@gmail.com\\line\n")
        f.write("Número de Factura: 001-001-00001234\\line\\line\n")
        f.write(f"Cliente: {cliente}\\line\n")
        f.write(f"Cédula/RUC: {cedula}\\line\n")
        f.write(f"Dirección: {direccion}\\line\n")
        f.write(f"Teléfono: {telefono}\\line\n")
        f.write(f"Fecha de Factura: {fecha_factura}\\line\n")
        f.write(f"Fecha de Vencimiento: {fecha_vencimiento}\\line\\line\n")
        f.write("\\b Productos \\b0\\line\n")
        f.write("Descripción\tUnidades\tPrecio Unitario\tTotal\\line\n")
        for d, u, p in productos:
            f.write(f"{d}\t{u}\t${p:.2f}\t${u*p:.2f}\\line\n")
        f.write("\\line\n")
        f.write(f"SUBTOTAL: ${subtotal:.2f}\\line\n")
        f.write(f"IVA (12%): ${iva:.2f}\\line\n")
        f.write(f"TOTAL A PAGAR: ${total:.2f}\\line\\line\n")
        f.write(f"Forma de pago: {forma_pago}\\line\n")
        f.write("Gracias por su compra. ¡Esperamos volver a verte pronto!\\line\n")
        f.write("}")
    
    return send_file(nombre_archivo, as_attachment=True)

if __name__ == '__main__':
    os.makedirs('facturas', exist_ok=True)
    app.run(debug=True)