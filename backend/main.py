from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = FastAPI()

# Habilitar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto si quieres restringir orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "data.json"

# Ruta para recibir los datos del ESP32
@app.post("/data")
async def recibir_datos(request: Request):
    try:
        datos = await request.json()

        # Guardar los datos en un archivo JSON
        with open(DATA_FILE, "w") as f:
            json.dump(datos, f)

        print("✅ Datos recibidos:", datos)
        return {"mensaje": "Datos recibidos correctamente"}
    
    except Exception as e:
        print("❌ Error al recibir datos:", e)
        return {"mensaje": "Error al recibir datos"}

# Ruta para enviar los datos al frontend
@app.get("/data")
async def enviar_datos():
    if not os.path.exists(DATA_FILE):
        return {"temperatura": 0, "humedad_ambiente": 0, "humedad_suelo": 0}

    with open(DATA_FILE, "r") as f:
        datos = json.load(f)

    return datos

# Ruta para generar el archivo Excel
@app.get("/download/excel")
async def download_excel():
    # Crear un libro de trabajo y hoja de trabajo
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos del Sensor"

    # Encabezados
    ws.append(["Temperatura", "Humedad Ambiente", "Humedad Suelo"])

    # Leer datos
    with open(DATA_FILE, "r") as f:
        datos = json.load(f)

    # Agregar datos a la hoja de trabajo
    ws.append([datos["temperatura"], datos["humedad_ambiente"], datos["humedad_suelo"]])

    # Guardar el archivo Excel
    excel_file = "data.xlsx"
    wb.save(excel_file)

    return FileResponse(excel_file, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="data.xlsx")

# Ruta para generar el archivo PDF
@app.get("/download/pdf")
async def download_pdf():
    pdf_file = "data.pdf"

    # Crear un canvas para el archivo PDF
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.drawString(100, 750, "Datos del Sensor")

    # Leer datos
    with open(DATA_FILE, "r") as f:
        datos = json.load(f)

    # Escribir los datos en el PDF
    c.drawString(100, 730, f"Temperatura: {datos['temperatura']} °C")
    c.drawString(100, 710, f"Humedad Ambiente: {datos['humedad_ambiente']} %")
    c.drawString(100, 690, f"Humedad Suelo: {datos['humedad_suelo']}")

    # Guardar el archivo PDF
    c.save()

    return FileResponse(pdf_file, media_type='application/pdf', filename="data.pdf")
