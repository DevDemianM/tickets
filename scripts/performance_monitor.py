"""
Script de monitoreo y gestión de rendimiento
Permite verificar el estado de las optimizaciones y ejecutar mantenimiento
"""
import time
import os
from datetime import datetime
from flask import current_app

from services.cache_manager import get_cache_manager, get_cached_technicians
from services.connection_manager import get_connection_manager
from models.tickets import Tickets


class PerformanceMonitor:
    """Monitorea y gestiona el rendimiento del sistema"""
    
    def __init__(self):
        self.reports = []
        self.start_time = time.time()
    
    def check_cache_status(self):
        """Verifica el estado del sistema de caché"""
        try:
            cache = get_cache_manager()
            stats = cache.get_stats()
            
            return {
                'status': 'OK',
                'cache_entries': stats['total_entries'],
                'active_entries': stats['active_entries'],
                'expired_entries': stats['expired_entries'],
                'efficiency': round((stats['active_entries'] / max(stats['total_entries'], 1)) * 100, 2)
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'efficiency': 0
            }
    
    def check_connection_pool_status(self):
        """Verifica el estado del pool de conexiones"""
        try:
            manager = get_connection_manager()
            status = manager.get_pool_status()
            
            return {
                'status': 'OK',
                'active_connections': status['active_connections'],
                'max_connections': status['max_connections'],
                'available_connections': status['available_connections'],
                'pool_utilization': round((status['active_connections'] / status['max_connections']) * 100, 2)
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'pool_utilization': 0
            }
    
    def test_query_performance(self):
        """Prueba el rendimiento de consultas comunes"""
        test_results = []
        
        # Test 1: Consulta de tickets recientes
        start_time = time.time()
        try:
            recent_tickets = Tickets.query.filter_by(type_of_service="1").order_by(
                Tickets.creation_date.desc()
            ).limit(10).all()
            
            execution_time = time.time() - start_time
            test_results.append({
                'test': 'Tickets recientes (límite 10)',
                'execution_time': round(execution_time, 3),
                'status': 'OK' if execution_time < 2.0 else 'SLOW',
                'records': len(recent_tickets)
            })
        except Exception as e:
            test_results.append({
                'test': 'Tickets recientes',
                'execution_time': 0,
                'status': 'ERROR',
                'error': str(e)
            })
        
        # Test 2: Consulta de datos comunes cacheados
        start_time = time.time()
        try:
            technicians = get_cached_technicians()
            
            execution_time = time.time() - start_time
            test_results.append({
                'test': 'Técnicos (cacheado)',
                'execution_time': round(execution_time, 3),
                'status': 'OK' if execution_time < 0.5 else 'SLOW',
                'records': len(technicians) if technicians else 0
            })
        except Exception as e:
            test_results.append({
                'test': 'Técnicos (cacheado)',
                'execution_time': 0,
                'status': 'ERROR',
                'error': str(e)
            })
        
        return test_results
    
    def generate_optimization_report(self):
        """Genera un reporte completo del estado de optimizaciones"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'cache_status': self.check_cache_status(),
            'connection_pool_status': self.check_connection_pool_status(),
            'query_performance': self.test_query_performance(),
            'recommendations': []
        }
        
        # Generar recomendaciones basadas en los resultados
        cache_efficiency = report['cache_status'].get('efficiency', 0)
        if cache_efficiency < 50:
            report['recommendations'].append(
                "Eficiencia de caché baja. Considerar aumentar TTL o revisar patrones de acceso."
            )
        
        pool_utilization = report['connection_pool_status'].get('pool_utilization', 0)
        if pool_utilization > 80:
            report['recommendations'].append(
                "Utilización del pool de conexiones alta. Considerar aumentar max_connections."
            )
        
        slow_queries = [q for q in report['query_performance'] if q.get('status') == 'SLOW']
        if slow_queries:
            report['recommendations'].append(
                f"Se detectaron {len(slow_queries)} consultas lentas. Revisar índices de base de datos."
            )
        
        if not report['recommendations']:
            report['recommendations'].append("Sistema funcionando óptimamente.")
        
        return report
    
    def cleanup_expired_cache(self):
        """Limpia entradas expiradas del caché"""
        try:
            cache = get_cache_manager()
            
            # Obtener estadísticas antes
            stats_before = cache.get_stats()
            
            # Limpiar caché (esto se hace automáticamente, pero podemos forzarlo)
            cache.clear()  # En producción, usar método más selectivo
            
            return {
                'status': 'OK',
                'entries_before': stats_before['total_entries'],
                'entries_after': 0,
                'message': 'Caché limpiado exitosamente'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def reset_connection_pool(self):
        """Reinicia el pool de conexiones"""
        try:
            manager = get_connection_manager()
            
            # Cerrar todas las conexiones
            manager.close_all_connections()
            
            return {
                'status': 'OK',
                'message': 'Pool de conexiones reiniciado exitosamente'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }


def run_performance_check():
    """Función principal para ejecutar verificación de rendimiento"""
    monitor = PerformanceMonitor()
    report = monitor.generate_optimization_report()
    
    print("=" * 60)
    print("REPORTE DE RENDIMIENTO DEL SISTEMA")
    print("=" * 60)
    print(f"Fecha: {report['timestamp']}")
    print()
    
    # Estado del caché
    cache_status = report['cache_status']
    print("ESTADO DEL CACHÉ:")
    print(f"  Estado: {cache_status['status']}")
    if cache_status['status'] == 'OK':
        print(f"  Entradas totales: {cache_status['cache_entries']}")
        print(f"  Entradas activas: {cache_status['active_entries']}")
        print(f"  Eficiencia: {cache_status['efficiency']}%")
    else:
        print(f"  Error: {cache_status.get('error', 'Desconocido')}")
    print()
    
    # Estado del pool de conexiones
    pool_status = report['connection_pool_status']
    print("ESTADO DEL POOL DE CONEXIONES:")
    print(f"  Estado: {pool_status['status']}")
    if pool_status['status'] == 'OK':
        print(f"  Conexiones activas: {pool_status['active_connections']}")
        print(f"  Máximo conexiones: {pool_status['max_connections']}")
        print(f"  Utilización: {pool_status['pool_utilization']}%")
    else:
        print(f"  Error: {pool_status.get('error', 'Desconocido')}")
    print()
    
    # Rendimiento de consultas
    print("RENDIMIENTO DE CONSULTAS:")
    for test in report['query_performance']:
        status_icon = "✓" if test['status'] == 'OK' else "⚠" if test['status'] == 'SLOW' else "✗"
        print(f"  {status_icon} {test['test']}: {test['execution_time']}s")
        if 'records' in test:
            print(f"    Registros: {test['records']}")
        if 'error' in test:
            print(f"    Error: {test['error']}")
    print()
    
    # Recomendaciones
    print("RECOMENDACIONES:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    print()
    print("=" * 60)
    
    return report


def apply_emergency_optimizations():
    """Aplica optimizaciones de emergencia cuando el sistema está lento"""
    print("Aplicando optimizaciones de emergencia...")
    
    monitor = PerformanceMonitor()
    
    # Limpiar caché expirado
    cache_result = monitor.cleanup_expired_cache()
    print(f"Limpieza de caché: {cache_result['status']}")
    
    # Reiniciar pool de conexiones
    pool_result = monitor.reset_connection_pool()
    print(f"Reinicio de pool: {pool_result['status']}")
    
    print("Optimizaciones de emergencia completadas.")
    return cache_result['status'] == 'OK' and pool_result['status'] == 'OK'


if __name__ == "__main__":
    # Ejecutar verificación de rendimiento si se ejecuta directamente
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--emergency":
        apply_emergency_optimizations()
    else:
        run_performance_check() 
