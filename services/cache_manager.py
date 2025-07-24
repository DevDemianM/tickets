"""
Sistema de caché para datos estáticos del sistema de tickets
Reduce consultas repetitivas a la base de datos
"""
import time
import threading
from typing import Any, Optional, Dict, Callable

class CacheManager:
    def __init__(self, default_ttl=300):  # 5 minutos por defecto
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str, fetch_function: Callable = None, ttl: Optional[int] = None) -> Any:
        """
        Obtiene un valor del caché o lo calcula usando la función proporcionada
        
        Args:
            key: Clave del caché
            fetch_function: Función para obtener el dato si no está en caché
            ttl: Tiempo de vida en segundos (usa default_ttl si no se especifica)
        
        Returns:
            El valor cacheado o recién calculado
        """
        if ttl is None:
            ttl = self.default_ttl
        
        current_time = time.time()
        
        with self.lock:
            # Verificar si existe y no ha expirado
            if (key in self.cache and 
                key in self.timestamps and 
                current_time - self.timestamps[key] < ttl):
                return self.cache[key]
            
            # Si no existe o expiró, calcular valor
            if fetch_function:
                try:
                    value = fetch_function()
                    self.cache[key] = value
                    self.timestamps[key] = current_time
                    return value
                except Exception as e:
                    print(f"Error actualizando caché para '{key}': {e}")
                    # Si hay error y tenemos un valor anterior, devolverlo
                    if key in self.cache:
                        return self.cache[key]
                    raise e
            
            # Si no hay función de fetch, devolver None
            return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Establece un valor en el caché"""
        if ttl is None:
            ttl = self.default_ttl
            
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def invalidate(self, key: str):
        """Invalida una entrada específica del caché"""
        with self.lock:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
    
    def invalidate_pattern(self, pattern: str):
        """Invalida todas las entradas que contengan el patrón"""
        with self.lock:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                self.cache.pop(key, None)
                self.timestamps.pop(key, None)
    
    def clear(self):
        """Limpia todo el caché"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del caché"""
        with self.lock:
            current_time = time.time()
            expired_count = sum(
                1 for timestamp in self.timestamps.values() 
                if current_time - timestamp >= self.default_ttl
            )
            
            return {
                'total_entries': len(self.cache),
                'expired_entries': expired_count,
                'active_entries': len(self.cache) - expired_count,
                'cache_keys': list(self.cache.keys())
            }

# Instancia global del caché
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Obtiene la instancia global del gestor de caché"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def cached_query(cache_key: str, query_function: Callable, ttl: int = 300):
    """
    Decorator para cachear resultados de consultas
    
    Args:
        cache_key: Clave única para el caché
        query_function: Función que ejecuta la consulta
        ttl: Tiempo de vida en segundos
    
    Returns:
        Resultado cacheado o recién calculado
    """
    cache = get_cache_manager()
    return cache.get(cache_key, query_function, ttl)

# Funciones de conveniencia para datos específicos del sistema
def get_cached_technicians():
    """Obtiene técnicos del caché (TTL: 10 minutos)"""
    def fetch_technicians():
        try:
            from .queries import get_technicians
            return get_technicians()
        except Exception as e:
            print(f"Error fetching technicians in cache: {e}")
            return []
    return cached_query('technicians', fetch_technicians, ttl=600)

def get_cached_product_information():
    """Obtiene información de productos del caché (TTL: 30 minutos)"""
    def fetch_product_info():
        from .queries import get_product_information
        return get_product_information()
    return cached_query('product_information', fetch_product_info, ttl=1800)

def get_cached_spare_parts():
    """Obtiene repuestos del caché (TTL: 30 minutos)"""
    def fetch_spare_parts():
        try:
            from .queries import get_spare_parts
            return get_spare_parts()
        except Exception as e:
            print(f"Error fetching spare parts in cache: {e}")
            return []
    return cached_query('spare_parts', fetch_spare_parts, ttl=1800)

def get_cached_problems():
    """Obtiene problemas del caché (TTL: 1 hora)"""
    def fetch_problems():
        try:
            from models.problems import Problems
            return Problems.query.order_by(Problems.name).all()
        except Exception as e:
            print(f"Error fetching problems in cache: {e}")
            return []  # Retornar lista vacía en caso de error
    
    return cached_query('problems', fetch_problems, ttl=3600)

def get_cached_spare_name():
    """Obtiene nombres de repuestos del caché (TTL: 30 minutos)"""
    def fetch_spare_name():
        from .queries import get_spare_name
        return get_spare_name()
    return cached_query('spare_name', fetch_spare_name, ttl=1800)

def get_cached_sertec():
    """Obtiene datos de sertec del caché (TTL: 1 hora)"""
    def fetch_sertec():
        from .queries import get_sertec
        return get_sertec()
    return cached_query('sertec', fetch_sertec, ttl=3600)

def invalidate_static_data():
    """Invalida todos los datos estáticos cuando sea necesario"""
    cache = get_cache_manager()
    cache.invalidate('technicians')
    cache.invalidate('product_information')
    cache.invalidate('spare_parts')
    cache.invalidate('spare_name')
    cache.invalidate('sertec')
    cache.invalidate('problems')

def force_refresh_cache():
    """Fuerza la actualización de todo el caché"""
    cache = get_cache_manager()
    cache.clear()
    
    # Pre-cargar datos más importantes
    try:
        get_cached_technicians()
        get_cached_product_information()
        get_cached_spare_parts()
        return True
    except Exception as e:
        print(f"Error pre-cargando caché: {e}")
        return False 
