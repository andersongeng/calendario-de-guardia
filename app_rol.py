import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import calendar
from datetime import datetime
from PIL import Image

icon = Image.open("logo.png")

# --- FUNCIÓN GENERADORA DEL PDF ---
def generar_pdf(mes, anio, personal, feriados_lista):
    filename = f"Rol_Guardia_{mes}_{anio}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, 
                            rightMargin=30, leftMargin=30, 
                            topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    
    estilo_negrita = ParagraphStyle(
        'NegritaCentrada', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=12, alignment=1, spaceAfter=8
    )

    # [cite_start]Encabezados basados en la plantilla [cite: 1, 2, 3]
    elements.append(Paragraph("Rol de guardias", styles['Title']))
    elements.append(Paragraph("<b>Departamento de seguridad privada, Residencia Puerto Escondido</b>", estilo_negrita))
    
    meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    nombre_mes = meses_es[mes-1]
    elements.append(Paragraph(f"<b>{nombre_mes} {anio}</b>", estilo_negrita))
    elements.append(Spacer(1, 10))

    # --- TABLA 1: CALENDARIO ---
    dias_semana = ["Domingo", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
    cal = calendar.Calendar(firstweekday=6)
    mes_dias = cal.monthdayscalendar(anio, mes)
    
    data_cal = [dias_semana]
    estilos_t1 = [
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
                nueva_fila.append(f"• {dia} •")
                estilos_t1.append(('BACKGROUND', (col_idx, fila_idx + 1), (col_idx, fila_idx + 1), colors.lightgrey))
                estilos_t1.append(('FONTNAME', (col_idx, fila_idx + 1), (col_idx, fila_idx + 1), 'Helvetica-Bold'))
            else:
                nueva_fila.append(str(dia))
        data_cal.append(nueva_fila)

    t1 = Table(data_cal, colWidths=75, rowHeights=30)
    t1.setStyle(TableStyle(estilos_t1))
    elements.append(t1)
    elements.append(Spacer(1, 15))

    # --- TABLA 2: TURNOS (PERSONAL) ---
    num_dias = calendar.monthrange(anio, mes)[1]
    filas_turnos = [[p.strip() for p in personal]]
    estilos_t2 = [
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]

    dias_lista = []
    for dia in range(1, num_dias + 1):
        dia_semana = calendar.weekday(anio, mes, dia)
        es_feriado = dia in feriados_lista
        if dia_semana == 6 or es_feriado:
            dias_lista.append(f"• {dia:02d} •")
        else:
            dias_lista.append(f"{dia:02d}")

    for i in range(0, len(dias_lista), 3):
        fila = dias_lista[i:i+3]
        for col_idx, contenido in enumerate(fila):
            if "•" in contenido:
                fila_actual = (i // 3) + 1
                estilos_t2.append(('BACKGROUND', (col_idx, fila_actual), (col_idx, fila_actual), colors.lightgrey))
                estilos_t2.append(('FONTNAME', (col_idx, fila_actual), (col_idx, fila_actual), 'Helvetica-Bold'))
        while len(fila) < 3: fila.append("")
        filas_turnos.append(fila)

    t2 = Table(filas_turnos, colWidths=100, rowHeights=20) # Altura reducida para evitar saltos de página
    t2.setStyle(TableStyle(estilos_t2))
    elements.append(t2)

    # [cite_start]Nota al pie [cite: 5]
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<i>Nota: Los dias marcados con un punto son dias feriados y domingos trabajados</i>", styles['Italic']))

    doc.build(elements)
    return filename

# --- INTERFAZ PRINCIPAL DE LA APP (Móvil-Friendly) ---
st.set_page_config(page_title="Rol Puerto Escondido", page_icon=icon)

st.title("🛡️ Sistema de Seguridad")
st.markdown("### Configuración del Rol de Guardia")
st.info("Completa los datos aquí abajo para generar el nuevo PDF.")

# Usamos columnas para que en PC salgan juntas y en Móvil una tras otra
col1, col2 = st.columns(2)

with col1:
    mes_sel = st.selectbox("📅 Mes del Rol", range(1, 13), index=datetime.now().month - 1)
    anio_sel = st.number_input("📆 Año", value=2026)

with col2:
    nombres_in = st.text_area("👥 Nombres del Personal (separados por coma)", "Alejandro, Emelin, Ronald")
    feriados_in = st.text_input("🚩 Días Feriados (Ejemplo: 1, 25)", "")

# Procesar feriados
lista_feriados = []
if feriados_in:
    try:
        lista_feriados = [int(x.strip()) for x in feriados_in.split(",") if x.strip().isdigit()]
    except:
        st.warning("Revisa el formato de los feriados (solo números y comas).")

st.markdown("---")

# Botón grande y visible para móviles
if st.button("📄 GENERAR PDF CON FORMATO", use_container_width=True, type="primary"):
    with st.spinner("Creando documento..."):
        lista_n = [n.strip() for n in nombres_in.split(",")]
        archivo = generar_pdf(mes_sel, anio_sel, lista_n, lista_feriados)
        
        with open(archivo, "rb") as f:
            st.success("✅ ¡PDF generado con éxito!")
            st.download_button(
                label="📥 DESCARGAR ROL AHORA",
                data=f,
                file_name=archivo,
                mime="application/pdf",
                use_container_width=True
            )