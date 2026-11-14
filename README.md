# Rediseño del proceso nocturno de recaudo del SITVM

**Integrantes:** 
- Isabella Bermudez Arboleda
- Sofia Villa Muñoz
- Carolina Uribe Builes
- Erian Jose Serna

**Caso asignado:** Caso 1 – Recaudo del transporte (Sistema Integrado de Transporte del Valle Metropolitano, SITVM)
**Operación desarrollada en esta entrega (Laboratorio 4):** operación 4, liquidación del tope tarifario (programación dinámica).

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
5. **Interpretación de la regla actual.** El caso dice que cada día se cobra lo más barato entre pasajes y pase diario, y que se aplica el pase semanal o mensual si la suma ya lo supera. Se interpretó así: desde el primer día con viajes, los días se agrupan en bloques fijos de 7 días; si el cobro diario acumulado de un bloque supera el pase semanal, ese bloque se cobra al precio del pase semanal. Los bloques semanales se agrupan a su vez en bloques fijos de 30 días; si su suma supera el pase mensual, se cobra el mensual. La regla decide por bloques fijos y nunca reconsidera en qué día conviene empezar un pase. Esta interpretación debe confirmarse con la organización si existe una regla operativa más precisa.

---
