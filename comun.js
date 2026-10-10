// Funciones compartidas por index.html (escaneo) y comparar.html (comparación con LINCE).
// Usa los datos de articulos.js (generado por actualizar_lista.py).

const ARTICULOS = new Map();
for(const k in (window.ARTICULOS_DATA || {})) ARTICULOS.set(String(k).toUpperCase(), window.ARTICULOS_DATA[k]);
const COLORES = window.COLORES_DATA || {};
const CURVAS = window.CURVAS_DATA || {};
const SIN_COLOR = new Set((window.SIN_COLOR_DATA || []).map(s => String(s).toUpperCase()));
const HAY_CATALOGO = ARTICULOS.size > 0;

function infoArticulo(articulo){
  const a = ARTICULOS.get(String(articulo || "").toUpperCase());
  return { desc: a ? (a[0] || "") : "", precio: (a && a[1] != null) ? a[1] : null, grupo: a ? (a[2] || "") : "" };
}

function nombreColor(cod){
  cod = String(cod || "").toUpperCase();
  if(!cod) return "";
  return COLORES[cod] || "";
}

// Código de barra de LINCE: ARTICULO % COLOR(2) TALLE.
// Los artículos sin color traen solo el talle después del %.
function leerCodigo(codigoCompleto){
  const cod = String(codigoCompleto || "").trim();
  let articulo = cod, color = "", talle = "";
  const i = cod.indexOf("%");
  if(i > 0){
    articulo = cod.slice(0, i).trim();
    const resto = cod.slice(i + 1);
    if(SIN_COLOR.has(articulo.toUpperCase())){
      talle = resto.trim();
    } else {
      color = resto.slice(0, 2).trim();
      talle = resto.slice(2).trim();
    }
  }
  return { articulo: articulo.toUpperCase(), color: color.toUpperCase(), talle: talle.toUpperCase() };
}

// Orden de los talles: primero letras (S, M, L...), después números, después el resto.
const ORDEN_LETRAS = ["XXS","XS","S","M","L","XL","XXL","2XL","XXXL","3XL","4XL","5XL","6XL","7XL","8XL"];
function compararTalles(a, b){
  const k = t => {
    t = String(t || "").toUpperCase();
    if(t === "") return [3, 0, ""];
    const i = ORDEN_LETRAS.indexOf(t);
    if(i >= 0) return [0, i, ""];
    if(/^\d+([.,]\d+)?$/.test(t)) return [1, parseFloat(t.replace(",", ".")), ""];
    return [2, 0, t];
  };
  const x = k(a), y = k(b);
  return x[0] - y[0] || x[1] - y[1] || x[2].localeCompare(y[2]);
}
function nombreColumnaTalle(t){ return t === "" ? "Sin talle" : t; }

const compararArticulos = (a, b) => String(a).localeCompare(String(b), "es", { numeric: true });

// Agrupa renglones {articulo, color, talle, cantidad} por artículo+color, con un total por talle.
function agruparPorTalle(renglones){
  const grupos = new Map(), talles = new Set();
  for(const r of renglones){
    if(!r.cantidad) continue;
    const clave = r.articulo + "|" + r.color;
    if(!grupos.has(clave)) grupos.set(clave, { articulo: r.articulo, color: r.color, porTalle: {} });
    const g = grupos.get(clave);
    g.porTalle[r.talle] = (g.porTalle[r.talle] || 0) + r.cantidad;
    talles.add(r.talle);
  }
  const lista = [...grupos.values()].sort((a, b) => compararArticulos(a.articulo, b.articulo) || a.color.localeCompare(b.color));
  return { lista, talles: [...talles].sort(compararTalles) };
}

// Hoja "Planilla": una fila por artículo+color, una columna por talle.
function hojaPlanilla(renglones, titulo){
  const { lista, talles } = agruparPorTalle(renglones);
  const enc = ["Artículo", "Descripción", "Color", "Nombre color", ...talles.map(nombreColumnaTalle), "Total", "Precio venta", "Valor venta"];
  const filas = [[titulo], [], enc];
  const totTalle = talles.map(() => 0);
  let totUnid = 0, totValor = 0;
  for(const g of lista){
    const info = infoArticulo(g.articulo);
    let total = 0;
    const celdas = talles.map((t, i) => {
      const c = g.porTalle[t] || 0;
      total += c; totTalle[i] += c;
      return c || "";
    });
    const valor = info.precio != null ? info.precio * total : "";
    totUnid += total; if(valor) totValor += valor;
    filas.push([g.articulo, info.desc, g.color, nombreColor(g.color), ...celdas, total, info.precio != null ? info.precio : "", valor]);
  }
  filas.push([]);
  filas.push(["TOTAL", "", "", "", ...totTalle.map(c => c || ""), totUnid, "", totValor || ""]);
  const hoja = XLSX.utils.aoa_to_sheet(filas);
  hoja["!cols"] = [{wch:13},{wch:30},{wch:6},{wch:16}, ...talles.map(() => ({wch:6})), {wch:7},{wch:12},{wch:13}];
  return hoja;
}

function formatoPrecio(n){
  if(n === null || n === undefined || n === "" || isNaN(n)) return "";
  return "$" + Number(n).toLocaleString("es-AR");
}

function esc(s){ return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

function nombreArchivo(s){ return String(s || "").replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, "_").slice(0, 40); }
