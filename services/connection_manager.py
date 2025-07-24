"""
Gestor de conexiones optimizado para consultas SQL Server
Implementa pool de conexiones reutilizable para mejorar rendimiento
"""
import pyodbc
import threading
import queue
import time
from contextlib import contextmanager
import os

class ConnectionManager:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connection_pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        
        # Configuración de conexión
        self.connection_string = (
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=20.109.21.246;'
            'DATABASE=MICELU;'
            'UID=db_read;'
            'PWD=mHRL_<="(],#aZ)T"A3QeD;'
            'TrustServerCertificate=yes;'
            'Connection Timeout=30;'
            'Command Timeout=60'
        )
        
        # Pre-llenar el pool con algunas conexiones
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa el pool con conexiones pre-creadas"""
        try:
            # Crear 3 conexiones iniciales
            for _ in range(min(3, self.max_connections)):
                conn = self._create_connection()
                if conn:
                    self.connection_pool.put(conn)
                    self.active_connections += 1
        except Exception as e:
            print(f"Error inicializando pool de conexiones: {e}")
    
    def _create_connection(self):
        """Crea una nueva conexión a la base de datos"""
        try:
            conn = pyodbc.connect(self.connection_string)
            # Configurar timeout a nivel de conexión
            conn.timeout = 60
            return conn
        except Exception as e:
            print(f"Error creando conexión: {e}")
            return None
    
    def _is_connection_valid(self, conn):
        """Verifica si una conexión sigue siendo válida"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except:
            return False
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener una conexión del pool"""
        connection = None
        try:
            # Intentar obtener conexión del pool
            try:
                connection = self.connection_pool.get_nowait()
                
                # Verificar si la conexión sigue siendo válida
                if not self._is_connection_valid(connection):
                    connection.close()
                    connection = None
            except queue.Empty:
                connection = None
            
            # Si no hay conexión válida disponible, crear una nueva
            if connection is None:
                with self.lock:
                    if self.active_connections < self.max_connections:
                        connection = self._create_connection()
                        if connection:
                            self.active_connections += 1
                    else:
                        # Esperar por una conexión disponible
                        try:
                            connection = self.connection_pool.get(timeout=30)
                        except queue.Empty:
                            raise Exception("Timeout esperando conexión disponible")
            
            yield connection
            
        except Exception as e:
            # Si hay error, cerrar la conexión problemática
            if connection:
                try:
                    connection.close()
                except:
                    pass
                with self.lock:
                    self.active_connections -= 1
            raise e
        finally:
            # Devolver conexión al pool si sigue siendo válida
            if connection:
                try:
                    if self._is_connection_valid(connection):
                        self.connection_pool.put_nowait(connection)
                    else:
                        connection.close()
                        with self.lock:
                            self.active_connections -= 1
                except queue.Full:
                    # Pool lleno, cerrar conexión
                    connection.close()
                    with self.lock:
                        self.active_connections -= 1
    
    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta utilizando el pool de conexiones
        
        Args:
            query (str): La consulta SQL a ejecutar
            params (tuple, optional): Parámetros para la consulta
            
        Returns:
            list: Resultados de la consulta
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                results = cursor.fetchall()
                cursor.close()
                
                execution_time = time.time() - start_time
                if execution_time > 5:  # Log solo consultas lentas
                    print(f"Consulta lenta ({execution_time:.2f}s): {query[:100]}...")
                
                return results
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"Error en consulta ({execution_time:.2f}s): {str(e)}")
            print(f"Query: {query[:200]}...")
            
            # Intentar con consulta escapada si es error de sintaxis
            if "syntax error" in str(e).lower() and "'" in query:
                try:
                    escaped_query = query.replace("'", "''")
                    print(f"Reintentando con query escapada...")
                    
                    with self.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(escaped_query)
                        results = cursor.fetchall()
                        cursor.close()
                        return results
                        
                except Exception as e2:
                    print(f"Error en segundo intento: {str(e2)}")
                    return []
            
            return []
    
    def close_all_connections(self):
        """Cierra todas las conexiones del pool"""
        with self.lock:
            while not self.connection_pool.empty():
                try:
                    conn = self.connection_pool.get_nowait()
                    conn.close()
                except:
                    pass
            self.active_connections = 0
    
    def get_pool_status(self):
        """Retorna información sobre el estado del pool"""
        return {
            'active_connections': self.active_connections,
            'max_connections': self.max_connections,
            'available_connections': self.connection_pool.qsize()
        }

# Instancia global del gestor de conexiones
_connection_manager = None

def get_connection_manager():
    """Obtiene la instancia global del gestor de conexiones"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager

def execute_query_optimized(query, params=None):
    """
    Función de conveniencia para ejecutar consultas optimizadas
    Compatible con la función execute_query existente
    """
    manager = get_connection_manager()
    return manager.execute_query(query, params) 
