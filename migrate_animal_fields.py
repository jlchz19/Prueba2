#!/usr/bin/env python3
"""
Script de migración para actualizar el modelo Animal con campos genéricos
para soportar cualquier tipo de animal de finca.
"""

import sqlite3
import os
from datetime import datetime

def migrate_animal_table():
    """Migra la tabla Animal para incluir los nuevos campos genéricos"""
    
    # Rutas de las bases de datos
    db_paths = [
        'finca_ganadera.db',
        'instance/finca_ganadera.db',
        'instance/mobile_finca_ganadera.db'
    ]
    
    # Comandos SQL para agregar las nuevas columnas
    migration_commands = [
        # Nuevos campos genéricos de producción
        "ALTER TABLE animal ADD COLUMN numero_crias_camada INTEGER;",
        "ALTER TABLE animal ADD COLUMN peso_promedio_crias REAL;",
        "ALTER TABLE animal ADD COLUMN produccion_diaria REAL;",
        "ALTER TABLE animal ADD COLUMN unidad_produccion VARCHAR(20);",
        
        # Actualizar campos reproductivos para ser más genéricos
        "ALTER TABLE animal ADD COLUMN crias_nacidas_vivas INTEGER;",
        "ALTER TABLE animal ADD COLUMN crias_nacidas_muertas INTEGER;",
        "ALTER TABLE animal ADD COLUMN peso_promedio_crias_nacimiento REAL;",
        "ALTER TABLE animal ADD COLUMN promedio_crias_por_camada REAL;",
    ]
    
    # Comandos para migrar datos existentes
    data_migration_commands = [
        # Migrar datos de lechones a crías (más genérico)
        "UPDATE animal SET crias_nacidas_vivas = lechones_nacidos_vivos WHERE lechones_nacidos_vivos IS NOT NULL;",
        "UPDATE animal SET crias_nacidas_muertas = lechones_nacidos_muertos WHERE lechones_nacidos_muertos IS NOT NULL;",
        "UPDATE animal SET peso_promedio_crias_nacimiento = peso_promedio_lechones WHERE peso_promedio_lechones IS NOT NULL;",
        "UPDATE animal SET promedio_crias_por_camada = promedio_lechones_por_camada WHERE promedio_lechones_por_camada IS NOT NULL;",
        
        # Migrar datos de camada a campos genéricos
        "UPDATE animal SET numero_crias_camada = numero_camada WHERE numero_camada IS NOT NULL;",
        "UPDATE animal SET peso_promedio_crias = peso_promedio_camada WHERE peso_promedio_camada IS NOT NULL;",
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Migrando base de datos: {db_path}")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Crear backup antes de la migración
                backup_name = f"{db_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                cursor.execute(f"VACUUM INTO '{backup_name}'")
                print(f"  ✓ Backup creado: {backup_name}")
                
                # Ejecutar comandos de migración
                for command in migration_commands:
                    try:
                        cursor.execute(command)
                        print(f"  ✓ {command}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"  - Columna ya existe: {command}")
                        else:
                            print(f"  ✗ Error en: {command} - {e}")
                
                # Ejecutar migración de datos
                for command in data_migration_commands:
                    try:
                        cursor.execute(command)
                        rows_affected = cursor.rowcount
                        print(f"  ✓ {command} ({rows_affected} filas afectadas)")
                    except sqlite3.Error as e:
                        print(f"  ✗ Error en migración de datos: {command} - {e}")
                
                conn.commit()
                print(f"  ✓ Migración completada para {db_path}")
                
            except Exception as e:
                print(f"  ✗ Error al migrar {db_path}: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()
        else:
            print(f"Base de datos no encontrada: {db_path}")

def verify_migration():
    """Verifica que la migración se haya ejecutado correctamente"""
    
    db_path = 'instance/finca_ganadera.db'
    if not os.path.exists(db_path):
        db_path = 'finca_ganadera.db'
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obtener información de las columnas de la tabla animal
            cursor.execute("PRAGMA table_info(animal)")
            columns = cursor.fetchall()
            
            print("\nColumnas actuales en la tabla animal:")
            new_columns = [
                'numero_crias_camada', 'peso_promedio_crias', 'produccion_diaria', 
                'unidad_produccion', 'crias_nacidas_vivas', 'crias_nacidas_muertas',
                'peso_promedio_crias_nacimiento', 'promedio_crias_por_camada'
            ]
            
            existing_columns = [col[1] for col in columns]
            
            for col_name in new_columns:
                if col_name in existing_columns:
                    print(f"  ✓ {col_name}")
                else:
                    print(f"  ✗ {col_name} - NO ENCONTRADA")
            
            # Contar registros con datos migrados
            cursor.execute("SELECT COUNT(*) FROM animal WHERE numero_crias_camada IS NOT NULL")
            count_crias = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM animal WHERE crias_nacidas_vivas IS NOT NULL")
            count_nacidas = cursor.fetchone()[0]
            
            print(f"\nDatos migrados:")
            print(f"  - Registros con número de crías: {count_crias}")
            print(f"  - Registros con crías nacidas: {count_nacidas}")
            
        except Exception as e:
            print(f"Error al verificar migración: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    print("=== MIGRACIÓN DEL MODELO ANIMAL ===")
    print("Actualizando campos para soportar cualquier tipo de animal de finca\n")
    
    migrate_animal_table()
    verify_migration()
    
    print("\n=== MIGRACIÓN COMPLETADA ===")
    print("El sistema ahora soporta el registro flexible de cualquier tipo de animal.")
