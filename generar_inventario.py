from datetime import date, timedelta
from pathlib import Path
import random

import pandas as pd

RUTA_SALIDA = Path(__file__).with_name("inventario.csv")
SUCURSALES = ["San Salvador", "Santa Ana", "San Miguel", "La Libertad", "Sonsonate"]
FACTORES_SUCURSAL = {
    "San Salvador": 1.70,
    "Santa Ana": 1.28,
    "San Miguel": 1.16,
    "La Libertad": 0.95,
    "Sonsonate": 0.82,
}
CATALOGO = [
    ("Abarrotes", "Arroz Blanco 5 lb", 4.85, 30),
    ("Abarrotes", "Frijol Rojo 5 lb", 6.50, 30),
    ("Abarrotes", "Azúcar Blanca 5 lb", 4.20, 25),
    ("Abarrotes", "Aceite Vegetal 1 L", 3.25, 24),
    ("Abarrotes", "Café Molido 1 lb", 7.90, 18),
    ("Abarrotes", "Sal de Mesa 1 kg", 1.10, 20),
    ("Abarrotes", "Pasta Larga 500 g", 1.35, 20),
    ("Abarrotes", "Salsa de Tomate 400 g", 1.75, 18),
    ("Abarrotes", "Atún en Agua 140 g", 1.60, 24),
    ("Abarrotes", "Galletas de Soda 12 u", 1.95, 24),
    ("Bebidas", "Agua Purificada 600 ml", 0.75, 40),
    ("Bebidas", "Refresco Cola 2 L", 2.35, 30),
    ("Bebidas", "Jugo de Naranja 1 L", 2.80, 20),
    ("Bebidas", "Café Instantáneo 200 g", 6.25, 15),
    ("Bebidas", "Bebida Energética 500 ml", 2.10, 24),
    ("Lácteos", "Leche Entera 1 L", 1.95, 35),
    ("Lácteos", "Queso Fresco 1 lb", 4.25, 18),
    ("Lácteos", "Crema 500 ml", 3.50, 15),
    ("Lácteos", "Yogurt Natural 1 L", 3.15, 15),
    ("Lácteos", "Mantequilla 250 g", 3.60, 12),
    ("Limpieza", "Detergente 1 kg", 3.95, 20),
    ("Limpieza", "Jabón de Baño 110 g", 1.25, 30),
    ("Limpieza", "Cloro 1 L", 1.45, 20),
    ("Limpieza", "Limpiador Multiusos 1 L", 2.60, 18),
    ("Limpieza", "Papel Higiénico 4 rollos", 2.95, 25),
    ("Cuidado Personal", "Shampoo 750 ml", 5.75, 15),
    ("Cuidado Personal", "Pasta Dental 100 ml", 2.45, 20),
    ("Cuidado Personal", "Desodorante 150 ml", 3.85, 15),
    ("Cuidado Personal", "Jabón Facial 100 g", 2.15, 15),
    ("Cuidado Personal", "Toallas Húmedas 80 u", 2.70, 18),
]


def generar_inventario() -> pd.DataFrame:
    aleatorio = random.Random(2026)
    inicio = date(2026, 1, 1)
    dias_disponibles = (date(2026, 10, 23) - inicio).days
    filas = []

    for sucursal in SUCURSALES:
        factor = FACTORES_SUCURSAL[sucursal]
        for indice, (categoria, producto, precio_base, stock_minimo) in enumerate(
            CATALOGO, start=1
        ):
            if aleatorio.random() < 0.025:
                continue

            cantidad = max(0, int(aleatorio.gauss(85 * factor, 30)))
            if aleatorio.random() < 0.15:
                cantidad = aleatorio.randint(0, max(stock_minimo - 1, 0))

            precio = round(
                precio_base * factor * aleatorio.uniform(0.96, 1.04), 2
            )
            fecha = inicio + timedelta(days=aleatorio.randint(0, dias_disponibles))
            filas.append(
                {
                    "Codigo": f"P{indice:03d}",
                    "Producto": producto,
                    "Categoria": categoria,
                    "Sucursal": sucursal,
                    "Cantidad": cantidad,
                    "Stock_Minimo": stock_minimo,
                    "Precio_Unitario": precio,
                    "Fecha_Ingreso": fecha,
                }
            )

    return pd.DataFrame(filas).sort_values(
        ["Sucursal", "Categoria", "Producto"], ignore_index=True
    )


def main() -> None:
    inventario = generar_inventario()
    inventario.to_csv(
        RUTA_SALIDA,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )
    valor_total = (inventario["Cantidad"] * inventario["Precio_Unitario"]).sum()
    print(f"Archivo generado: {RUTA_SALIDA}")
    print(f"Registros: {len(inventario)}")
    print(f"Sucursales: {inventario['Sucursal'].nunique()}")
    print(f"Productos: {inventario['Producto'].nunique()}")
    print(f"Unidades: {inventario['Cantidad'].sum():,}")
    print(f"Valor total: ${valor_total:,.2f}")


if __name__ == "__main__":
    main()
