# 📦 Control de Stock

App web para escanear códigos de barra con la cámara del celular, contar unidades
y exportar todo a Excel. No necesita instalar nada: se abre desde el navegador.

Los datos se guardan en el propio celular o computadora (en el navegador). No se
suben a internet.

## Cómo usarla

1. Abrí el enlace de la app en el celular (Chrome o Safari).
2. Tocá **▶ Iniciar cámara** y apuntá al código de barra. Cada lectura suma 1 unidad.
   La app muestra **artículo, color, talle y precio de venta**.
3. También podés escribir el código a mano y tocar **Agregar**.
4. Con los botones **−** y **+** ajustás la cantidad. La **✕** borra ese renglón.
5. Cuando terminaste, tocá **⬇ Exportar a Excel** para bajar la planilla
   (columnas: Artículo, Descripción, Color, Talle, Precio, Cantidad, Subtotal…).
6. **🗑 Vaciar todo** borra la lista para empezar de nuevo.

## Lista de artículos (`articulos.js`)

Las descripciones y precios salen de `articulos.js`, generado desde el export
de **LINCE** (`ARTICULO.XLS`). El código de barra se interpreta así:
`ARTÍCULO` + `%` + `COLOR` (2 caracteres) + `TALLE`.

Para **actualizar precios o artículos**: volvé a exportar `ARTICULO.XLS` desde
LINCE y regenerá `articulos.js` (columnas usadas: código, descripción, precio de
lista). Después `git commit` + `git push` y GitHub Pages se actualiza solo.

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
