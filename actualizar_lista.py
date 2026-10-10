"""Genera articulos.js a partir de los archivos DBF de LINCE.

Uso:  python actualizar_lista.py [carpeta_con_los_dbf]
Por defecto lee C:\\linceV3\\INV2013\\DBF. Necesita art.dbf, col.dbf, mat.dbf y comb.dbf.

articulos.js lleva SOLO datos de catálogo (descripción, precio, colores, talles).
Las cantidades de stock NO se publican: la comparación se hace en comparar.html
leyendo comb.dbf directo en el navegador.
"""
import json
import os
import struct
import sys
from collections import defaultdict


def leer_dbf(ruta):
    with open(ruta, "rb") as f:
        cab = f.read(32)
        n, largo_cab, largo_reg = struct.unpack("<IHH", cab[4:12])
        campos = []
        while True:
            d = f.read(32)
            if d[0] == 0x0D:
                break
            campos.append((d[:11].split(b"\0")[0].decode("latin-1"), d[16]))
        f.seek(largo_cab)
        filas = []
        for _ in range(n):
            r = f.read(largo_reg)
            if len(r) < largo_reg:
                break
            if r[0:1] == b"*":  # registro borrado
                continue
            p, fila = 1, {}
            for nombre, largo in campos:
                fila[nombre] = r[p:p + largo].decode("latin-1").strip()
                p += largo
            filas.append(fila)
        return filas


def buscar(carpeta, nombre):
    for f in os.listdir(carpeta):
        if f.lower() == nombre:
            return os.path.join(carpeta, f)
    sys.exit(f"Falta {nombre} en {carpeta}")


def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else r"C:\linceV3\INV2013\DBF"
    art = leer_dbf(buscar(carpeta, "art.dbf"))
    col = leer_dbf(buscar(carpeta, "col.dbf"))
    mat = leer_dbf(buscar(carpeta, "mat.dbf"))
    comb = leer_dbf(buscar(carpeta, "comb.dbf"))

    articulos = {}
    for r in art:
        cod = r["ARTCOD"].upper()
        if not cod:
            continue
        try:
            precio = round(float(r["APR2"] or 0), 2)
        except ValueError:
            precio = 0
        articulos[cod] = [r["ARTDES"], precio or None, r["ARTGRUPO"]]

    # colores: los códigos de 1 carácter (o con . y -) son títulos de la tabla
    colores = {r["COLCOD"].upper(): r["COLDES"] for r in col
               if len(r["COLCOD"]) == 2 and "." not in r["COLCOD"] and "-" not in r["COLCOD"]}

    curvas = {}
    for r in mat:
        talles = [r[f"MC{i}"].upper() for i in range(1, 26) if r.get(f"MC{i}")]
        if r["MATCOD"] and talles:
            curvas[r["MATCOD"]] = talles

    # artículos que en LINCE no llevan color: su código de barra trae solo el talle
    con_color = defaultdict(bool)
    for r in comb:
        con_color[r["COART"].upper()] |= bool(r["COCOL"])
    sin_color = sorted(a for a, c in con_color.items() if not c)

    js = ("// Generado por actualizar_lista.py desde LINCE. No editar a mano.\n"
          "window.ARTICULOS_DATA=" + json.dumps(articulos, ensure_ascii=False, separators=(",", ":")) + ";\n"
          "window.COLORES_DATA=" + json.dumps(colores, ensure_ascii=False, separators=(",", ":")) + ";\n"
          "window.CURVAS_DATA=" + json.dumps(curvas, ensure_ascii=False, separators=(",", ":")) + ";\n"
          "window.SIN_COLOR_DATA=" + json.dumps(sin_color, separators=(",", ":")) + ";\n")
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "articulos.js")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"articulos.js: {len(articulos)} artículos, {len(colores)} colores, "
          f"{len(curvas)} curvas de talle, {len(sin_color)} artículos sin color")


if __name__ == "__main__":
    main()
