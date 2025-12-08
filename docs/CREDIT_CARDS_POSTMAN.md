# HU-16 Tarjetas en cuotas – Guía Postman

Esta guía resume cómo probar los nuevos endpoints de planes de cuotas de tarjeta.

## Autenticación
Incluye el header `Authorization: Token <token>` para todas las peticiones.

## 1. Crear plan de cuotas
`POST /api/credit-cards/plans/`

Body (JSON):
```json
{
  "credit_card_account_id": 5,
  "purchase_transaction_id": 120,
  "financing_category_id": 18,
  "description": "Televisor",
  "number_of_installments": 12,
  "interest_rate": "2.0",
  "start_date": "2025-01-15"
}
```
Respuesta esperada `201`:
```json
{
  "status": "success",
  "data": { "plan_id": 33 }
}
```

## 2. Listar planes
`GET /api/credit-cards/plans/`

Respuesta `200` con `results` y cuotas anidadas (`payments`).

## 3. Ver calendario de un plan
`GET /api/credit-cards/plans/{plan_id}/schedule/`

Respuesta `200`:
```json
{
  "status": "success",
  "data": { "schedule": [ {"installment_number":1,"due_date":"2025-01-15","installment_amount":110000,"principal_amount":100000,"interest_amount":10000,"remaining_principal":1100000} ] }
}
```

## 4. Registrar un pago de cuota
`POST /api/credit-cards/plans/{plan_id}/payments/`

Body:
```json
{
  "installment_number": 1,
  "payment_date": "2025-02-15",
  "source_account_id": 3,
  "notes": "Pago mensual"
}
```
Respuesta `201` incluye ids de transacciones creadas (transferencia capital, gasto interés).

## 5. Resumen mensual
`GET /api/credit-cards/plans/monthly-summary/?year=2025&month=2`

Devuelve totales de cuotas del mes (pendientes/pagadas y monto total en centavos).

## 6. Próximos pagos
`GET /api/credit-cards/plans/upcoming-payments/?days=30`

Lista cuotas vencidas o próximas en los siguientes días.

### Notas de validación
- La compra debe ser un gasto con `origin_account` tarjeta de crédito.
- Los intereses se registran en la categoría de gasto indicada (Financiamiento).
- Los pagos se registran como transferencia (capital) + gasto de interés para evitar doble conteo.
