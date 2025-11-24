"""
Script para probar específicamente el serializer de analytics
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_back.settings')
django.setup()

from datetime import datetime, date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from analytics.services import FinancialAnalyticsService
from analytics.serializers import ExpensesCategoryChartSerializer, AnalyticsDashboardSerializer

User = get_user_model()

def test_serializer():
    """Probar el serializer específicamente"""
    
    print("🧪 PROBANDO SERIALIZERS DE ANALYTICS")
    print("=" * 50)
    
    # Obtener usuario con datos
    user = User.objects.filter(username='usuarioPrueba').first()
    if not user:
        print("❌ Usuario 'usuarioPrueba' no encontrado")
        return
    
    print(f"👤 Usuario: {user.username} (ID: {user.id})")
    
    # Período del mes actual
    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = today
    
    print(f"📅 Período: {start_date} a {end_date}")
    
    try:
        # 1. Probar servicio get_expenses_by_category
        print(f"\n1️⃣ PROBANDO SERVICIO get_expenses_by_category...")
        
        expenses_data = FinancialAnalyticsService.get_expenses_by_category(
            user=user,
            start_date=start_date,
            end_date=end_date,
            mode='total',
            others_threshold=0.05
        )
        
        print(f"✅ Servicio OK - Datos obtenidos:")
        print(f"   - Claves: {list(expenses_data.keys())}")
        print(f"   - categories_count: {expenses_data.get('categories_count')} (tipo: {type(expenses_data.get('categories_count'))})")
        
        # 2. Probar serializer ExpensesCategoryChartSerializer directamente
        print(f"\n2️⃣ PROBANDO ExpensesCategoryChartSerializer...")
        
        try:
            serializer = ExpensesCategoryChartSerializer(expenses_data)
            print(f"✅ Serializer OK - Datos serializados correctamente")
            print(f"   - Datos serializados disponibles: {list(serializer.data.keys())}")
            
            # Mostrar datos específicos
            print(f"\n📊 DATOS SERIALIZADOS:")
            for key, value in serializer.data.items():
                if isinstance(value, (list, dict)):
                    print(f"   {key}: {type(value)} (elementos: {len(value) if isinstance(value, list) else 'dict'})")
                else:
                    print(f"   {key}: {value} (tipo: {type(value)})")
                    
        except Exception as e:
            print(f"❌ Error en ExpensesCategoryChartSerializer: {e}")
            print(f"📋 Datos que se intentaron serializar:")
            for key, value in expenses_data.items():
                print(f"   {key}: {type(value)} = {value}")
            return
        
        # 3. Probar otros servicios
        print(f"\n3️⃣ PROBANDO OTROS SERVICIOS...")
        
        indicators = FinancialAnalyticsService.get_period_indicators(
            user, start_date, end_date, 'total'
        )
        print(f"✅ Indicadores OK - Claves: {list(indicators.keys())}")
        
        daily_flow_chart = FinancialAnalyticsService.get_daily_flow_chart(
            user, start_date, end_date, 'total'
        )
        print(f"✅ Daily flow OK - Claves: {list(daily_flow_chart.keys())}")
        
        # 4. Probar dashboard completo
        print(f"\n4️⃣ PROBANDO DASHBOARD COMPLETO...")
        
        dashboard_data = {
            'indicators': indicators,
            'expenses_chart': expenses_data,
            'daily_flow_chart': daily_flow_chart,
            'metadata': {
                'generated_at': date.today().isoformat(),
                'user_id': user.id,
                'period_requested': 'current_month',
                'mode_used': 'total',
                'others_threshold': 0.05
            }
        }
        
        print(f"🔍 Dashboard data preparada - Claves: {list(dashboard_data.keys())}")
        
        try:
            dashboard_serializer = AnalyticsDashboardSerializer(dashboard_data)
            print(f"✅ Dashboard Serializer OK!")
            print(f"📊 Dashboard serializado correctamente")
            
        except Exception as e:
            print(f"❌ Error en AnalyticsDashboardSerializer: {e}")
            
            # Debug más específico
            print(f"\n🔍 DEBUGGING DASHBOARD SERIALIZER:")
            
            # Probar cada componente por separado
            try:
                from analytics.serializers import PeriodIndicatorsSerializer
                ind_serializer = PeriodIndicatorsSerializer(indicators)
                print(f"   ✅ PeriodIndicatorsSerializer OK")
            except Exception as ie:
                print(f"   ❌ PeriodIndicatorsSerializer Error: {ie}")
                
            try:
                exp_serializer = ExpensesCategoryChartSerializer(expenses_data)
                print(f"   ✅ ExpensesCategoryChartSerializer OK")
            except Exception as ee:
                print(f"   ❌ ExpensesCategoryChartSerializer Error: {ee}")
                
            try:
                from analytics.serializers import DailyFlowChartSerializer
                flow_serializer = DailyFlowChartSerializer(daily_flow_chart)
                print(f"   ✅ DailyFlowChartSerializer OK")
            except Exception as fe:
                print(f"   ❌ DailyFlowChartSerializer Error: {fe}")
            
            return
            
        print(f"\n🎉 ¡TODOS LOS TESTS PASARON!")
        print(f"✅ El problema debe estar en otro lado, no en los serializers")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serializer()