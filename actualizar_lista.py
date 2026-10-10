"""Genera articulos.js a partir de los archivos DBF de LINCE.

Uso:  python actualizar_lista.py [carpeta_con_los_dbf]
Por defecto lee C:\\linceV3\\INV2013\\DBF. Necesita art.dbf, col.dbf, mat.dbf y comb.dbf.

articulos.js lleva SOLO datos de catálogo (descripción, precio, colores, talles).
Las cantidades de stock van en stock.json CIFRADAS (AES-GCM, clave derivada con PBKDF2)
con la contraseña guardada en CLAVE_ARCHIVO, que queda FUERA del repositorio.
El botón "Consultar stock" de la app las descifra en el celular con esa contraseña.
"""
import base64
import datetime
import json
import os
import secrets
import struct
import sys
from collections import defaultdict

CARPETA = os.path.dirname(os.path.abspath(__file__))
CLAVE_ARCHIVO = os.path.join(os.path.dirname(CARPETA), "control-stock-CONTRASEÑA.txt")
ITERACIONES = 250000


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
    with open(os.path.join(CARPETA, "articulos.js"), "w", encoding="utf-8") as f:
        f.write(js)
    print(f"articulos.js: {len(articulos)} artículos, {len(colores)} colores, "
          f"{len(curvas)} curvas de talle, {len(sin_color)} artículos sin color")

    generar_stock(comb, os.path.getmtime(buscar(carpeta, "comb.dbf")))


def leer_o_crear_clave():
    if not os.path.exists(CLAVE_ARCHIVO):
        palabras = ["remera", "camisa", "jean", "buzo", "campera", "chomba", "bermuda", "sweater",
                    "saco", "chaleco", "boxer", "media", "gorra", "cinto", "corbata", "polar"]
        clave = "-".join(secrets.choice(palabras) for _ in range(3)) + "-" + str(secrets.randbelow(900) + 100)
        with open(CLAVE_ARCHIVO, "w", encoding="utf-8") as f:
            f.write(clave + "\n\n"
                    "Contraseña para ver el stock en la app Control de Stock (botón Consultar stock).\n"
                    "Se pone una sola vez en cada celular. No la compartas.\n"
                    "Si la cambiás acá, hay que volver a correr actualizar_lista.py y publicar.\n")
        print(f"Nueva contraseña creada en {CLAVE_ARCHIVO}")
    with open(CLAVE_ARCHIVO, encoding="utf-8") as f:
        return f.readline().strip()


def generar_stock(comb, fecha_archivo):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    suma = defaultdict(float)
    for r in comb:
        try:
            cant = float(r["COCANT"] or 0)
        except ValueError:
            continue
        if r["COART"] and cant:
            suma[(r["COART"].upper(), r["COCOL"].upper(), r["COTLL"].upper())] += cant
    stock = defaultdict(list)
    for (art, color, talle), cant in sorted(suma.items()):
        if cant:
            stock[art].append([color, talle, int(cant) if cant == int(cant) else cant])

    fecha = datetime.datetime.fromtimestamp(fecha_archivo).strftime("%Y-%m-%dT%H:%M")
    plano = json.dumps({"fecha": fecha, "stock": stock}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    sal, iv = os.urandom(16), os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=ITERACIONES)
    llave = kdf.derive(leer_o_crear_clave().encode("utf-8"))
    cifrado = AESGCM(llave).encrypt(iv, plano, None)
    b64 = lambda b: base64.b64encode(b).decode("ascii")
    with open(os.path.join(CARPETA, "stock.json"), "w", encoding="utf-8") as f:
        json.dump({"sal": b64(sal), "iv": b64(iv), "iteraciones": ITERACIONES, "datos": b64(cifrado)}, f)
    print(f"stock.json (cifrado): {len(stock)} artículos con stock, LINCE del {fecha}")


if __name__ == "__main__":
    main()
