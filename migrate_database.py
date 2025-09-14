#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar las nuevas columnas y tablas
para las funcionalidades avanzadas de AgroGest.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Ejecuta las migraciones necesarias para actualizar la base de datos."""
    db_path = 'finca_ganadera.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos {db_path} no encontrada.")
        return False
    
    print(f"🔄 Iniciando migración de la base de datos...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear backup de la base de datos
        backup_path = f'finca_ganadera_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        backup_conn = sqlite3.connect(backup_path)
        conn.backup(backup_conn)
        backup_conn.close()
        print(f"✅ Backup creado: {backup_path}")
        
        # Lista de migraciones a ejecutar
        migrations = [
            # Migración 1: Agregar columnas faltantes a historial_peso
            {
                'name': 'Add missing columns to historial_peso',
                'sql': [
                    "ALTER TABLE historial_peso ADD COLUMN usuario_id INTEGER REFERENCES usuario(id);",
                ]
            },
            
            # Migración 2: Crear tabla historial_alimentacion
            {
                'name': 'Create historial_alimentacion table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS historial_alimentacion (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL REFERENCES animal(id),
                        fecha DATE NOT NULL DEFAULT (date('now')),
                        tipo_alimento VARCHAR(100) NOT NULL,
                        cantidad FLOAT NOT NULL,
                        unidad VARCHAR(20) DEFAULT 'kg',
                        costo FLOAT,
                        observaciones TEXT,
                        usuario_id INTEGER REFERENCES usuario(id)
                    );"""
                ]
            },
            
            # Migración 3: Crear tabla historial_salud
            {
                'name': 'Create historial_salud table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS historial_salud (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL REFERENCES animal(id),
                        fecha DATE NOT NULL DEFAULT (date('now')),
                        tipo_evento VARCHAR(50) NOT NULL,
                        descripcion TEXT NOT NULL,
                        medicamento VARCHAR(100),
                        dosis VARCHAR(50),
                        veterinario VARCHAR(100),
                        costo FLOAT,
                        proxima_dosis DATE,
                        observaciones TEXT,
                        usuario_id INTEGER REFERENCES usuario(id)
                    );"""
                ]
            },
            
            # Migración 4: Crear tabla nota_animal
            {
                'name': 'Create nota_animal table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS nota_animal (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL REFERENCES animal(id),
                        fecha DATETIME NOT NULL DEFAULT (datetime('now')),
                        titulo VARCHAR(100) NOT NULL,
                        contenido TEXT NOT NULL,
                        tipo VARCHAR(20) DEFAULT 'general',
                        usuario_id INTEGER REFERENCES usuario(id)
                    );"""
                ]
            },
            
            # Migración 5: Crear tabla historial_potrero
            {
                'name': 'Create historial_potrero table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS historial_potrero (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL REFERENCES animal(id),
                        potrero_id INTEGER NOT NULL REFERENCES potrero(id),
                        fecha_entrada DATE NOT NULL,
                        fecha_salida DATE,
                        motivo_cambio VARCHAR(200),
                        usuario_id INTEGER REFERENCES usuario(id)
                    );"""
                ]
            },
            
            # Migración 6: Crear tabla evento_reproductivo
            {
                'name': 'Create evento_reproductivo table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS evento_reproductivo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL REFERENCES animal(id),
                        tipo_evento VARCHAR(30) NOT NULL,
                        fecha_evento DATE NOT NULL,
                        semental_id INTEGER REFERENCES animal(id),
                        fecha_estimada_parto DATE,
                        resultado VARCHAR(20),
                        observaciones TEXT,
                        crias_nacidas INTEGER,
                        crias_vivas INTEGER,
                        peso_promedio_crias FLOAT,
                        usuario_id INTEGER REFERENCES usuario(id),
                        finca_id INTEGER NOT NULL REFERENCES finca(id)
                    );"""
                ]
            },
            
            # Migración 7: Crear tabla movimiento_financiero
            {
                'name': 'Create movimiento_financiero table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS movimiento_financiero (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        finca_id INTEGER NOT NULL REFERENCES finca(id),
                        tipo VARCHAR(20) NOT NULL,
                        categoria VARCHAR(50) NOT NULL,
                        descripcion VARCHAR(200) NOT NULL,
                        monto FLOAT NOT NULL,
                        fecha DATE NOT NULL DEFAULT (date('now')),
                        metodo_pago VARCHAR(30),
                        referencia VARCHAR(100),
                        animal_id INTEGER REFERENCES animal(id),
                        usuario_id INTEGER REFERENCES usuario(id)
                    );"""
                ]
            },
            
            # Migración 8: Actualizar tabla inventario
            {
                'name': 'Update inventario table',
                'sql': [
                    "ALTER TABLE inventario ADD COLUMN cantidad_minima FLOAT DEFAULT 0;",
                    "ALTER TABLE inventario ADD COLUMN ubicacion VARCHAR(100);",
                    "ALTER TABLE inventario ADD COLUMN fecha_actualizacion DATETIME DEFAULT (datetime('now'));",
                ]
            },
            
            # Migración 9: Crear tabla alerta
            {
                'name': 'Create alerta table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS alerta (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        finca_id INTEGER NOT NULL REFERENCES finca(id),
                        tipo VARCHAR(30) NOT NULL,
                        titulo VARCHAR(100) NOT NULL,
                        descripcion TEXT NOT NULL,
                        prioridad VARCHAR(20) DEFAULT 'media',
                        fecha_creacion DATETIME DEFAULT (datetime('now')),
                        fecha_vencimiento DATE,
                        estado VARCHAR(20) DEFAULT 'activa',
                        animal_id INTEGER REFERENCES animal(id),
                        usuario_id INTEGER REFERENCES usuario(id)
                    );"""
                ]
            },
            
            # Migración 10: Crear tabla codigo_qr
            {
                'name': 'Create codigo_qr table',
                'sql': [
                    """CREATE TABLE IF NOT EXISTS codigo_qr (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL REFERENCES animal(id),
                        codigo VARCHAR(100) UNIQUE NOT NULL,
                        fecha_generacion DATETIME DEFAULT (datetime('now')),
                        activo BOOLEAN DEFAULT 1,
                        usuario_id INTEGER REFERENCES usuario(id)
                    );"""
                ]
            }
        ]

        # Migración adicional: asegurar columnas críticas en registro_peso
        # - Agregar finca_id y backfill desde animal.finca_id
        # - Agregar usuario_id y fecha_registro si hiciera falta
        migrations.append({
            'name': 'Ensure registro_peso has finca_id, usuario_id, fecha_registro and backfill',
            'sql': [
                # Agregar columnas (si no existen, el bloque de try/except más abajo lo ignora)
                "ALTER TABLE registro_peso ADD COLUMN finca_id INTEGER REFERENCES finca(id);",
                "ALTER TABLE registro_peso ADD COLUMN usuario_id INTEGER REFERENCES usuario(id);",
                "ALTER TABLE registro_peso ADD COLUMN fecha_registro DATETIME DEFAULT (datetime('now'));",
                # Crear índice para consultas por finca
                "CREATE INDEX IF NOT EXISTS idx_registro_peso_finca ON registro_peso(finca_id);",
                # Backfill de finca_id desde la tabla animal
                "UPDATE registro_peso SET finca_id = (SELECT animal.finca_id FROM animal WHERE animal.id = registro_peso.animal_id) WHERE finca_id IS NULL;"
            ]
        })
        
        # Ejecutar migraciones
        for i, migration in enumerate(migrations, 1):
            print(f"🔄 Ejecutando migración {i}/{len(migrations)}: {migration['name']}")
            
            for sql in migration['sql']:
                try:
                    cursor.execute(sql)
                    print(f"   ✅ {sql[:50]}...")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e) or "already exists" in str(e):
                        print(f"   ⚠️  Ya existe: {sql[:50]}...")
                    else:
                        print(f"   ❌ Error: {e}")
                        raise
        
        # Confirmar cambios
        conn.commit()
        print("✅ Todas las migraciones completadas exitosamente!")
        
        # Verificar estructura de la base de datos
        print("\n📋 Verificando estructura de tablas:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if not table_name.startswith('sqlite_'):
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print(f"   📄 {table_name}: {len(columns)} columnas")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 AgroGest - Migración de Base de Datos")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Migración completada exitosamente!")
        print("✅ La aplicación ya puede usar las nuevas funcionalidades.")
    else:
        print("\n❌ La migración falló. Revisa los errores anteriores.")
        print("💡 Puedes restaurar desde el backup si es necesario.")
