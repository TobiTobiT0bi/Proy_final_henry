# Test Contracts Dataset

Esta carpeta contiene los conjuntos de imágenes de documentos legales utilizados para probar y validar el pipeline de extracción de enmiendas contractuales.

## Pares de Prueba Disponibles

### Par 1: Licencia de Software (Caso Estándar)
- **Original:** `documento_1__contrato.jpg` (Contrato de Licencia de Software entre TechNova S.A. y DataBridge Soluciones S.R.L.)
- **Modificado:** `documento_1__enmienda.jpg` (Enmienda con modificaciones en plazo a 24 meses, tarifa a USD 15.000 y notificación de terminación a 60 días)

### Par 2: Servicios de Consultoría (Caso Variant)
- **Original:** `documento_2__contrato.jpg` (Contrato de Servicios de Consultoría entre Orion Consulting Group y GreenWave Energía S.A.)
- **Modificado:** `documento_2__enmienda.jpg` (Enmienda con aumento de duración a 9 meses, tarifa a USD 9.500 y entregables quincenales)

### Par 3: Servicio SaaS (Caso Boundary)
- **Original:** `documento_3__contrato.jpg` (Contrato de Servicio SaaS entre CloudMetrics Ltd. y RetailPulse S.A.)
- **Modificado:** `documento_3__enmienda.jpg` (Versión actualizada con ajuste de tarifa a USD 1.250, disponibilidad de servicio al 99.9% y soporte mediante tickets)

## Propósito
Estos documentos abarcan distintos tipos de contratos comerciales, estructuras visuales y tipos de cambios (precios, plazos, condiciones operativas), lo que permite evaluar la capacidad de extracción y generalización del modelo GPT-4o Vision.