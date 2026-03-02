import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import calendar
from datetime import datetime

def generar_pdf(mes, anio, personal, feriados_lista):
    filename = f"Rol_Guardia_{mes}_{anio}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=30, leftMargin=30,
                            topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para negritas y centrado
    estilo_negrita = ParagraphStyle(
        'NegritaCentrada',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=1, # 1 es centrado
        spaceAfter=10
    )

    # 1. Título principal [cite: 1]
    elements.append(Paragraph("Rol de guardias", styles['Title']))
    
    # 2. Departamento y Residencia en NEGRITA [cite: 2]
    elements.append(Paragraph("<b>Departamento de seguridad privada, Residencia Puerto Escondido</b>", estilo_negrita))
    
    # 3. Mes y Año en NEGRITA [cite: 3]
    nombre_mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][mes-1]
    elements.append(Paragraph(f"<b>{nombre_mes} {anio}</b>", estilo_negrita))
    
    elements.append(Spacer(1, 10))

    # --- TABLA 1: CALENDARIO (Más grande) --- 
    dias_semana = ["Domingo", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
    cal = calendar.Calendar(firstweekday=6)
    mes_dias = cal.monthdayscalendar(anio, mes)
    
    data_cal = [dias_semana]
    estilos_celdas = [
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke)
    ]

    for fila_idx, semana in enumerate(mes_dias):
        nueva_fila = []
        for col_idx, dia in enumerate(semana):
            es_feriado = dia in feriados_lista
            es_domingo = (col_idx == 0 and dia != 0)

            if dia == 0:
                nueva_fila.append("")
            elif es_domingo or es_feriado:
                # Opción muy notable: Número con un asterisco o punto grande y negrita
                nueva_fila.append(f"• {dia} •") 
                # Pintamos el fondo de la celda de los domingos
                estilos_celdas.append(('BACKGROUND', (col_idx, fila_idx + 1), (col_idx, fila_idx + 1), colors.lightgrey))
                estilos_celdas.append(('FONTNAME', (col_idx, fila_idx + 1), (col_idx, fila_idx + 1), 'Helvetica-Bold'))
            else:
                nueva_fila.append(str(dia))
        data_cal.append(nueva_fila)
    
    # Ajustamos colWidths (ancho) y rowHeights (alto) para que se vea espacioso
    t1 = Table(data_cal, colWidths=75, rowHeights=30) 
    t1.setStyle(TableStyle(estilos_celdas))
    elements.append(t1)
    elements.append(Spacer(1, 15))

    # --- TABLA 2: TURNOS (Celdas grandes como el PDF original) --- 
    num_dias = calendar.monthrange(anio, mes)[1]
    encabezado_personal = [p.strip() for p in personal]
    filas_turnos = [encabezado_personal]

    estilos_t2 = [
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]
    
    # Lista de todos los números de días del mes
    dias_lista = []
    for dia in range(1, num_dias + 1):
        # Averiguamos qué día de la semana es (0=Lunes, 6=Domingo)
        dia_semana = calendar.weekday(anio, mes, dia)
        es_feriado = dia in feriados_lista
        
        if dia_semana == 6 or es_feriado:
            dias_lista.append(f"• {dia:02d} •")
        else:
            dias_lista.append(f"{dia:02d}")

    # Agrupar los días en filas de 3 (para Alejandro, Emelin, Ronald)
    for i in range(0, len(dias_lista), 3):
        fila = dias_lista[i:i+3]
        
        # Aplicar color de fondo gris a la celda si contiene un domingo
        for col_idx, contenido in enumerate(fila):
            if "•" in contenido:
                fila_actual = (i // 3) + 1 # +1 por el encabezado
                estilos_t2.append(('BACKGROUND', (col_idx, fila_actual), (col_idx, fila_actual), colors.lightgrey))
                estilos_t2.append(('FONTNAME', (col_idx, fila_actual), (col_idx, fila_actual), 'Helvetica-Bold'))
        
        while len(fila) < 3: fila.append("")
        filas_turnos.append(fila)

    # Ajustamos tamaño de celdas para la tabla de guardias
    t2 = Table(filas_turnos, colWidths=100, rowHeights=22)
    t2.setStyle(TableStyle(estilos_t2))
    elements.append(t2)

    # Nota al pie [cite: 5]
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<i>Nota: Los dias marcados con un punto son dias feriados y domingos trabajados</i>", styles['Italic']))

    doc.build(elements)
    return filename

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Generador Puerto Escondido")
st.title("Configuración del Rol de Guardia")

with st.sidebar:
    st.header("Opciones")
    mes_sel = st.selectbox("Mes", range(1, 13), index=2) # Marzo por defecto
    anio_sel = st.number_input("Año", value=2026)
    nombres_input = st.text_area("Personal (separado por comas)", "Alejandro, Emelin, Ronald")
    feriados_input = st.text_input("Días feriados (ej: 1, 15, 20)", "")

lista_feriados = []
if feriados_input:
    lista_feriados = [int(x.strip()) for x in feriados_input.split(",") if x.strip().isdigit()]

if st.button("Generar PDF con Formato"):
    lista_n = nombres_input.split(",")
    archivo = generar_pdf(mes_sel, anio_sel, lista_n, lista_feriados)
    with open(archivo, "rb") as f:
        st.download_button("📥 Descargar PDF listo para imprimir", f, file_name=archivo)