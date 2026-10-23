from pathlib import Path

import pandas as pd

RUTA_INVENTARIO = Path(__file__).with_name("inventario.csv")


def cargar_inventario(ruta: Path | str = RUTA_INVENTARIO) -> pd.DataFrame:
    inventario = pd.read_csv(ruta, parse_dates=["Fecha_Ingreso"])
    inventario["Valor_Inventario"] = (
        inventario["Cantidad"] * inventario["Precio_Unitario"]
    ).round(2)
    inventario["Bajo_Stock"] = inventario["Cantidad"] < inventario["Stock_Minimo"]
    return inventario


def mostrar_titulo(texto: str) -> None:
    print(f"\n{'=' * 82}")
    print(texto)
    print("=" * 82)


def main() -> None:
    inventario = cargar_inventario()
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 170)
    pd.set_option("display.float_format", lambda valor: f"{valor:,.2f}")

    mostrar_titulo("INSPECCIÓN DEL INVENTARIO CON PANDAS")
    print(f"Archivo analizado: {RUTA_INVENTARIO}")
    print(f"Dimensiones (filas, columnas): {inventario.shape}")
    print(f"Columnas: {list(inventario.columns)}")

    mostrar_titulo("1. PRIMEROS Y ÚLTIMOS REGISTROS")
    print("\nPrimeras 8 filas:")
    print(inventario.head(8).to_string(index=False))
    print("\nÚltimas 5 filas:")
    print(inventario.tail(5).to_string(index=False))

    mostrar_titulo("2. ESTRUCTURA Y TIPOS DE DATOS")
    inventario.info()

    mostrar_titulo("3. VALORES NULOS, DUPLICADOS Y VALORES ÚNICOS")
    nulos = pd.DataFrame(
        {
            "Nulos": inventario.isnull().sum(),
            "Porcentaje": (inventario.isnull().mean() * 100).round(2),
            "Valores_Unicos": inventario.nunique(),
        }
    )
    print(nulos.to_string())
    print(f"\nFilas duplicadas: {inventario.duplicated().sum()}")
    print(f"Sucursales: {inventario['Sucursal'].nunique()}")
    print(f"Categorías: {inventario['Categoria'].nunique()}")
    print(f"Productos diferentes: {inventario['Producto'].nunique()}")

    mostrar_titulo("4. ESTADÍSTICAS DESCRIPTIVAS")
    print(inventario.describe(include="all").to_string())

    mostrar_titulo("5. RESUMEN POR SUCURSAL")
    resumen_sucursal = (
        inventario.groupby("Sucursal")
        .agg(
            Registros=("Codigo", "size"),
            Productos=("Producto", "nunique"),
            Unidades=("Cantidad", "sum"),
            Promedio_Unidades=("Cantidad", "mean"),
            Valor_Inventario=("Valor_Inventario", "sum"),
            Alertas_Stock=("Bajo_Stock", "sum"),
        )
        .sort_values("Valor_Inventario", ascending=False)
    )
    print(resumen_sucursal.to_string())
    print("\nParticipación del valor por sucursal:")
    participacion = (
        resumen_sucursal["Valor_Inventario"]
        .div(resumen_sucursal["Valor_Inventario"].sum())
        .mul(100)
        .round(2)
    )
    print(participacion.to_string())

    mostrar_titulo("6. RESUMEN POR CATEGORÍA")
    resumen_categoria = (
        inventario.groupby("Categoria")
        .agg(
            Productos=("Producto", "nunique"),
            Unidades=("Cantidad", "sum"),
            Valor_Inventario=("Valor_Inventario", "sum"),
            Precio_Promedio=("Precio_Unitario", "mean"),
        )
        .sort_values("Valor_Inventario", ascending=False)
    )
    print(resumen_categoria.to_string())

    mostrar_titulo("7. PRODUCTOS CON MAYOR VALOR EN INVENTARIO")
    top_productos = (
        inventario.groupby(["Codigo", "Producto", "Categoria"])
        .agg(
            Unidades=("Cantidad", "sum"),
            Valor_Inventario=("Valor_Inventario", "sum"),
        )
        .sort_values("Valor_Inventario", ascending=False)
        .head(10)
    )
    print(top_productos.to_string())

    mostrar_titulo("8. ALERTAS DE STOCK BAJO")
    alertas = inventario.loc[
        inventario["Bajo_Stock"],
        [
            "Sucursal",
            "Producto",
            "Cantidad",
            "Stock_Minimo",
            "Precio_Unitario",
        ],
    ].sort_values(["Sucursal", "Cantidad"])
    print(f"Registros por debajo del stock mínimo: {len(alertas)}")
    print(alertas.to_string(index=False))

    mostrar_titulo("9. CORRELACIÓN ENTRE VARIABLES NUMÉRICAS")
    columnas_numericas = [
        "Cantidad",
        "Stock_Minimo",
        "Precio_Unitario",
        "Valor_Inventario",
    ]
    print(inventario[columnas_numericas].corr().round(3).to_string())


if __name__ == "__main__":
    main()
