from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

def generar_reporte_mermas(mermas, mes, año):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          rightMargin=30, leftMargin=30, 
                          topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    elementos = []
    
    # Título
    elementos.append(Paragraph(f"Reporte de Mermas - {mes}/{año}", styles['Title']))
    elementos.append(Paragraph("Restaurante Riquísimo", styles['Normal']))
    elementos.append(Paragraph(" ", styles['Normal']))
    
    # Datos de las mermas
    data = [['Producto', 'Cantidad', 'Unidad', 'Motivo', 'Usuario', 'Fecha']]
    
    for merma in mermas:
        data.append([
            merma.producto.nombre,
            str(merma.cantidad),
            merma.producto.get_unidad_display(),
            merma.motivo,
            merma.usuario.username if merma.usuario else "N/A",
            merma.fecha_registro.strftime("%d/%m/%Y %H:%M")
        ])
    
    # Tabla
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#732F48')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F6E0E3')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elementos.append(t)
    
    # Total
    total = sum(m.cantidad for m in mermas)
    elementos.append(Paragraph(f"<br/><b>Total de productos perdidos: {total}</b>", styles['Normal']))
    
    # Fecha generación
    elementos.append(Paragraph(f"<br/>Reporte generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    
    doc.build(elementos)
    buffer.seek(0)
    return buffer