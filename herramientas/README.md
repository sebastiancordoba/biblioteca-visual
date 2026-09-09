# Herramientas

Scripts para buscar, descargar y publicar arte en la colección. Se ejecutan **desde la raíz
`Pinturas/`**, no desde aquí. Usan `curl` por debajo porque el Python del sistema (3.9) no trae
certificados CA y `urllib` falla con `CERTIFICATE_VERIFY_FAILED`.

| Archivo | Qué hace |
|---|---|
| `commons.py` | Busca en Wikimedia Commons. Ordena por calidad de fuente y megapíxeles, y clasifica cada candidato como `institucional`, `foto de sala` o `?`. |
| `download.py` | Baja los originales a resolución completa desde un manifiesto TSV. Verifica el código HTTP, respeta el `retry-after` del límite de tasa y comprueba las dimensiones con `sips`. |
| `data_<libro>.py` | **Las fichas de las obras.** Aquí se escribe una obra nueva. |
| `data_lote3.py` | Fichas añadidas por lotes posteriores; se engancha a los módulos anteriores. |
| `inject.py` | Vuelca las fichas en `index.html`. Idempotente. |
| `readme.py` | Regenera `README.md` de Gilgamesh e Ilíada. |
| `readme_genesis.js` | Regenera `README.md` del Génesis desde los datos ya inyectados. |
| `verificar.js` | Comprueba rutas rotas, alineación de índices e imágenes por debajo de 1500 px. |
| `probar_render.js` | Ejecuta el renderizador con un DOM simulado y revisa el HTML producido. |
| `*.tsv` | Manifiestos de descarga: `<ruta destino>` TAB `<File:Título en Commons.jpg>`. Reejecutables: lo ya descargado se salta. |

## Uso típico

```sh
python3 herramientas/commons.py search "Rubens Judgement of Paris" 8      # pintura
python3 herramientas/commons.py search "Lamassu Khorsabad" 8 objeto        # escultura
python3 herramientas/download.py herramientas/iliada.tsv
python3 herramientas/inject.py && python3 herramientas/readme.py
node herramientas/verificar.js && node herramientas/probar_render.js
```

**Uno a la vez.** Wikimedia limita la tasa con dureza; en paralelo devuelve 429 y búsquedas vacías.
Ver `../CLAUDE.md` para el detalle.
