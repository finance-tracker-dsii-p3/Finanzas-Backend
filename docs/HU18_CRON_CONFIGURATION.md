# Configuración de Cron Job para Notificaciones - HU-18

## Descripción

Este documento explica cómo configurar el comando `check_notifications` para que se ejecute automáticamente en el servidor de producción. Este comando verifica y envía todas las notificaciones pendientes:

- Recordatorios personalizados
- Recordatorios de fin de mes (día 28)
- Recordatorios de facturas
- Alertas de SOAT

---

## Comando

```bash
python manage.py check_notifications
```

**Ubicación:** `Finanzas-Backend/notifications/management/commands/check_notifications.py`

---

## Configuración en Linux/Unix (Crontab)

### 1. Editar crontab

```bash
crontab -e
```

### 2. Agregar entrada

Ejecutar diariamente a las 9:00 AM:

```bash
0 9 * * * cd /ruta/completa/al/proyecto/Finanzas-Backend && /usr/bin/python3 manage.py check_notifications >> /var/log/notifications.log 2>&1
```

**Explicación:**
- `0 9 * * *` - Todos los días a las 9:00 AM
- `cd /ruta/completa/al/proyecto/Finanzas-Backend` - Cambiar al directorio del proyecto
- `/usr/bin/python3` - Ruta completa al Python (verificar con `which python3`)
- `manage.py check_notifications` - Comando a ejecutar
- `>> /var/log/notifications.log 2>&1` - Redirigir salida a archivo de log

### 3. Verificar ruta de Python

```bash
which python3
# o
which python
```

### 4. Verificar permisos

Asegurarse de que el usuario tiene permisos para:
- Ejecutar el script
- Escribir en el archivo de log
- Acceder a la base de datos

### 5. Probar manualmente

```bash
cd /ruta/completa/al/proyecto/Finanzas-Backend
python manage.py check_notifications --verbose
```

---

## Configuración en Windows (Task Scheduler)

### 1. Abrir Task Scheduler

- Presionar `Win + R`
- Escribir `taskschd.msc`
- Presionar Enter

### 2. Crear nueva tarea

1. Click en "Create Basic Task" o "Create Task"
2. Nombre: `Check Notifications`
3. Descripción: `Ejecuta verificación de notificaciones diariamente`

### 3. Configurar trigger

1. Trigger: Daily
2. Start date: Fecha actual
3. Time: 09:00 AM
4. Recur every: 1 days

### 4. Configurar acción

1. Action: Start a program
2. Program/script: `C:\ruta\a\python.exe` (o `python` si está en PATH)
3. Add arguments: `manage.py check_notifications`
4. Start in: `C:\ruta\completa\al\proyecto\Finanzas-Backend`

### 5. Configurar condiciones (opcional)

- ✅ Start the task only if the computer is on AC power (desmarcar si se ejecuta en servidor)
- ✅ Wake the computer to run this task (opcional)

### 6. Configurar configuración

- ✅ Allow task to be run on demand
- ✅ Run task as soon as possible after a scheduled start is missed
- ✅ If the task fails, restart every: 10 minutes (máximo 3 veces)

### 7. Ejecutar con PowerShell (alternativa)

Crear script `check_notifications.ps1`:

```powershell
Set-Location "C:\ruta\completa\al\proyecto\Finanzas-Backend"
python manage.py check_notifications --verbose
```

Programar con:

```powershell
schtasks /create /tn "Check Notifications" /tr "powershell.exe -File C:\ruta\check_notifications.ps1" /sc daily /st 09:00
```

---

## Configuración en Docker

### 1. Usar cron en contenedor

Crear archivo `crontab.txt`:

```
0 9 * * * cd /app && python manage.py check_notifications >> /var/log/notifications.log 2>&1
```

### 2. Dockerfile

```dockerfile
FROM python:3.11

# ... resto de configuración ...

# Instalar cron
RUN apt-get update && apt-get install -y cron

# Copiar crontab
COPY crontab.txt /etc/cron.d/check-notifications
RUN chmod 0644 /etc/cron.d/check-notifications
RUN crontab /etc/cron.d/check-notifications

# Crear directorio de logs
RUN mkdir -p /var/log

# Iniciar cron
CMD cron && python manage.py runserver 0.0.0.0:8000
```

### 3. Usar docker-compose con servicio separado

`docker-compose.yml`:

```yaml
services:
  web:
    # ... configuración del servidor web ...

  notifications:
    build: .
    command: python manage.py check_notifications
    volumes:
      - ./logs:/var/log
    environment:
      - DJANGO_SETTINGS_MODULE=finanzas_back.settings
    depends_on:
      - db
    restart: "no"  # No reiniciar automáticamente
```

Programar con cron en el host:

```bash
0 9 * * * docker-compose run --rm notifications
```

---

## Configuración en Cloud (Render, Heroku, etc.)

### Render

1. Crear nuevo **Cron Job**
2. Nombre: `Check Notifications`
3. Schedule: `0 9 * * *` (todos los días a las 9 AM)
4. Command: `python manage.py check_notifications`
5. Environment: Production

### Heroku

Usar Heroku Scheduler:

1. Instalar addon: `heroku addons:create scheduler:standard`
2. Configurar en dashboard:
   - Command: `python manage.py check_notifications`
   - Frequency: Daily at 9:00 AM UTC

### AWS Lambda + EventBridge

1. Crear función Lambda que ejecute el comando
2. Configurar EventBridge Rule:
   - Schedule: `cron(0 9 * * ? *)`
   - Target: Lambda function

---

## Monitoreo y Logs

### Verificar ejecución

```bash
# Ver últimas líneas del log
tail -f /var/log/notifications.log

# Ver ejecuciones recientes
grep "$(date +%Y-%m-%d)" /var/log/notifications.log
```

### Output esperado

```
============================================================
  Verificación de Notificaciones - 2025-01-20 09:00:00
============================================================

[1/4] Verificando recordatorios personalizados...
  ✓ 3 recordatorios personalizados procesados

[2/4] Verificando recordatorios de fin de mes...
  ✓ 0 recordatorios de fin de mes enviados

[3/4] Verificando facturas pendientes...
  ✓ Facturas verificadas: 5
    - Próximas a vencer: 2
    - Vencen hoy: 1
    - Atrasadas: 2

[4/4] Verificando SOATs pendientes...
  ✓ 2 alertas de SOAT creadas

============================================================
  Resumen Final
============================================================
  ✓ Total de notificaciones enviadas: 5

  Verificación completada exitosamente
============================================================
```

### Alertas de errores

Configurar alertas si el comando falla:

```bash
# En crontab, agregar notificación por email
0 9 * * * cd /ruta/proyecto && python manage.py check_notifications || echo "Error en check_notifications" | mail -s "Error Notificaciones" admin@example.com
```

---

## Troubleshooting

### Problema: Comando no se ejecuta

**Solución:**
1. Verificar permisos de ejecución: `chmod +x manage.py`
2. Verificar ruta de Python: `which python3`
3. Verificar logs del sistema: `journalctl -u cron` (Linux)
4. Probar manualmente: `python manage.py check_notifications --verbose`

### Problema: Error de base de datos

**Solución:**
1. Verificar variables de entorno (DATABASE_URL, etc.)
2. Verificar conexión: `python manage.py dbshell`
3. Verificar migraciones: `python manage.py migrate`

### Problema: Timezone incorrecto

**Solución:**
1. Configurar timezone del sistema: `timedatectl set-timezone America/Bogota`
2. Verificar en Django settings: `USE_TZ = True`
3. Verificar timezone de usuarios en base de datos

### Problema: Notificaciones no se envían

**Solución:**
1. Verificar preferencias de usuarios: `enable_*_reminders = True`
2. Verificar que hay datos (facturas, SOATs, etc.)
3. Ejecutar con `--verbose` para ver detalles
4. Verificar logs de aplicación

---

## Frecuencia recomendada

- **Producción:** Diariamente a las 9:00 AM
- **Desarrollo:** Manualmente cuando sea necesario
- **Testing:** Cada hora para pruebas rápidas

---

## Seguridad

1. ✅ Ejecutar con usuario con permisos mínimos necesarios
2. ✅ No exponer credenciales en logs
3. ✅ Rotar logs periódicamente
4. ✅ Monitorear ejecuciones fallidas
5. ✅ Limitar acceso al archivo de log

---

## Referencias

- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [Crontab Guru](https://crontab.guru/) - Generador de expresiones cron
- [Task Scheduler Documentation](https://docs.microsoft.com/en-us/windows/desktop/taskschd/task-scheduler-start-page)

---

**Última actualización:** Enero 2025
**Mantenido por:** Equipo de Desarrollo
