from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_pdf_comprobante(pedido):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'TituloTienda', parent=styles['Title'], textColor=colors.HexColor('#1e40af')
    )
    estilo_normal = styles['Normal']

    elementos = []

    comprobante = pedido.pago.comprobante

    elementos.append(Paragraph("TIENDA MASS", estilo_titulo))
    elementos.append(Paragraph(
        f"{comprobante.get_tipo_display()} Electrónica {comprobante.serie}-{comprobante.numero}",
        styles['Heading2']
    ))
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph(f"<b>Pedido:</b> {pedido.numero_orden}", estilo_normal))
    elementos.append(Paragraph(f"<b>Fecha de emisión:</b> {comprobante.fecha_emision.strftime('%d/%m/%Y %H:%M')}", estilo_normal))
    elementos.append(Paragraph(f"<b>Cliente:</b> {pedido.cliente.username}", estilo_normal))
    elementos.append(Paragraph(f"<b>Dirección de entrega:</b> {pedido.direccion_entrega}", estilo_normal))
    elementos.append(Spacer(1, 16))

    # Tabla de productos
    data = [["Producto", "Cantidad", "Precio unit.", "Subtotal"]]
    for detalle in pedido.detalles.all():
        data.append([
            detalle.producto.nombre,
            str(detalle.cantidad),
            f"S/ {detalle.precio_unitario}",
            f"S/ {detalle.subtotal}",
        ])

    tabla = Table(data, colWidths=[7*cm, 3*cm, 3.5*cm, 3.5*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 16))

    # Totales
    data_totales = [
        ["Subtotal", f"S/ {comprobante.subtotal}"],
        ["IGV (18%)", f"S/ {comprobante.igv}"],
        ["Envío", f"S/ {pedido.costo_envio}"],
        ["TOTAL", f"S/ {comprobante.total}"],
    ]
    tabla_totales = Table(data_totales, colWidths=[13.5*cm, 3.5*cm])
    tabla_totales.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e40af')),
    ]))
    elementos.append(tabla_totales)
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph(f"<b>Método de pago:</b> {pedido.pago.get_metodo_display()}", estilo_normal))
    elementos.append(Paragraph(f"<b>Referencia de transacción:</b> {pedido.pago.referencia_transaccion}", estilo_normal))
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph(
        "<i>Este es un comprobante generado digitalmente por Tienda Mass. "
        "Documento de uso interno / académico, sin validez tributaria SUNAT.</i>",
        ParagraphStyle('Nota', parent=estilo_normal, fontSize=8, textColor=colors.grey)
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer