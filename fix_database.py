import sqlite3
import os

def fix_database():
    db_paths = ['finca_ganadera.db', 'instance/finca_ganadera.db']
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Arreglando {db_path}...")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # Agregar columnas faltantes a potrero
                cursor.execute("ALTER TABLE potrero ADD COLUMN tipo_pasto VARCHAR(100)")
                print("✓ Columna tipo_pasto agregada")
            except:
                print("- tipo_pasto ya existe")
            
            try:
                cursor.execute("ALTER TABLE potrero ADD COLUMN funcion VARCHAR(100)")
                print("✓ Columna funcion agregada")
            except:
                print("- funcion ya existe")
            
            try:
                # Agregar columna ubicacion_id a animal
                cursor.execute("ALTER TABLE animal ADD COLUMN ubicacion_id INTEGER")
                print("✓ Columna ubicacion_id agregada")
            except:
                print("- ubicacion_id ya existe")
            
            try:
                # Crear tabla ubicacion
                cursor.execute("""
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
                    finca_id INTEGER NOT NULL
                )
                """)
                print("✓ Tabla ubicacion creada")
            except Exception as e:
                print(f"Error creando tabla ubicacion: {e}")
            
            conn.commit()
            conn.close()
            print(f"✓ {db_path} arreglado\n")

if __name__ == "__main__":
    fix_database()
    print("Base de datos arreglada. Ahora puedes ejecutar la aplicación.")
