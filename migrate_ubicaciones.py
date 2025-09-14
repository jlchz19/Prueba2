#!/usr/bin/env python3
"""
Script de migración para agregar el sistema de ubicaciones específicas
"""

import sqlite3
import os
from datetime import datetime

def migrate_ubicaciones():
    """Migra la base de datos para incluir el sistema de ubicaciones"""
    
    # Rutas de las bases de datos
    db_paths = [
        'finca_ganadera.db',
        'instance/finca_ganadera.db',
        'instance/mobile_finca_ganadera.db'
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
                
                # 1. Crear tabla ubicacion
                create_ubicacion_table = """
                CREATE TABLE IF NOT EXISTS ubicacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    tipo_ubicacion VARCHAR(50) NOT NULL,
                    tipo_animal VARCHAR(50) NOT NULL,
                    capacidad INTEGER NOT NULL,
                    area REAL,
                    descripcion TEXT,
                    estado VARCHAR(20) DEFAULT 'disponible',
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    finca_id INTEGER NOT NULL,
                    FOREIGN KEY (finca_id) REFERENCES finca (id)
                );
                """
                cursor.execute(create_ubicacion_table)
                print("  ✓ Tabla ubicacion creada")
                
                # 2. Agregar columnas faltantes a la tabla potrero
                potrero_columns = [
                    ("tipo_pasto", "VARCHAR(100)"),
                    ("funcion", "VARCHAR(100)")
                ]
                
                for col_name, col_type in potrero_columns:
                    try:
                        cursor.execute(f"ALTER TABLE potrero ADD COLUMN {col_name} {col_type};")
                        print(f"  ✓ Columna {col_name} agregada a potrero")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"  - Columna {col_name} ya existe")
                        else:
                            print(f"  ✗ Error agregando {col_name}: {e}")
                
                # 3. Agregar columna ubicacion_id a la tabla animal
                try:
                    cursor.execute("ALTER TABLE animal ADD COLUMN ubicacion_id INTEGER;")
                    print("  ✓ Columna ubicacion_id agregada a animal")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print("  - Columna ubicacion_id ya existe")
                    else:
                        print(f"  ✗ Error agregando ubicacion_id: {e}")
                
                # 4. Crear índices para mejor rendimiento
                try:
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_animal_ubicacion ON animal(ubicacion_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ubicacion_finca ON ubicacion(finca_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ubicacion_tipo ON ubicacion(tipo_ubicacion);")
                    print("  ✓ Índices creados")
                except sqlite3.Error as e:
                    print(f"  ✗ Error creando índices: {e}")
                
                # 5. Insertar ubicaciones de ejemplo (opcional)
                cursor.execute("SELECT COUNT(*) FROM ubicacion")
                if cursor.fetchone()[0] == 0:
                    # Obtener fincas existentes
                    cursor.execute("SELECT id FROM finca LIMIT 1")
                    finca_result = cursor.fetchone()
                    
                    if finca_result:
                        finca_id = finca_result[0]
                        ubicaciones_ejemplo = [
                            ('Cochiquera Principal', 'cochiquera', 'Porcino', 20, 100.0, 'Cochiquera principal para cerdos adultos'),
                            ('Gallinero Norte', 'gallinero', 'Aviar', 50, 80.0, 'Gallinero para gallinas ponedoras'),
                            ('Establo Central', 'establo', 'Equino', 8, 200.0, 'Establo para caballos de trabajo'),
                        ]
                        
                        for ubicacion in ubicaciones_ejemplo:
                            cursor.execute("""
                                INSERT INTO ubicacion (nombre, tipo_ubicacion, tipo_animal, capacidad, area, descripcion, finca_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, ubicacion + (finca_id,))
                        
                        print("  ✓ Ubicaciones de ejemplo creadas")
                
                conn.commit()
                print(f"  ✓ Migración completada para {db_path}")
                
            except Exception as e:
                print(f"  ✗ Error al migrar {db_path}: {e}")
                if 'conn' in locals():
                    conn.rollback()
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
            
            # Verificar tabla ubicacion
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ubicacion'")
            if cursor.fetchone():
                print("✓ Tabla ubicacion existe")
                
                cursor.execute("SELECT COUNT(*) FROM ubicacion")
                count = cursor.fetchone()[0]
                print(f"✓ Ubicaciones registradas: {count}")
            else:
                print("✗ Tabla ubicacion no encontrada")
            
            # Verificar columna ubicacion_id en animal
            cursor.execute("PRAGMA table_info(animal)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'ubicacion_id' in columns:
                print("✓ Columna ubicacion_id existe en tabla animal")
            else:
                print("✗ Columna ubicacion_id no encontrada en tabla animal")
            
        except Exception as e:
            print(f"Error al verificar migración: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    print("=== MIGRACIÓN DEL SISTEMA DE UBICACIONES ===")
    print("Creando sistema de ubicaciones específicas por tipo de animal\n")
    
    migrate_ubicaciones()
    print("\n=== VERIFICACIÓN ===")
    verify_migration()
    
    print("\n=== MIGRACIÓN COMPLETADA ===")
    print("El sistema ahora soporta ubicaciones específicas:")
    print("- Cochiqueras para cerdos")
    print("- Gallineros para aves") 
    print("- Establos/Corrales para caballos")
    print("- Potreros para bovinos")
