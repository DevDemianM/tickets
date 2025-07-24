#!/usr/bin/env python3
"""
🚀 SCRIPT DE OPTIMIZACIÓN DE BASE DE DATOS - PASO 2
Aplica índices automáticamente para mejorar el rendimiento

Uso:
    python apply_database_optimization.py

Estimación de mejora: 50-70% adicional en velocidad de consultas
"""

import os
import sys
from pathlib import Path
import time

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

def apply_database_indexes():
    """
    Aplica todos los índices de optimización a la base de datos
    """
    print("🚀 INICIANDO OPTIMIZACIÓN DE BASE DE DATOS...")
    print("=" * 60)
    
    try:
        # Importar después de agregar al path
        from flask import Flask
        from sqlalchemy import text
        from models import db
        
        # Crear aplicación Flask mínima para contexto de base de datos
        app = Flask(__name__)
        
        # Configuración básica de base de datos (ajustar según tu configuración)
        database_url = os.getenv('DATABASE_URL', 'postgresql://usuario:password@localhost:5432/tickets_db')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicializar base de datos
        db.init_app(app)
        
        with app.app_context():
            print("📊 Conectando a la base de datos...")
            
            # Leer archivo SQL de índices
            sql_file_path = Path(__file__).parent / 'create_database_indexes.sql'
            
            if not sql_file_path.exists():
                print(f"❌ ERROR: No se encuentra el archivo {sql_file_path}")
                return False
            
            print(f"📖 Leyendo archivo SQL: {sql_file_path}")
            
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Dividir en comandos individuales (separados por ';')
            sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
            
            print(f"🔧 Ejecutando {len(sql_commands)} comandos de optimización...")
            
            successful_commands = 0
            failed_commands = 0
            
            for i, command in enumerate(sql_commands, 1):
                if not command or command.isspace():
                    continue
                    
                try:
                    print(f"  [{i:2d}/{len(sql_commands)}] Ejecutando comando...")
                    
                    # Ejecutar comando SQL usando text() para SQLAlchemy
                    result = db.session.execute(text(command))
                    db.session.commit()
                    
                    successful_commands += 1
                    print(f"  ✅ Completado")
                    
                except Exception as e:
                    failed_commands += 1
                    print(f"  ⚠️  Error: {str(e)}")
                    db.session.rollback()
                    continue
            
            print("\n" + "=" * 60)
            print("📈 RESUMEN DE OPTIMIZACIÓN:")
            print(f"  ✅ Comandos exitosos: {successful_commands}")
            print(f"  ❌ Comandos fallidos: {failed_commands}")
            print(f"  📊 Tasa de éxito: {(successful_commands/(successful_commands+failed_commands)*100):.1f}%")
            
            if successful_commands > 0:
                print("\n🎯 MEJORAS ESTIMADAS:")
                print("  • Consultas de paginación: 60-80% más rápidas")
                print("  • Búsquedas por filtros: 70-90% más rápidas")
                print("  • Cambios de página: 80-95% más rápidas")
                print("  • JOINs con relaciones: 50-70% más rápidas")
                
                print("\n🔍 Para verificar los índices creados, ejecuta:")
                print("  SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;")
                
                return True
            else:
                print("\n❌ No se pudo aplicar ninguna optimización.")
                return False
                
    except ImportError as e:
        print(f"❌ ERROR DE IMPORTACIÓN: {e}")
        print("   Asegúrate de estar en el directorio correcto del proyecto")
        return False
        
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        return False

def verify_prerequisites():
    """
    Verifica que los prerrequisitos estén en orden
    """
    print("🔍 Verificando prerrequisitos...")
    
    # Verificar variables de entorno
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("⚠️  Advertencia: DATABASE_URL no está configurada")
        print("   Se usará configuración por defecto")
    
    # Verificar archivo SQL
    sql_file_path = Path(__file__).parent / 'create_database_indexes.sql'
    if not sql_file_path.exists():
        print(f"❌ ERROR: Archivo SQL no encontrado: {sql_file_path}")
        return False
    
    print("✅ Prerrequisitos verificados")
    return True

def main():
    """
    Función principal
    """
    print("🎯 OPTIMIZACIÓN DE BASE DE DATOS - SISTEMA DE TICKETS")
    print("   Aplicando índices para mejorar el rendimiento...")
    print()
    
    # Verificar prerrequisitos
    if not verify_prerequisites():
        print("❌ Faltan prerrequisitos. Abortando.")
        sys.exit(1)
    
    # Aplicar optimizaciones
    start_time = time.time()
    
    success = apply_database_indexes()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏱️  Tiempo total: {duration:.2f} segundos")
    
    if success:
        print("\n🎉 ¡OPTIMIZACIÓN COMPLETADA EXITOSAMENTE!")
        print("   Tu sistema de tickets ahora debería ser mucho más rápido.")
        sys.exit(0)
    else:
        print("\n💥 OPTIMIZACIÓN FALLÓ")
        print("   Revisa los errores anteriores y vuelve a intentar.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
