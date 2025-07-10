import os
import webbrowser
import smtplib
from email.utils import make_msgid
from email.message import EmailMessage
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
    correo = request.form['correo']
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
        f.write(f"Nombre: {cliente}\\line\n")
        f.write(f"C\\'e9dula/RUC: {cedula}\\line\n")
        f.write(f"Direcci\\'f3n: {direccion}\\line\n")
        f.write(f"Tel\\'e9fono: {telefono}\\line\n")
        f.write(f"Correo: {correo}\\line\n")
        f.write(f"Fecha de Factura: {fecha_factura}\\line\n")
        f.write(f"Fecha de Vencimiento: {fecha_vencimiento}\\line\n")
        f.write("\\line\n")

        f.write("\\b DETALLE DE PRODUCTOS\\b0\\line\n")
        f.write("Descripci\\'f3n\\tab Unidades\\tab Precio Unitario\\tab Total\\line\n")
        f.write("\\line\n")
        for d, u, p in productos:
            total_linea = u * p
            f.write(f"{d}\\tab {u}\\tab ${p:.2f}\\tab ${total_linea:.2f}\\line\n")
        f.write("\\line\n")

        f.write(f"\\b Subtotal:\\b0\\tab ${subtotal:.2f}\\line\n")
        f.write(f"\\b IVA (12%):\\b0\\tab ${iva:.2f}\\line\n")
        f.write(f"\\b Total a pagar:\\b0\\tab ${total:.2f}\\line\n")
        f.write(f"\\b Forma de pago:\\b0\\tab {forma_pago}\\line\n")
        f.write("\\line\n")

        f.write("Gracias por su compra. \\u161?Esperamos volver a verte pronto!\\line\n")
        f.write("}")

    def enviar_factura_por_correo(destinatario, archivo_adjunto):
        remitente = "compucelltechnologic@gmail.com"
        contraseña = "fmlq ihxs tkvx cdyk"

        mensaje = EmailMessage()
        mensaje['Subject'] = "Factura electrónica - Compucell Technology"
        mensaje['From'] = remitente
        mensaje['To'] = destinatario

        firma_cid = make_msgid(domain='compucell.com')[1:-1]

        cuerpo_html = f"""
        <html>
        <body>
            <p>Estimado/a <strong>{cliente}</strong>,</p>
            <p>Adjunto encontrará su factura electrónica generada por <strong>Compucell Technology</strong>.</p>
            <p style='color: #0ea5e9;'><strong>Gracias por su compra. Estamos para servirle.</strong></p>

            <br><br>
            <p style='font-size: 13px; font-family: Arial, sans-serif;'>
              <img src='cid:{firma_cid}' width='160' style='margin-bottom: 10px;'><br>
              <strong>Compucell Technology</strong><br>
              <a href='mailto:compucelltechnologic@gmail.com'>compucelltechnologic@gmail.com</a><br>
              +593 994138746<br>
              Av. Leopoldo Freire y Washington, local 593, Riobamba, Chimborazo, Ecuador<br><br>
              <strong style='color:#0ea5e9;'>¡Gracias por comprar en Compucell Technology!</strong><br>
              <a href='https://forms.gle/R65kfigLb3kJNFcaA' target='_blank'>👉 Califica tu experiencia con nosotros</a>
            </p>
        </body>
        </html>
        """

        mensaje.set_content("Adjunto su factura. Gracias por su compra.")
        mensaje.add_alternative(cuerpo_html, subtype='html')

        with open(archivo_adjunto, 'rb') as f:
            contenido = f.read()
            mensaje.add_attachment(contenido, maintype='application', subtype='octet-stream', filename=os.path.basename(archivo_adjunto))

        with open("firma.png", 'rb') as img:
            mensaje.get_payload()[1].add_related(img.read(), maintype='image', subtype='png', cid=f"<{firma_cid}>")

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(remitente, contraseña)
                smtp.send_message(mensaje)
            print("✅ Correo con firma y factura enviado.")
        except Exception as e:
            print(f"❌ Error al enviar el correo: {e}")

    enviar_factura_por_correo(correo, nombre_archivo)

    return send_file(nombre_archivo, as_attachment=True)

if __name__ == '__main__':
    webbrowser.open("http://localhost:5000")
    app.run(debug=True, use_reloader=False)
