# 🚀 GUÍA DE DESPLIEGUE CONTINUO - FINANZAS BACKEND

## 🎯 **CONFIGURACIÓN DE SECRETOS EN GITHUB**

Para que el **despliegue continuo** funcione perfectamente, necesitas configurar estos secretos en tu repositorio de GitHub:

### **Paso 1: Ir a Settings > Secrets and Variables > Actions**

### **Paso 2: Agregar estos Repository Secrets:**

```bash
# 🔑 SECRETOS OBLIGATORIOS:
RENDER_API_KEY           # Tu API key de Render
RENDER_SERVICE_ID        # ID del servicio principal (producción)
RENDER_SERVICE_URL       # URL completa de tu servicio: https://tu-app.onrender.com

# 🎭 SECRETOS OPCIONALES (para staging):
RENDER_SERVICE_ID_STAGING    # ID del servicio de staging (si tienes uno separado)
RENDER_SERVICE_URL_STAGING   # URL del servicio de staging

# 🔧 SECRETOS ADICIONALES (si usas):
RENDER_SERVICE_ID_PROD       # Alias para producción (opcional)
RENDER_SERVICE_URL_PROD      # URL de producción (opcional)
```

---

## 🏗️ **CÓMO OBTENER TUS VALORES DE RENDER**

### **1. API Key:**
```bash
1. Ve a https://dashboard.render.com/account/api-keys
2. Crea una nueva API key
3. Cópiala y úsala como RENDER_API_KEY
```

### **2. Service ID:**
```bash
1. Ve a tu servicio en Render Dashboard
2. En la URL verás algo como: https://dashboard.render.com/web/srv-xxxxxxxxxxxxx
3. El Service ID es la parte: srv-xxxxxxxxxxxxx
```

### **3. Service URL:**
```bash
1. En tu servicio de Render, ve a la pestaña "Settings"
2. Copia la URL completa, ejemplo: https://finanzas-backend-abc123.onrender.com
```

---

## 🔄 **FLUJO DE DESPLIEGUE AUTOMÁTICO**

### **Branches y Triggers:**

1. **🚀 PRODUCCIÓN (main):**
   - Push a `main` → Ejecuta tests → Despliega a producción
   - Solo si todos los tests pasan ✅

2. **🎭 STAGING (develop):**
   - Push a `develop` → Tests rápidos → Despliega a staging
   - Para pruebas y testing

3. **🔍 PULL REQUESTS:**
   - PR hacia `main` → Ejecuta tests completos
   - Si se mergea → Despliega automáticamente

---

## 📋 **WORKFLOWS CREADOS**

### **1. `.github/workflows/ci.yml`**
- ✅ Ejecuta tests
- ✅ Verifica código
- ✅ Runs en Python 3.13

### **2. `.github/workflows/deploy.yml`** 
- ✅ Despliegue a producción
- ✅ Health checks avanzados
- ✅ Rollback automático en fallo
- ✅ Notificaciones de estado

### **3. `.github/workflows/staging-deploy.yml`**
- ✅ Despliegue a staging/develop
- ✅ Tests rápidos
- ✅ Comentarios en PRs

---

## 🎯 **FUNCIONES IMPLEMENTADAS**

### **✅ Health Checks Avanzados:**
```bash
- Verificación de base de datos
- Tests de conectividad
- Reintentos automáticos
- Timeouts configurables
```

### **✅ Endpoints Nuevos:**
```bash
GET /              # Información básica de la API
GET /health/       # Status detallado del sistema
GET /api/          # Root de la API
```

### **✅ Build Mejorado:**
```bash
- Verificación de paquetes
- Check de configuración Django
- Migraciones con verbosidad
- Usuario admin opcional
```

### **✅ Configuración Render Optimizada:**
```bash
- Gunicorn con 3 workers
- Timeout de 120 segundos
- Health check path configurado
- Auto-deploy habilitado
```

---

## 🚀 **COMANDOS PARA EMPEZAR**

### **1. Configurar secretos (manual en GitHub):**
Ve a: `https://github.com/TU_USUARIO/TU_REPO/settings/secrets/actions`

### **2. Test local del build:**
```bash
# En tu directorio local:
chmod +x build.sh
./build.sh
```

### **3. Test del health check:**
```bash
python manage.py runserver
curl http://localhost:8000/health/
```

### **4. Push para activar CD:**
```bash
git add .
git commit -m "🚀 Activate continuous deployment"
git push origin main
```

---

## 🔧 **TROUBLESHOOTING**

### **❌ Si el deployment falla:**

1. **Check secretos:**
   ```bash
   - Verifica que RENDER_API_KEY esté configurado
   - Verifica que RENDER_SERVICE_ID sea correcto
   ```

2. **Check logs en GitHub Actions:**
   ```bash
   - Ve a la pestaña "Actions" en tu repo
   - Click en el workflow fallido
   - Revisa los logs detallados
   ```

3. **Check logs en Render:**
   ```bash
   - Ve a tu servicio en Render Dashboard
   - Click en "Logs" para ver errores del deployment
   ```

### **❌ Si los health checks fallan:**
```bash
- Verifica que /health/ endpoint esté funcionando localmente
- Check que la base de datos esté accesible
- Verifica las variables de entorno en Render
```

---

## 🎉 **RESULTADO FINAL**

Con esta configuración tendrás:

- ✅ **Despliegue automático** en cada push a main
- ✅ **Tests automáticos** antes de cada deploy
- ✅ **Staging environment** para pruebas
- ✅ **Health checks** robustos
- ✅ **Rollback automático** si algo falla
- ✅ **Notificaciones** de estado
- ✅ **Multi-environment** support

**¡Tu aplicación se desplegará automáticamente y de forma segura! 🚀**