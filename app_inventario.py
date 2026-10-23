from __future__ import annotations

import io
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Qt5Agg")

import pandas as pd
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

RUTA_INVENTARIO = Path(__file__).with_name("inventario.csv")
SUCURSALES = ["San Salvador", "Santa Ana", "San Miguel", "La Libertad", "Sonsonate"]
COLORES_SUCURSAL = {
    "San Salvador": "#0F766E",
    "Santa Ana": "#D97706",
    "San Miguel": "#2563EB",
    "La Libertad": "#7C3AED",
    "Sonsonate": "#DC2626",
}
COLORES_CATEGORIA = {
    "Abarrotes": "#0F766E",
    "Bebidas": "#2563EB",
    "Cuidado Personal": "#DB2777",
    "Lácteos": "#7C3AED",
    "Limpieza": "#0891B2",
}
COLOR_ACCENTO = "#0F766E"
COLOR_GRIS = "#CBD5E1"

COLUMNAS_TABLA = [
    "Código",
    "Producto",
    "Categoría",
    "Sucursal",
    "Cantidad",
    "Stock mínimo",
    "Precio unitario",
    "Valor total",
    "Estado",
    "Fecha ingreso",
]

matplotlib.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": "#CBD5E1",
        "axes.labelcolor": "#475569",
        "axes.titlecolor": "#0F172A",
        "xtick.color": "#475569",
        "ytick.color": "#475569",
        "text.color": "#0F172A",
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
    }
)

ESTILOS = """
QWidget {
    font-family: "DejaVu Sans";
    color: #0F172A;
}
QWidget#fondo {
    background-color: #F1F5F9;
}
QFrame#cabecera {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0F172A, stop:1 #115E59);
    border-radius: 18px;
}
QLabel#tituloApp {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 700;
}
QLabel#subtituloApp {
    color: #99F6E4;
    font-size: 11px;
}
QLabel#marcaApp {
    color: #0F172A;
    background-color: #FBBF24;
    border-radius: 11px;
    font-size: 17px;
    font-weight: 700;
}
QPushButton#botonActualizar {
    background-color: #FFFFFF;
    color: #0F766E;
    border: none;
    border-radius: 9px;
    padding: 9px 16px;
    font-weight: 700;
}
QPushButton#botonActualizar:hover {
    background-color: #CCFBF1;
}
QPushButton#botonLimpiar {
    background-color: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 12px;
    font-weight: 600;
}
QPushButton#botonLimpiar:hover {
    border-color: #0F766E;
    color: #0F766E;
}
QFrame#tarjetaKpi {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}
QLabel#tituloKpi {
    color: #64748B;
    font-size: 11px;
    font-weight: 600;
}
QLabel#valorKpi {
    color: #0F172A;
    font-size: 22px;
    font-weight: 700;
}
QLabel#detalleKpi {
    color: #94A3B8;
    font-size: 10px;
}
QTabWidget::pane {
    border: none;
    background-color: #FFFFFF;
    border-radius: 14px;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #64748B;
    padding: 10px 18px;
    margin-right: 4px;
    font-weight: 600;
    border: none;
}
QTabBar::tab:selected {
    color: #0F766E;
    border-bottom: 3px solid #0F766E;
}
QTabBar::tab:hover:!selected {
    color: #0F172A;
}
QWidget#pagina {
    background-color: #FFFFFF;
    border-radius: 14px;
}
QFrame#panelControles {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
}
QLabel#etiquetaFiltro {
    color: #475569;
    font-size: 11px;
    font-weight: 600;
}
QLabel#resultado {
    color: #64748B;
    font-size: 11px;
}
QLabel#insight {
    background-color: #F0FDFA;
    border: 1px solid #99F6E4;
    border-radius: 8px;
    padding: 8px 12px;
    color: #115E59;
    font-size: 11px;
}
QLabel#nota {
    color: #64748B;
    font-size: 11px;
}
QComboBox, QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 22px;
    color: #0F172A;
}
QComboBox:hover, QLineEdit:hover {
    border-color: #94A3B8;
}
QComboBox:focus, QLineEdit:focus {
    border: 1px solid #0F766E;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
    selection-background-color: #CCFBF1;
    selection-color: #0F172A;
    alternate-background-color: #F8FAFC;
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    padding: 8px 6px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    font-weight: 700;
}
QTableCornerButton::section {
    background-color: #F8FAFC;
    border: none;
}
QPlainTextEdit#reporte {
    background-color: #F8FAFC;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px;
    selection-background-color: #99F6E4;
}
QStatusBar {
    background-color: #F1F5F9;
    color: #64748B;
}
QToolBar {
    background-color: #FFFFFF;
    border: none;
    spacing: 4px;
}
"""


def cargar_datos(ruta: Path | str = RUTA_INVENTARIO) -> pd.DataFrame:
    datos = pd.read_csv(ruta, parse_dates=["Fecha_Ingreso"])
    datos["Valor_Inventario"] = (
        datos["Cantidad"] * datos["Precio_Unitario"]
    ).round(2)
    datos["Bajo_Stock"] = datos["Cantidad"] < datos["Stock_Minimo"]
    return datos


def formato_moneda(valor: float) -> str:
    return f"${valor:,.2f}"


def formato_entero(valor: float) -> str:
    return f"{valor:,.0f}"


class ItemNumero(QTableWidgetItem):
    def __init__(self, valor: float, texto: str | None = None):
        super().__init__(texto if texto is not None else formato_entero(valor))
        self._valor = float(valor)
        self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def __lt__(self, otro: QTableWidgetItem) -> bool:
        if isinstance(otro, ItemNumero):
            return self._valor < otro._valor
        return super().__lt__(otro)


class ItemFecha(QTableWidgetItem):
    def __init__(self, fecha: pd.Timestamp):
        super().__init__(fecha.strftime("%d/%m/%Y"))
        self._fecha = fecha
        self.setTextAlignment(Qt.AlignCenter)

    def __lt__(self, otro: QTableWidgetItem) -> bool:
        if isinstance(otro, ItemFecha):
            return self._fecha < otro._fecha
        return super().__lt__(otro)


class TarjetaKPI(QFrame):
    def __init__(self, titulo: str, color: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("tarjetaKpi")
        self.setMinimumHeight(104)

        fila = QHBoxLayout(self)
        fila.setContentsMargins(14, 12, 16, 12)
        fila.setSpacing(12)

        franja = QFrame()
        franja.setFixedWidth(5)
        franja.setStyleSheet(
            f"background-color: {color}; border-radius: 2px;"
        )

        contenido = QVBoxLayout()
        contenido.setSpacing(3)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setObjectName("tituloKpi")
        self.lbl_valor = QLabel("0")
        self.lbl_valor.setObjectName("valorKpi")
        self.lbl_detalle = QLabel("")
        self.lbl_detalle.setObjectName("detalleKpi")

        contenido.addWidget(self.lbl_titulo)
        contenido.addWidget(self.lbl_valor)
        contenido.addWidget(self.lbl_detalle)

        fila.addWidget(franja)
        fila.addLayout(contenido, 1)

    def actualizar(self, valor: str, detalle: str) -> None:
        self.lbl_valor.setText(valor)
        self.lbl_detalle.setText(detalle)


class VentanaInventario(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ruta_datos = RUTA_INVENTARIO
        self.datos = cargar_datos(self.ruta_datos)
        self.setWindowTitle("Inventario Comercial | Cinco sucursales")
        self.resize(1300, 840)
        self.setMinimumSize(1080, 700)
        self.setStyleSheet(ESTILOS)
        self._construir_interfaz()
        self._cargar_filtros()
        self._actualizar_todo()
        self.statusBar().showMessage(
            f"Inventario cargado: {len(self.datos):,} registros desde "
            f"{self.ruta_datos.name}"
        )

    def _construir_interfaz(self) -> None:
        central = QWidget()
        central.setObjectName("fondo")
        principal = QVBoxLayout(central)
        principal.setContentsMargins(22, 18, 22, 14)
        principal.setSpacing(14)

        principal.addWidget(self._crear_cabecera())
        principal.addLayout(self._crear_tarjetas())

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._crear_tab_inventario(), "Inventario")
        self.tabs.addTab(self._crear_tab_graficos(), "Panel gráfico")
        self.tabs.addTab(self._crear_tab_analisis(), "Análisis con Pandas")
        principal.addWidget(self.tabs, 1)

        self.setCentralWidget(central)

    def _crear_cabecera(self) -> QFrame:
        cabecera = QFrame()
        cabecera.setObjectName("cabecera")
        fila = QHBoxLayout(cabecera)
        fila.setContentsMargins(22, 17, 20, 17)
        fila.setSpacing(14)

        marca = QLabel("IC")
        marca.setObjectName("marcaApp")
        marca.setAlignment(Qt.AlignCenter)
        marca.setFixedSize(50, 50)

        textos = QVBoxLayout()
        textos.setSpacing(2)
        titulo = QLabel("Inventario Comercial")
        titulo.setObjectName("tituloApp")
        subtitulo = QLabel(
            "Distribuidora salvadoreña  |  5 sucursales  |  Inventario 2026"
        )
        subtitulo.setObjectName("subtituloApp")
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        self.btn_actualizar = QPushButton("Actualizar datos")
        self.btn_actualizar.setObjectName("botonActualizar")
        self.btn_actualizar.setCursor(Qt.PointingHandCursor)
        self.btn_actualizar.clicked.connect(self._recargar_datos)

        fila.addWidget(marca)
        fila.addLayout(textos)
        fila.addStretch(1)
        fila.addWidget(self.btn_actualizar)
        return cabecera

    def _crear_tarjetas(self) -> QHBoxLayout:
        fila = QHBoxLayout()
        fila.setSpacing(12)
        self.tarjetas = {
            "valor": TarjetaKPI("VALOR DEL INVENTARIO", COLOR_ACCENTO),
            "unidades": TarjetaKPI("UNIDADES DISPONIBLES", "#2563EB"),
            "productos": TarjetaKPI("PRODUCTOS EN CATÁLOGO", "#7C3AED"),
            "alertas": TarjetaKPI("ALERTAS DE STOCK", "#DC2626"),
        }
        for tarjeta in self.tarjetas.values():
            fila.addWidget(tarjeta, 1)
        return fila

    def _crear_tab_inventario(self) -> QWidget:
        pagina = QWidget()
        pagina.setObjectName("pagina")
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(18, 18, 18, 16)
        layout.setSpacing(12)

        panel = QFrame()
        panel.setObjectName("panelControles")
        filtros = QHBoxLayout(panel)
        filtros.setContentsMargins(12, 10, 12, 10)
        filtros.setSpacing(9)

        etiqueta_sucursal = QLabel("Sucursal")
        etiqueta_sucursal.setObjectName("etiquetaFiltro")
        self.combo_sucursal_tabla = QComboBox()
        self.combo_sucursal_tabla.setMinimumWidth(175)

        etiqueta_categoria = QLabel("Categoría")
        etiqueta_categoria.setObjectName("etiquetaFiltro")
        self.combo_categoria_tabla = QComboBox()
        self.combo_categoria_tabla.setMinimumWidth(155)

        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("Buscar producto o código...")
        self.busqueda.setClearButtonEnabled(True)
        self.busqueda.setMinimumWidth(250)

        self.btn_limpiar = QPushButton("Limpiar filtros")
        self.btn_limpiar.setObjectName("botonLimpiar")
        self.btn_limpiar.setCursor(Qt.PointingHandCursor)

        filtros.addWidget(etiqueta_sucursal)
        filtros.addWidget(self.combo_sucursal_tabla)
        filtros.addSpacing(6)
        filtros.addWidget(etiqueta_categoria)
        filtros.addWidget(self.combo_categoria_tabla)
        filtros.addSpacing(6)
        filtros.addWidget(self.busqueda, 1)
        filtros.addWidget(self.btn_limpiar)

        self.tabla = QTableWidget(0, len(COLUMNAS_TABLA))
        self.tabla.setHorizontalHeaderLabels(COLUMNAS_TABLA)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.setWordWrap(False)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(33)
        self.tabla.horizontalHeader().setHighlightSections(False)
        self.tabla.horizontalHeader().setDefaultSectionSize(100)
        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        anchos = {
            0: 72,
            2: 120,
            3: 112,
            4: 84,
            5: 102,
            6: 108,
            7: 110,
            8: 102,
            9: 108,
        }
        for columna, ancho in anchos.items():
            self.tabla.setColumnWidth(columna, ancho)

        pie = QHBoxLayout()
        self.lbl_resultados = QLabel("")
        self.lbl_resultados.setObjectName("resultado")
        pie.addWidget(self.lbl_resultados)
        pie.addStretch(1)

        layout.addWidget(panel)
        layout.addWidget(self.tabla, 1)
        layout.addLayout(pie)

        self.combo_sucursal_tabla.currentIndexChanged.connect(
            self._actualizar_tabla
        )
        self.combo_categoria_tabla.currentIndexChanged.connect(
            self._actualizar_tabla
        )
        self.busqueda.textChanged.connect(self._actualizar_tabla)
        self.btn_limpiar.clicked.connect(self._limpiar_filtros)
        return pagina

    def _crear_tab_graficos(self) -> QWidget:
        pagina = QWidget()
        pagina.setObjectName("pagina")
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(10)

        panel = QFrame()
        panel.setObjectName("panelControles")
        controles = QHBoxLayout(panel)
        controles.setContentsMargins(12, 10, 12, 10)
        controles.setSpacing(9)

        etiqueta_sucursal = QLabel("Sucursal")
        etiqueta_sucursal.setObjectName("etiquetaFiltro")
        self.combo_sucursal_grafico = QComboBox()
        self.combo_sucursal_grafico.setMinimumWidth(190)

        etiqueta_grafico = QLabel("Gráfico")
        etiqueta_grafico.setObjectName("etiquetaFiltro")
        self.combo_grafico = QComboBox()
        self.combo_grafico.setMinimumWidth(280)
        opciones = [
            ("Unidades por sucursal", "unidades_sucursal"),
            ("Valor del inventario por sucursal", "valor_sucursal"),
            ("Participación por categoría", "categoria"),
            ("Top 10 productos por unidades", "top_productos"),
            ("Alertas de stock por sucursal", "alertas"),
            ("Precio promedio por categoría", "precio_categoria"),
        ]
        for texto, clave in opciones:
            self.combo_grafico.addItem(texto, clave)

        controles.addWidget(etiqueta_sucursal)
        controles.addWidget(self.combo_sucursal_grafico)
        controles.addSpacing(6)
        controles.addWidget(etiqueta_grafico)
        controles.addWidget(self.combo_grafico)
        controles.addStretch(1)

        self.figura = Figure(figsize=(10, 5.4), dpi=100, facecolor="#FFFFFF")
        self.canvas = FigureCanvas(self.figura)
        self.canvas.setMinimumHeight(420)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setIconSize(QSize(16, 16))

        self.lbl_insight = QLabel("")
        self.lbl_insight.setObjectName("insight")
        self.lbl_insight.setWordWrap(True)

        layout.addWidget(panel)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.lbl_insight)

        self.combo_sucursal_grafico.currentIndexChanged.connect(
            self._actualizar_grafico
        )
        self.combo_grafico.currentIndexChanged.connect(self._actualizar_grafico)
        return pagina

    def _crear_tab_analisis(self) -> QWidget:
        pagina = QWidget()
        pagina.setObjectName("pagina")
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(18, 18, 18, 16)
        layout.setSpacing(10)

        panel = QFrame()
        panel.setObjectName("panelControles")
        controles = QHBoxLayout(panel)
        controles.setContentsMargins(12, 10, 12, 10)
        controles.setSpacing(9)

        etiqueta = QLabel("Consulta")
        etiqueta.setObjectName("etiquetaFiltro")
        self.combo_analisis = QComboBox()
        self.combo_analisis.setMinimumWidth(300)
        opciones = [
            ("Vista previa (head y tail)", "preview"),
            ("Estructura y tipos (info)", "estructura"),
            ("Estadísticas descriptivas (describe)", "describe"),
            ("Valores nulos y duplicados", "nulos"),
            ("Resumen por sucursal", "sucursal"),
            ("Resumen por categoría", "categoria"),
            ("Alertas de stock bajo", "alertas"),
            ("Matriz de correlación", "correlacion"),
        ]
        for texto, clave in opciones:
            self.combo_analisis.addItem(texto, clave)
        self.combo_analisis.setCurrentIndex(1)

        nota = QLabel("Reporte generado en tiempo real con Pandas.")
        nota.setObjectName("nota")

        controles.addWidget(etiqueta)
        controles.addWidget(self.combo_analisis)
        controles.addWidget(nota)
        controles.addStretch(1)

        self.texto_analisis = QPlainTextEdit()
        self.texto_analisis.setObjectName("reporte")
        self.texto_analisis.setReadOnly(True)
        self.texto_analisis.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.texto_analisis.setFont(QFont("DejaVu Sans Mono", 10))

        layout.addWidget(panel)
        layout.addWidget(self.texto_analisis, 1)

        self.combo_analisis.currentIndexChanged.connect(
            self._actualizar_analisis
        )
        return pagina

    def _cargar_filtros(self) -> None:
        sucursales = [s for s in SUCURSALES if s in set(self.datos["Sucursal"])]
        sucursales += sorted(
            set(self.datos["Sucursal"]) - set(sucursales)
        )
        categorias = sorted(self.datos["Categoria"].unique())

        self.combo_sucursal_tabla.blockSignals(True)
        self.combo_sucursal_grafico.blockSignals(True)
        self.combo_categoria_tabla.blockSignals(True)

        self.combo_sucursal_tabla.clear()
        self.combo_sucursal_grafico.clear()
        self.combo_categoria_tabla.clear()

        self.combo_sucursal_tabla.addItem("Todas las sucursales", None)
        self.combo_sucursal_grafico.addItem("Todas las sucursales", None)
        self.combo_categoria_tabla.addItem("Todas las categorías", None)

        for sucursal in sucursales:
            self.combo_sucursal_tabla.addItem(sucursal, sucursal)
            self.combo_sucursal_grafico.addItem(sucursal, sucursal)
        for categoria in categorias:
            self.combo_categoria_tabla.addItem(categoria, categoria)

        self.combo_sucursal_tabla.blockSignals(False)
        self.combo_sucursal_grafico.blockSignals(False)
        self.combo_categoria_tabla.blockSignals(False)

    def _datos_filtrados(self) -> pd.DataFrame:
        datos = self.datos
        sucursal = self.combo_sucursal_tabla.currentData()
        categoria = self.combo_categoria_tabla.currentData()
        texto = self.busqueda.text().strip()

        if sucursal:
            datos = datos[datos["Sucursal"] == sucursal]
        if categoria:
            datos = datos[datos["Categoria"] == categoria]
        if texto:
            coincide = datos["Producto"].str.contains(
                texto, case=False, regex=False, na=False
            ) | datos["Codigo"].str.contains(
                texto, case=False, regex=False, na=False
            )
            datos = datos[coincide]
        return datos

    def _limpiar_filtros(self) -> None:
        self.combo_sucursal_tabla.blockSignals(True)
        self.combo_categoria_tabla.blockSignals(True)
        self.busqueda.blockSignals(True)
        self.combo_sucursal_tabla.setCurrentIndex(0)
        self.combo_categoria_tabla.setCurrentIndex(0)
        self.busqueda.clear()
        self.combo_sucursal_tabla.blockSignals(False)
        self.combo_categoria_tabla.blockSignals(False)
        self.busqueda.blockSignals(False)
        self._actualizar_tabla()

    def _actualizar_todo(self) -> None:
        self._actualizar_tarjetas()
        self._actualizar_tabla()
        self._actualizar_grafico()
        self._actualizar_analisis()

    def _actualizar_tarjetas(self) -> None:
        valor = self.datos["Valor_Inventario"].sum()
        unidades = self.datos["Cantidad"].sum()
        productos = self.datos["Producto"].nunique()
        alertas = int(self.datos["Bajo_Stock"].sum())
        sucursales = self.datos["Sucursal"].nunique()

        self.tarjetas["valor"].actualizar(
            formato_moneda(valor),
            f"{len(self.datos):,} registros en {sucursales} sucursales",
        )
        self.tarjetas["unidades"].actualizar(
            formato_entero(unidades),
            "Unidades físicas registradas en total",
        )
        self.tarjetas["productos"].actualizar(
            formato_entero(productos),
            f"Distribuidos en {self.datos['Categoria'].nunique()} categorías",
        )
        self.tarjetas["alertas"].actualizar(
            formato_entero(alertas),
            "Productos por debajo del stock mínimo",
        )

    def _actualizar_tabla(self, *_args) -> None:
        datos = self._datos_filtrados()
        self.tabla.setSortingEnabled(False)
        self.tabla.clearContents()
        self.tabla.setRowCount(len(datos))

        for fila, (_, registro) in enumerate(datos.iterrows()):
            cantidad = int(registro["Cantidad"])
            stock_minimo = int(registro["Stock_Minimo"])
            valor = float(registro["Valor_Inventario"])

            if cantidad == 0:
                estado = "Agotado"
                color_estado = QColor("#991B1B")
            elif cantidad < stock_minimo:
                estado = "Bajo stock"
                color_estado = QColor("#B45309")
            else:
                estado = "Disponible"
                color_estado = QColor("#15803D")

            item_codigo = QTableWidgetItem(str(registro["Codigo"]))
            item_codigo.setTextAlignment(Qt.AlignCenter)
            item_producto = QTableWidgetItem(str(registro["Producto"]))
            item_categoria = QTableWidgetItem(str(registro["Categoria"]))
            item_sucursal = QTableWidgetItem(str(registro["Sucursal"]))
            item_cantidad = ItemNumero(cantidad, formato_entero(cantidad))
            item_minimo = ItemNumero(stock_minimo, formato_entero(stock_minimo))
            item_precio = ItemNumero(
                float(registro["Precio_Unitario"]),
                formato_moneda(float(registro["Precio_Unitario"])),
            )
            item_valor = ItemNumero(valor, formato_moneda(valor))
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignCenter)
            item_estado.setForeground(QBrush(color_estado))
            fuente_estado = item_estado.font()
            fuente_estado.setBold(True)
            item_estado.setFont(fuente_estado)
            item_fecha = ItemFecha(registro["Fecha_Ingreso"])

            if cantidad < stock_minimo:
                item_cantidad.setForeground(QBrush(QColor("#B91C1C")))
                item_minimo.setForeground(QBrush(QColor("#B91C1C")))
                fuente_cantidad = item_cantidad.font()
                fuente_cantidad.setBold(True)
                item_cantidad.setFont(fuente_cantidad)

            items = [
                item_codigo,
                item_producto,
                item_categoria,
                item_sucursal,
                item_cantidad,
                item_minimo,
                item_precio,
                item_valor,
                item_estado,
                item_fecha,
            ]
            for columna, item in enumerate(items):
                self.tabla.setItem(fila, columna, item)

        self.tabla.setSortingEnabled(True)
        unidades = datos["Cantidad"].sum()
        valor = datos["Valor_Inventario"].sum()
        self.lbl_resultados.setText(
            f"Mostrando {len(datos):,} de {len(self.datos):,} registros  |  "
            f"{formato_entero(unidades)} unidades  |  "
            f"{formato_moneda(valor)} en inventario"
        )

    def _actualizar_grafico(self, *_args) -> None:
        tipo = self.combo_grafico.currentData()
        sucursal = self.combo_sucursal_grafico.currentData()
        datos = (
            self.datos
            if sucursal is None
            else self.datos[self.datos["Sucursal"] == sucursal]
        )

        self.figura.clear()
        eje = self.figura.add_subplot(111)

        if datos.empty:
            eje.text(
                0.5,
                0.5,
                "No hay datos para los filtros seleccionados",
                ha="center",
                va="center",
                transform=eje.transAxes,
                fontsize=13,
                color="#64748B",
            )
            eje.set_axis_off()
            self.lbl_insight.setText("No hay datos disponibles.")
        elif tipo == "unidades_sucursal":
            self._grafico_unidades(eje, sucursal)
        elif tipo == "valor_sucursal":
            self._grafico_valor(eje, sucursal)
        elif tipo == "categoria":
            self._grafico_categoria(eje, datos, sucursal)
        elif tipo == "top_productos":
            self._grafico_top_productos(eje, datos, sucursal)
        elif tipo == "alertas":
            self._grafico_alertas(eje, sucursal)
        elif tipo == "precio_categoria":
            self._grafico_precio(eje, datos, sucursal)

        self.figura.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    def _configurar_ejes(self, eje, eje_grilla: str = "y") -> None:
        for lado in ("top", "right"):
            eje.spines[lado].set_visible(False)
        eje.spines["left"].set_color("#CBD5E1")
        eje.spines["bottom"].set_color("#CBD5E1")
        eje.grid(
            axis=eje_grilla,
            color="#E2E8F0",
            linewidth=0.8,
            alpha=0.9,
        )
        eje.set_axisbelow(True)
        eje.tick_params(axis="both", labelsize=9.5, length=0)

    def _grafico_unidades(self, eje, sucursal: str | None) -> None:
        serie = (
            self.datos.groupby("Sucursal")["Cantidad"]
            .sum()
            .reindex(SUCURSALES, fill_value=0)
        )
        colores = [
            COLORES_SUCURSAL.get(nombre, COLOR_ACCENTO)
            if sucursal is None or nombre == sucursal
            else COLOR_GRIS
            for nombre in serie.index
        ]
        barras = eje.bar(
            serie.index, serie.values, color=colores, width=0.62
        )
        eje.bar_label(
            barras,
            labels=[formato_entero(valor) for valor in serie.values],
            padding=5,
            fontsize=9,
            fontweight="bold",
            color="#334155",
        )
        eje.set_ylim(0, serie.max() * 1.15)
        eje.yaxis.set_major_formatter(
            FuncFormatter(lambda valor, _: f"{valor:,.0f}")
        )
        eje.set_ylabel("Unidades disponibles")
        eje.set_title(
            "Unidades disponibles por sucursal",
            loc="left",
            fontsize=15,
            fontweight="bold",
            pad=16,
        )
        self._configurar_ejes(eje)

        total = serie.sum()
        if sucursal is None:
            principal = serie.idxmax()
            participacion = serie.max() / total * 100
            self.lbl_insight.setText(
                f"{principal} concentra la mayor cantidad de unidades: "
                f"{formato_entero(serie.max())} ({participacion:.1f}% del total)."
            )
        else:
            participacion = serie.get(sucursal, 0) / total * 100
            self.lbl_insight.setText(
                f"{sucursal} tiene {formato_entero(serie.get(sucursal, 0))} "
                f"unidades, equivalentes al {participacion:.1f}% del inventario."
            )

    def _grafico_valor(self, eje, sucursal: str | None) -> None:
        serie = (
            self.datos.groupby("Sucursal")["Valor_Inventario"]
            .sum()
            .reindex(SUCURSALES, fill_value=0)
            .sort_values()
        )
        colores = [
            COLORES_SUCURSAL.get(nombre, COLOR_ACCENTO)
            if sucursal is None or nombre == sucursal
            else COLOR_GRIS
            for nombre in serie.index
        ]
        barras = eje.barh(serie.index, serie.values, color=colores, height=0.6)
        eje.bar_label(
            barras,
            labels=[formato_moneda(valor) for valor in serie.values],
            padding=5,
            fontsize=9,
            fontweight="bold",
            color="#334155",
        )
        eje.set_xlim(0, serie.max() * 1.27)
        eje.xaxis.set_major_formatter(
            FuncFormatter(lambda valor, _: f"${valor:,.0f}")
        )
        eje.set_xlabel("Valor del inventario (USD)")
        eje.set_title(
            "Valor del inventario por sucursal",
            loc="left",
            fontsize=15,
            fontweight="bold",
            pad=16,
        )
        self._configurar_ejes(eje, "x")

        principal = serie.idxmax()
        participacion = serie.max() / serie.sum() * 100
        if sucursal is None:
            self.lbl_insight.setText(
                f"{principal} aporta el mayor valor: "
                f"{formato_moneda(serie.max())} ({participacion:.1f}% del total)."
            )
        else:
            valor = serie.get(sucursal, 0)
            self.lbl_insight.setText(
                f"{sucursal} aporta {formato_moneda(valor)} al valor total del "
                f"inventario ({valor / serie.sum() * 100:.1f}%)."
            )

    def _grafico_categoria(
        self, eje, datos: pd.DataFrame, sucursal: str | None
    ) -> None:
        serie = (
            datos.groupby("Categoria")["Valor_Inventario"]
            .sum()
            .sort_values(ascending=False)
        )
        colores = [
            COLORES_CATEGORIA.get(categoria, "#64748B")
            for categoria in serie.index
        ]
        cuñas, _, _ = eje.pie(
            serie.values,
            colors=colores,
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.42, "edgecolor": "#FFFFFF", "linewidth": 2},
            autopct=lambda pct: f"{pct:.1f}%" if pct >= 5 else "",
            pctdistance=0.79,
            textprops={
                "color": "#FFFFFF",
                "fontsize": 9,
                "fontweight": "bold",
            },
        )
        eje.text(
            0,
            0.07,
            "Valor total",
            ha="center",
            va="center",
            fontsize=9,
            color="#64748B",
        )
        eje.text(
            0,
            -0.08,
            formato_moneda(serie.sum()),
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="#0F172A",
        )
        eje.legend(
            cuñas,
            [
                f"{categoria}  {formato_moneda(valor)}"
                for categoria, valor in serie.items()
            ],
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            frameon=False,
            fontsize=9,
        )
        eje.set_aspect("equal")
        alcance = "Todas las sucursales" if sucursal is None else sucursal
        eje.set_title(
            f"Participación por categoría | {alcance}",
            loc="left",
            fontsize=15,
            fontweight="bold",
            pad=16,
        )
        self.lbl_insight.setText(
            f"{serie.index[0]} representa el {serie.iloc[0] / serie.sum() * 100:.1f}% "
            f"del valor del inventario ({formato_moneda(serie.iloc[0])})."
        )

    def _grafico_top_productos(
        self, eje, datos: pd.DataFrame, sucursal: str | None
    ) -> None:
        serie = (
            datos.groupby("Producto")["Cantidad"]
            .sum()
            .nlargest(10)
            .sort_values()
        )
        colores = [COLOR_ACCENTO] * len(serie)
        colores[-1] = "#D97706"
        barras = eje.barh(serie.index, serie.values, color=colores, height=0.65)
        eje.bar_label(
            barras,
            labels=[formato_entero(valor) for valor in serie.values],
            padding=5,
            fontsize=9,
            fontweight="bold",
            color="#334155",
        )
        eje.set_xlim(0, serie.max() * 1.13)
        eje.xaxis.set_major_formatter(
            FuncFormatter(lambda valor, _: f"{valor:,.0f}")
        )
        eje.set_xlabel("Unidades disponibles")
        eje.set_title(
            "Top 10 productos por unidades",
            loc="left",
            fontsize=15,
            fontweight="bold",
            pad=16,
        )
        self._configurar_ejes(eje, "x")
        self.lbl_insight.setText(
            f"{serie.index[-1]} es el producto con más unidades: "
            f"{formato_entero(serie.iloc[-1])}."
        )

    def _grafico_alertas(self, eje, sucursal: str | None) -> None:
        alertas = self.datos[self.datos["Bajo_Stock"]]
        serie = (
            alertas.groupby("Sucursal")
            .size()
            .reindex(SUCURSALES, fill_value=0)
        )
        colores = [
            COLORES_SUCURSAL.get(nombre, COLOR_ACCENTO)
            if sucursal is None or nombre == sucursal
            else COLOR_GRIS
            for nombre in serie.index
        ]
        barras = eje.bar(
            serie.index, serie.values, color=colores, width=0.62
        )
        eje.bar_label(
            barras,
            labels=[formato_entero(valor) for valor in serie.values],
            padding=5,
            fontsize=9,
            fontweight="bold",
            color="#334155",
        )
        eje.set_ylim(0, max(serie.max() * 1.18, 1))
        eje.yaxis.set_major_formatter(
            FuncFormatter(lambda valor, _: f"{valor:,.0f}")
        )
        eje.set_ylabel("Productos bajo mínimo")
        eje.set_title(
            "Alertas de stock por sucursal",
            loc="left",
            fontsize=15,
            fontweight="bold",
            pad=16,
        )
        self._configurar_ejes(eje)

        principal = serie.idxmax()
        if sucursal is None:
            self.lbl_insight.setText(
                f"{principal} registra la mayor cantidad de alertas: "
                f"{int(serie.max())} productos por debajo del stock mínimo."
            )
        else:
            self.lbl_insight.setText(
                f"{sucursal} registra {int(serie.get(sucursal, 0))} productos "
                f"por debajo del stock mínimo."
            )

    def _grafico_precio(
        self, eje, datos: pd.DataFrame, sucursal: str | None
    ) -> None:
        serie = (
            datos.groupby("Categoria")["Precio_Unitario"]
            .mean()
            .sort_values()
        )
        barras = eje.barh(
            serie.index,
            serie.values,
            color=[
                COLORES_CATEGORIA.get(categoria, "#64748B")
                for categoria in serie.index
            ],
            height=0.62,
        )
        eje.bar_label(
            barras,
            labels=[formato_moneda(valor) for valor in serie.values],
            padding=5,
            fontsize=9,
            fontweight="bold",
            color="#334155",
        )
        eje.set_xlim(0, serie.max() * 1.25)
        eje.xaxis.set_major_formatter(
            FuncFormatter(lambda valor, _: f"${valor:,.2f}")
        )
        eje.set_xlabel("Precio unitario promedio (USD)")
        eje.set_title(
            "Precio promedio por categoría",
            loc="left",
            fontsize=15,
            fontweight="bold",
            pad=16,
        )
        self._configurar_ejes(eje, "x")
        self.lbl_insight.setText(
            f"{serie.index[-1]} tiene el precio promedio más alto: "
            f"{formato_moneda(serie.iloc[-1])} por unidad."
        )

    def _actualizar_analisis(self, *_args) -> None:
        vista = self.combo_analisis.currentData()
        generadores = {
            "preview": self._reporte_preview,
            "estructura": self._reporte_estructura,
            "describe": self._reporte_describe,
            "nulos": self._reporte_nulos,
            "sucursal": self._reporte_sucursal,
            "categoria": self._reporte_categoria,
            "alertas": self._reporte_alertas,
            "correlacion": self._reporte_correlacion,
        }
        generador = generadores.get(vista, self._reporte_estructura)
        self.texto_analisis.setPlainText(generador())

    def _reporte_preview(self) -> str:
        with pd.option_context("display.width", 240, "display.max_columns", None):
            return (
                "VISTA PREVIA DEL INVENTARIO\n"
                f"Dimensiones: {self.datos.shape[0]} filas x "
                f"{self.datos.shape[1]} columnas\n\n"
                "Primeras 10 filas\n"
                + self.datos.head(10).to_string(index=False)
                + "\n\nÚltimas 10 filas\n"
                + self.datos.tail(10).to_string(index=False)
            )

    def _reporte_estructura(self) -> str:
        buffer = io.StringIO()
        self.datos.info(buf=buffer)
        return (
            "ESTRUCTURA Y TIPOS DE DATOS\n"
            f"Dimensiones: {self.datos.shape[0]} filas x "
            f"{self.datos.shape[1]} columnas\n"
            f"Memoria: {self.datos.memory_usage(deep=True).sum() / 1024:.1f} KB\n\n"
            + buffer.getvalue()
            + "\nTipos por columna\n"
            + self.datos.dtypes.to_string()
        )

    def _reporte_describe(self) -> str:
        with pd.option_context(
            "display.width",
            240,
            "display.max_columns",
            None,
            "display.float_format",
            lambda valor: f"{valor:,.2f}",
        ):
            return (
                "ESTADÍSTICAS DESCRIPTIVAS\n\n"
                + self.datos.describe(include="all").to_string()
                + "\n\nResumen numérico\n"
                + self.datos[
                    [
                        "Cantidad",
                        "Stock_Minimo",
                        "Precio_Unitario",
                        "Valor_Inventario",
                    ]
                ].describe().to_string()
            )

    def _reporte_nulos(self) -> str:
        nulos = pd.DataFrame(
            {
                "Nulos": self.datos.isnull().sum(),
                "Porcentaje": (
                    self.datos.isnull().mean() * 100
                ).round(2),
                "Valores únicos": self.datos.nunique(),
            }
        )
        return (
            "CALIDAD DE LOS DATOS\n"
            f"Filas duplicadas: {self.datos.duplicated().sum()}\n"
            f"Filas totales: {len(self.datos)}\n"
            f"Sucursales: {self.datos['Sucursal'].nunique()}\n"
            f"Productos diferentes: {self.datos['Producto'].nunique()}\n\n"
            + nulos.to_string()
        )

    def _reporte_sucursal(self) -> str:
        resumen = (
            self.datos.groupby("Sucursal")
            .agg(
                Registros=("Codigo", "size"),
                Productos=("Producto", "nunique"),
                Unidades=("Cantidad", "sum"),
                Valor_Inventario=("Valor_Inventario", "sum"),
                Alertas_Stock=("Bajo_Stock", "sum"),
            )
            .sort_values("Valor_Inventario", ascending=False)
        )
        resumen["Participación"] = (
            resumen["Valor_Inventario"]
            / resumen["Valor_Inventario"].sum()
            * 100
        ).round(2)
        with pd.option_context(
            "display.width", 240, "display.float_format", lambda v: f"{v:,.2f}"
        ):
            return (
                "RESUMEN POR SUCURSAL\n"
                "Agrupación con groupby y agregaciones de Pandas\n\n"
                + resumen.to_string()
            )

    def _reporte_categoria(self) -> str:
        resumen = (
            self.datos.groupby("Categoria")
            .agg(
                Productos=("Producto", "nunique"),
                Unidades=("Cantidad", "sum"),
                Valor_Inventario=("Valor_Inventario", "sum"),
                Precio_Promedio=("Precio_Unitario", "mean"),
            )
            .sort_values("Valor_Inventario", ascending=False)
        )
        with pd.option_context(
            "display.width", 240, "display.float_format", lambda v: f"{v:,.2f}"
        ):
            return (
                "RESUMEN POR CATEGORÍA\n\n"
                + resumen.to_string()
                + "\n\nProductos con mayor valor acumulado\n"
                + (
                    self.datos.groupby(["Producto", "Categoria"])[
                        "Valor_Inventario"
                    ]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .to_string()
                )
            )

    def _reporte_alertas(self) -> str:
        alertas = self.datos[self.datos["Bajo_Stock"]].sort_values(
            ["Sucursal", "Cantidad"]
        )
        columnas = [
            "Sucursal",
            "Producto",
            "Cantidad",
            "Stock_Minimo",
            "Precio_Unitario",
        ]
        return (
            "ALERTAS DE STOCK BAJO\n"
            f"Productos por debajo del mínimo: {len(alertas)}\n\n"
            + alertas[columnas].to_string(index=False)
        )

    def _reporte_correlacion(self) -> str:
        columnas = [
            "Cantidad",
            "Stock_Minimo",
            "Precio_Unitario",
            "Valor_Inventario",
        ]
        return (
            "MATRIZ DE CORRELACIÓN\n"
            "Coeficiente de Pearson entre variables numéricas\n\n"
            + self.datos[columnas].corr().round(3).to_string()
        )

    def _recargar_datos(self) -> None:
        try:
            self.datos = cargar_datos(self.ruta_datos)
        except Exception as error:
            QMessageBox.critical(
                self,
                "No se pudo cargar el inventario",
                f"Revise el archivo {self.ruta_datos.name}.\n\n{error}",
            )
            return

        self._cargar_filtros()
        self._limpiar_filtros()
        self._actualizar_todo()
        self.statusBar().showMessage(
            f"Datos actualizados: {len(self.datos):,} registros | "
            f"{self.datos['Sucursal'].nunique()} sucursales"
        )


def main() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    aplicacion = QApplication(sys.argv)
    aplicacion.setApplicationName("Inventario Comercial")
    aplicacion.setFont(QFont("DejaVu Sans", 10))
    aplicacion.setStyle("Fusion")

    try:
        ventana = VentanaInventario()
    except Exception as error:
        QMessageBox.critical(
            None,
            "Error al iniciar",
            f"No fue posible cargar el inventario.\n\n{error}",
        )
        return 1

    ventana.show()
    return aplicacion.exec_()


if __name__ == "__main__":
    sys.exit(main())
