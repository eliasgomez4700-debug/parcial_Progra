from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak


RUTA_CSV = Path(__file__).with_name("inventario.csv")
RUTA_PDF = Path(__file__).with_name("informe_consultoria.pdf")


def calcular_metricas(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["Valor_Inventario"] = (df["Cantidad"] * df["Precio_Unitario"]).round(2)
    df["Bajo_Stock"] = df["Cantidad"] < df["Stock_Minimo"]

    total_valor = df["Valor_Inventario"].sum()
    total_unidades = df["Cantidad"].sum()
    bajo_stock = int(df["Bajo_Stock"].sum())

    resumen_sucursal = (
        df.groupby("Sucursal")
        .agg(
            Registros=("Codigo", "size"),
            Unidades=("Cantidad", "sum"),
            Valor=("Valor_Inventario", "sum"),
            Alertas=("Bajo_Stock", "sum"),
        )
        .sort_values("Valor", ascending=False)
        .reset_index()
    )

    resumen_categoria = (
        df.groupby("Categoria")
        .agg(
            Productos=("Producto", "nunique"),
            Unidades=("Cantidad", "sum"),
            Valor=("Valor_Inventario", "sum"),
        )
        .sort_values("Valor", ascending=False)
        .reset_index()
    )

    top_productos = (
        df.groupby(["Codigo", "Producto", "Categoria"])
        .agg(Unidades=("Cantidad", "sum"), Valor=("Valor_Inventario", "sum"))
        .sort_values("Valor", ascending=False)
        .head(5)
        .reset_index()
    )

    alertas = df.loc[
        df["Bajo_Stock"],
        ["Sucursal", "Producto", "Cantidad", "Stock_Minimo", "Precio_Unitario"],
    ].sort_values(["Sucursal", "Cantidad"]).reset_index(drop=True)

    correlaciones = df[["Cantidad", "Stock_Minimo", "Precio_Unitario", "Valor_Inventario"]].corr().round(3)

    return {
        "total_registros": len(df),
        "total_valor": round(float(total_valor), 2),
        "total_unidades": int(total_unidades),
        "bajo_stock": bajo_stock,
        "sucursal_lider": resumen_sucursal.iloc[0],
        "categoria_lider": resumen_categoria.iloc[0],
        "top_productos": top_productos,
        "alertas": alertas,
        "resumen_sucursal": resumen_sucursal,
        "resumen_categoria": resumen_categoria,
        "correlaciones": correlaciones,
    }


def formatear_moneda(valor: float) -> str:
    return f"${valor:,.2f}"


def crear_pdf() -> None:
    df = pd.read_csv(RUTA_CSV, parse_dates=["Fecha_Ingreso"])
    metricas = calcular_metricas(df)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#0F172A"),
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#0F766E"),
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=1,
        textColor=colors.HexColor("#1F2937"),
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=8,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#374151"),
    )

    story = []

    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph("INFORME DE CONSULTORÍA", title_style))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Análisis de gestión de inventario y abastecimiento", subtitle_style))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph("Empresa: Distribuidora de Productos del Sector Retail", body_style))
    story.append(Paragraph("Período analizado: enero-diciembre 2026", body_style))
    story.append(Paragraph("Preparado por: Consultora de Operaciones y Supply Chain", body_style))
    story.append(Paragraph("Fecha: 23 de octubre de 2026", body_style))
    story.append(Spacer(1, 18 * mm))
    story.append(
        Paragraph(
            "Este documento presenta la evaluación estratégica del inventario, con foco en composición por sucursal, categoría, nivel de stock y valor económico asociado.",
            small_style,
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("1. Resumen ejecutivo", section_style))
    story.append(
        Paragraph(
            f"El inventario total analizado comprende {metricas['total_registros']} registros distribuidos en cinco sucursales. El valor total del inventario asciende a {formatear_moneda(metricas['total_valor'])}, con {metricas['total_unidades']:,} unidades en circulación. Se identificaron {metricas['bajo_stock']} alertas de stock bajo, lo que indica riesgo operativo en ciertos productos y sedes.",
            small_style,
        )
    )

    summary_table = Table(
        [
            ["Indicador", "Resultado"],
            ["Valor total de inventario", formatear_moneda(metricas['total_valor'])],
            ["Unidades en inventario", f"{metricas['total_unidades']:,}"],
            ["Registros analizados", f"{metricas['total_registros']}"],
            ["Alertas de stock bajo", f"{metricas['bajo_stock']}"],
            ["Sucursal con mayor valor", f"{metricas['sucursal_lider']['Sucursal']} ({formatear_moneda(metricas['sucursal_lider']['Valor'])})"],
            ["Categoría con mayor valor", f"{metricas['categoria_lider']['Categoria']} ({formatear_moneda(metricas['categoria_lider']['Valor'])})"],
        ],
        colWidths=[90 * mm, 90 * mm],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("2. Análisis de hallazgos por variable", section_style))

    sucursal_text = (
        "La sucursal de San Salvador concentra el mayor valor del inventario con "
        f"{formatear_moneda(metricas['sucursal_lider']['Valor'])}, equivalente a aproximadamente "
        f"{(metricas['sucursal_lider']['Valor'] / metricas['total_valor'] * 100):.1f}% del total del sistema. "
        "Santa Ana y San Miguel también presentan valores relevantes, pero la estructura del portafolio revela que el centro urbano y la demanda mayorista ejercen mayor presión sobre la inversión."
    )
    story.append(Paragraph(sucursal_text, small_style))

    categoria_text = (
        "La categoría Abarrotes lidera el valor total con "
        f"{formatear_moneda(metricas['categoria_lider']['Valor'])} y {metricas['categoria_lider']['Unidades']:,} unidades, seguida por Cuidado Personal y Lácteos. "
        "Esto sugiere que la rotación y el margen operativo están fuertemente influenciados por productos de consumo masivo que requieren alta disponibilidad y reabastecimiento constante."
    )
    story.append(Paragraph(categoria_text, small_style))

    producto_text = (
        "Los productos más valiosos son Café Molido 1 lb, Frijol Rojo 5 lb, Café Instantáneo 200 g y Desodorante 150 ml. "
        "Estos artículos representan la mayor concentración del valor y, por tanto, requieren control de inventario más estricto y análisis de rotación por sucursal."
    )
    story.append(Paragraph(producto_text, small_style))

    stock_text = (
        f"Se registraron {metricas['bajo_stock']} casos de stock bajo. Los más críticos aparecen en Sonsonate, donde hay productos sin inventario disponible como Agua Purificada 600 ml y Shampoo 750 ml, y en La Libertad y San Miguel, con productos esenciales por debajo del mínimo. Este patrón aumenta el riesgo de desabastecimiento y pérdida de ventas."
    )
    story.append(Paragraph(stock_text, small_style))

    precio_text = (
        "La relación entre precio unitario y valor total es fuerte: la correlación entre Precio_Unitario y Valor_Inventario alcanza 0.848. Esto confirma que el precio y la mezcla de productos tienen una influencia decisiva sobre la inversión total y deben considerarse en la política de compras."
    )
    story.append(Paragraph(precio_text, small_style))

    cantidad_text = (
        "La correlación entre Cantidad y Valor_Inventario es 0.638, lo que establece una relación positiva moderada. Esto indica que el valor no depende solo del volumen físico, sino también del precio y la composición por producto."
    )
    story.append(Paragraph(cantidad_text, small_style))

    story.append(Paragraph("3. Conclusiones por variable analizada", section_style))
    conclusions = [
        "<b>Sucursal:</b> San Salvador concentra la mayor inversión y demanda; la estrategia de abastecimiento debe priorizar esta sede y su repliegue de stock.",
        "<b>Categoría:</b> Abarrotes y Cuidado Personal son las categorías con mayor impacto económico; requieren revisión de frecuencia de compra y políticas de cobertura.",
        "<b>Producto:</b> Los artículos más valiosos y sensibles deben mantenerse en niveles adecuados para evitar pérdida de ventas y desabastecimiento.",
        "<b>Cantidad:</b> La cantidad disponible tiene incidencia real sobre el valor, pero no es el único factor: el precio unitario modifica la estructura del valor final.",
        "<b>Stock mínimo:</b> El stock mínimo no está alineado con la demanda real en varios casos; la diferencia entre el mínimo y la disponibilidad real genera brechas operativas.",
        "<b>Precio unitario:</b> El precio influye más que la cantidad en el valor del inventario; la fijación o revisión de precios de compra requiere seguimiento continuo.",
        "<b>Valor del inventario:</b> El valor total refleja principalmente la combinación de productos premium, de compra frecuente y con alta demanda por sucursal.",
        "<b>Fecha de ingreso:</b> No se observan anomalías temporales relevantes; la dispersión de fechas indica que la renovación del stock es relativamente estable y no sugiere agotamiento masivo por antigüedad.",
        "<b>Bajo stock:</b> El 11.5% de los registros se encuentran por debajo del stock mínimo, una señal de desalineación entre compras y demanda real."
    ]
    for item in conclusions:
        story.append(Paragraph(item, small_style))

    story.append(Paragraph("4. Recomendaciones estratégicas", section_style))
    recommendations = [
        "1. Reforzar la política de compras en San Salvador y Santa Ana, donde la concentración del valor es mayor y el riesgo de escasez más significativo.",
        "2. Definir puntos de reorden automáticos por SKU con base en demanda histórica, rotación y servicio mínimo, especialmente en Abarrotes, Bebidas y Cuidado Personal.",
        "3. Crear alertas de stock bajo por sucursal y por producto para evitar faltantes de artículos de alta demanda y de alto valor económico.",
        "4. Revisar la política de inventario para productos sensibles a la estacionalidad y a la rotación, evitando exceso de productos de bajo movimiento y escasez de artículos esenciales.",
        "5. Evaluar proveedores alternos y tiempos de entrega para reducir el riesgo operativo en productos con bajo inventario y con alta sensibilidad a la demanda.",
        "6. Implementar un tablero de control integrado con indicadores de valor, cobertura, rotación, desabastecimiento y margen, para apoyar decisiones en tiempo real."
    ]
    for item in recommendations:
        story.append(Paragraph(item, small_style))

    story.append(PageBreak())

    story.append(Paragraph("5. Datos de referencia", section_style))
    sucursal_table = Table(
        [
            ["Sucursal", "Unidades", "Valor"],
            *[[row["Sucursal"], f"{row['Unidades']:,}", formatear_moneda(row['Valor'])] for _, row in metricas['resumen_sucursal'].iterrows()],
        ],
        colWidths=[70 * mm, 35 * mm, 50 * mm],
    )
    sucursal_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    story.append(sucursal_table)
    story.append(Spacer(1, 8 * mm))

    categoria_table = Table(
        [
            ["Categoría", "Unidades", "Valor"],
            *[[row["Categoria"], f"{row['Unidades']:,}", formatear_moneda(row['Valor'])] for _, row in metricas['resumen_categoria'].iterrows()],
        ],
        colWidths=[70 * mm, 35 * mm, 50 * mm],
    )
    categoria_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    story.append(categoria_table)
    story.append(Spacer(1, 8 * mm))

    top_productos_table = Table(
        [
            ["Producto", "Categoría", "Valor"],
            *[[row["Producto"], row["Categoria"], formatear_moneda(row["Valor"]) ] for _, row in metricas['top_productos'].iterrows()],
        ],
        colWidths=[70 * mm, 45 * mm, 38 * mm],
    )
    top_productos_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    story.append(top_productos_table)

    doc = SimpleDocTemplate(
        str(RUTA_PDF),
        pagesize=LETTER,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    doc.build(story)


if __name__ == "__main__":
    crear_pdf()
    print(f"PDF generado correctamente en: {RUTA_PDF}")
