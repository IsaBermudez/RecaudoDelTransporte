# Rediseño del proceso nocturno de recaudo del SITVM

**Integrantes:** 
- Isabella Bermudez Arboleda
- Sofia Villa Muñoz
- Carolina Uribe Builes
- Erian Jose Serna

**Caso asignado:** Caso 1 – Recaudo del transporte (Sistema Integrado de Transporte del Valle Metropolitano, SITVM)
**Operación desarrollada en esta entrega (Laboratorio 4):** operación 4, liquidación del tope tarifario (programación dinámica).

> Las demás operaciones del caso (deduplicación, ordenamiento y franjas de congestión) y el proceso completo se dejan como **Pendiente para la entrega del 23 de noviembre**.

---

## 1. Análisis del problema

### Operación 4: liquidación del tope tarifario

El objetivo es garantizar que ningún usuario con tarjeta personalizada pague, en el mes, más que la combinación más barata de pasajes y pases que cubra todos sus viajes. La diferencia se devuelve como saldo en la tarjeta. Hoy el sistema explora todas las combinaciones de pases, pero no termina para las tarjetas que viajan muchos días. A esas tarjetas se les aplica una regla simplificada que, en algunos meses, cobra más que el mínimo.

### Entradas

- Una lista de enteros con los viajes de la tarjeta en cada día calendario del mes (el cero indica un día sin viajes). El periodo varía entre 28 y 31 días.
- El monto que se le cobró realmente a la tarjeta durante el mes, en pesos (solo para calcular la devolución).
- Tarifas del perfil general:

| Producto | Valor | Cobertura |
|---|---|---|
| Pasaje sencillo | $3.900 | un viaje |
| Pase diario | $9.500 | un día calendario |
| Pase semanal | $36.000 | 7 días consecutivos |
| Pase mensual | $135.000 | 30 días consecutivos |

### Salida

- El costo mínimo, en pesos, de cubrir todos los viajes del periodo.
- La devolución al usuario: lo cobrado menos el costo mínimo, sin valores negativos.

### Restricciones

- Todos los viajes deben quedar cubiertos y el costo debe ser exactamente el de la combinación más barata: ni un peso de menos para el usuario ni un peso de más para el sistema.
- Un pase puede extenderse más allá del último día del periodo sin cobro adicional.
- Los días sin viajes no generan costo.
- Las tarifas corresponden al perfil del usuario (aquí, perfil general).
- El archivo original de validaciones no se modifica, para conservar la trazabilidad ante reclamaciones.
- Volumen real: cerca de 950.000 tarjetas por cierre de mes, en la ventana de 4 horas (00:00 a 04:00), en un servidor de unos 500 W.

### Supuestos

1. El pase diario cubre un día calendario, el semanal siete días consecutivos y el mensual treinta, contados desde el día en que empiezan.
2. Un pase siempre se compra el primer día aún no cubierto que tenga viajes. Los días sin viajes no generan cobro y no impiden que un pase vigente cubra días posteriores. Esta suposición se verificó con una fuerza bruta que prueba pases en cualquier día de inicio (ver sección 4).
3. La lista puede ser de un mes de 28, 29, 30 o 31 días. En un mes de 31 días, un pase mensual no cubre el último día, que se paga aparte (por ejemplo, 31 días con 3 viajes diarios cuestan $135.000 + $9.500 = $144.500).
4. Se admiten cero viajes por día; no se admiten cantidades negativas (la implementación lanza `ValueError`).
5. **Interpretación de la regla actual.** El caso dice que cada día se cobra lo más barato entre pasajes y pase diario, y que se cobra el pase semanal o mensual si la suma ya lo supera. Se interpretó así: desde el primer día con viajes, los días se agrupan en bloques fijos de 7 días, y si su cobro diario supera el pase semanal, se cobra este; igual con bloques fijos de 30 días y el pase mensual. La regla nunca reconsidera en qué día conviene empezar un pase.

---

## 2. Diseño de la solución

### Por qué programación dinámica

La decisión de comprar un pase semanal o mensual afecta el costo de varios días a la vez, así que elegir lo más barato para cada día por separado no siempre da el mínimo.

- **Subestructura óptima:** después de elegir un producto para cubrir los primeros días que quedan, el costo del resto del mes también debe ser el mínimo posible para esos días restantes.
- **Subproblemas traslapados:** distintas combinaciones de productos llegan a calcular el costo mínimo desde el mismo día. Por ejemplo, "pasaje el día 1 y pasaje el día 2" y "pase diario el día 1 y pasaje el día 2" terminan ambos preguntando por el día 3. Guardar el resultado de cada día evita repetirlo.

### Ejemplo resuelto a mano

Tarjeta con siete días de viajes:

| Día | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| Viajes | 3 | 3 | 3 | 0 | 2 | 0 | 3 |

Costo diario más barato: con 3 viajes, el pase diario ($9.500) es mejor que tres pasajes ($11.700); con 2 viajes, dos pasajes ($7.800) son mejores. Pagar día por día cuesta 4 × $9.500 + $7.800 = $45.800. El pase semanal cubre los siete días por $36.000.

Para confirmar que $36.000 es el mínimo se calcula `C(t)` de atrás hacia adelante:

| Día `t` | Viajes | Alternativas | `C(t)` |
|---|---|---|---|
| 8 | — | caso base | $0 |
| 7 | 3 | 9.500 + 0 · 36.000 + 0 | $9.500 |
| 6 | 0 | `C(7)` | $9.500 |
| 5 | 2 | 7.800 + 9.500 = 17.300 · 36.000 + 0 | $17.300 |
| 4 | 0 | `C(5)` | $17.300 |
| 3 | 3 | 9.500 + 17.300 = 26.800 · 36.000 + 0 | $26.800 |
| 2 | 3 | 9.500 + 26.800 = 36.300 · 36.000 + 0 | $36.000 |
| 1 | 3 | 9.500 + 36.000 = 45.500 · 36.000 + 0 | **$36.000** |

Hasta el día 3 conviene pagar solo ese día (26.800 contra 36.000). En el día 2 pagar día por día ya cuesta 36.300 y el pase semanal, 36.000, gana; en el día 1 también gana y cubre todo el periodo. El resultado (36.000) está verificado en `pruebas.py`.

### Recurrencia

Sea `d` el número de días del periodo (numerados de 1 a `d`) y `v(t)` los viajes del día `t`. `C(t)` es el costo mínimo de cubrir los viajes desde el día `t` hasta el día `d`.

- **Caso base:** `C(d+1) = 0` (no queda nada por cubrir).
- Si `v(t) = 0`: `C(t) = C(t+1)` (un día sin viajes no cuesta nada).
- Si `v(t) > 0`:

```
C(t) = min(  min(3900·v(t), 9500) + C(t+1),      # pasajes o pase diario, solo hoy
             36000 + C(min(t+7,  d+1)),           # pase semanal desde hoy
             135000 + C(min(t+30, d+1)) )         # pase mensual desde hoy
```

Cada término explica una decisión: la primera cubre solo el día `t` con lo más barato entre pasajes y pase diario; la segunda compra un pase semanal que cubre `t..t+6` y salta al primer día no cubierto; la tercera hace lo mismo con el pase mensual. `min(·, d+1)` impide pasarse del final del periodo (el pase "sobrante" no cobra de más).

**Orden de llenado:** la tabla se llena de atrás hacia adelante (`t = d, d-1, …, 1`), porque `C(t)` depende solo de días posteriores (`t+1`, `t+7`, `t+30`), que ya están calculados. La respuesta es `C(1)`.

La devolución se calcula como `max(0, cobrado − C(1))`.

---

## 3. Implementación

Código en [`src/tope_tarifario/`](src/tope_tarifario/):

| Módulo | Contenido |
|---|---|
| [`estrategia.py`](src/tope_tarifario/estrategia.py) | `costo_minimo` (programación dinámica con tabulación), `liquidar_tope`, `costo_minimo_contado` (con contador de celdas) |
| [`exhaustivo.py`](src/tope_tarifario/exhaustivo.py) | `costo_exhaustivo` (recursión sin memoria), `costo_exhaustivo_contado`, `costo_fuerza_bruta` (prueba todos los subconjuntos de pases, solo para 7 días o menos) |
| [`regla_actual.py`](src/tope_tarifario/regla_actual.py) | `costo_regla_actual` (regla simplificada del sistema) y su versión con contador |
| [`pruebas.py`](src/tope_tarifario/pruebas.py) | Pruebas con `assert` |

Decisiones de implementación relevantes:

- Todo está escrito a mano, sin bibliotecas de optimización. Las funciones llevan type hints y docstrings Google-style y cumplen PEP 8.
- La DP usa tabulación (un arreglo de `d+1` posiciones) y no recursión, para evitar el límite de recursión de Python en periodos largos.
- Las versiones `_contado` son copias de las funciones con un contador propio. Se mantienen aparte para que el contador no altere los tiempos medidos.
- Se agregó `costo_fuerza_bruta` porque `costo_exhaustivo` usa la misma recurrencia sin memoria: verifica el código pero no el modelo. La fuerza bruta no supone que un pase empiece en un día con viajes, así que valida el supuesto 2.
- Entradas con viajes negativos lanzan `ValueError`.

---