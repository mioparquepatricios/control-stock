# 📦 Control de Stock

App web para escanear códigos de barra con la cámara del celular, contar unidades
y exportar todo a Excel. No necesita instalar nada: se abre desde el navegador.

Los datos se guardan en el propio celular o computadora (en el navegador). No se
suben a internet.

## Cómo usarla

1. Abrí el enlace de la app en el celular (Chrome o Safari).
2. Tocá **➕ Empezar lote nuevo** y ponele un nombre (una pared, un mueble, el depósito…).
3. Tocá **▶ Iniciar cámara** y apuntá al código de barra. Cada lectura suma 1 unidad.
   La app muestra **artículo, color (con nombre), talle y precio de venta**.
4. También podés escribir el código a mano y tocar **Agregar**.
5. Con los botones **−** y **+** ajustás la cantidad. La **✕** borra ese renglón.
6. Al terminar ese sector tocá **✔ Cerrar lote**: se baja un Excel con
   - hoja **Planilla**: una fila por artículo y color, una columna por talle, total y valor;
   - hoja **Detalle**: un renglón por código (la usa la comparación).
7. En **📋 Lotes** podés volver a bajar la planilla, reabrir o borrar un lote, y bajar
   una planilla con **todos los lotes cerrados** juntos.

## Comparar con LINCE (`comparar.html`)

Botón **📊 Comparar con el stock de LINCE** (al final de la lista de lotes). Conviene usarlo
en la compu del local:

1. Elegí el archivo `comb.dbf` de `C:\linceV3\INV2013\DBF` (stock por artículo, color y talle).
2. Elegí la o las planillas que bajaste del escáner.
3. Elegí si comparar solo los artículos contados o todo el stock, y tocá **Comparar**.
4. **⬇ Bajar la comparación en Excel**: hoja *Diferencias por talle* (LINCE / Contado /
   Diferencia), *Lista completa* (con estado OK / FALTA / SOBRA) y *Contado*.

Los archivos se leen en el navegador: **el stock no se sube a internet**.

## Lista de artículos (`articulos.js`)

Descripciones, precios, nombres de colores y curvas de talle salen de `articulos.js`,
generado desde los DBF de **LINCE** (`art.dbf`, `col.dbf`, `mat.dbf`, `comb.dbf`) con:

    python actualizar_lista.py [carpeta_de_los_dbf]

(por defecto lee `C:\linceV3\INV2013\DBF`). `articulos.js` **no** lleva cantidades de stock.
Después `git commit` + `git push` y GitHub Pages se actualiza solo.

El código de barra se interpreta así: `ARTÍCULO` + `%` + `COLOR` (2 caracteres) + `TALLE`.
Los artículos que en LINCE no tienen color traen solo `ARTÍCULO` + `%` + `TALLE`.

> La cámara solo funciona si la página se abre por **https** (como en GitHub Pages)
> o en `localhost`.

## Publicarla con GitHub Pages (gratis)

1. En GitHub, entrá al repositorio → **Settings** → **Pages**.
2. En **Source** elegí la rama `main` y la carpeta `/ (root)`. Guardá.
3. Esperá 1–2 minutos. GitHub muestra la dirección pública, algo como
   `https://TU-USUARIO.github.io/control-stock/`.
4. Abrí esa dirección en el celular y agregala a la pantalla de inicio.

## Probarla en la computadora

Abrí `index.html` con doble clic. La lista y la exportación a Excel funcionan;
la cámara puede pedir https.
