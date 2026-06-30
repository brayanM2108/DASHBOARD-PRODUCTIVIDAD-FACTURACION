"""
Script para migrar procesos administrativos desde Excel a MariaDB.

Uso:
    python scripts/import_administrative_processes.py ruta/al/archivo.xlsx

El Excel debe tener las columnas: FECHA, NOMBRE, PROCESO, CANTIDAD
Opcional: OBSERVACION
"""

import sys
from datetime import datetime

import pandas as pd

sys.path.insert(0, ".")
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.administrative_process_repository import AdministrativeProcessRepository


def main(filepath: str):
    df = pd.read_excel(filepath)
    required = {"FECHA", "NOMBRE", "PROCESO", "CANTIDAD"}
    missing = required - set(df.columns)
    if missing:
        print(f"Error: faltan columnas: {missing}")
        sys.exit(1)

    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce").dt.date
    df = df.dropna(subset=["FECHA", "NOMBRE", "PROCESO", "CANTIDAD"])

    db = SessionLocal()
    user_repo = UserRepository(db)
    process_repo = AdministrativeProcessRepository(db)

    users = {u.username.upper(): u.id for u in user_repo.list_all()}
    total = len(df)
    ok = 0
    errors = 0

    for _, row in df.iterrows():
        username = str(row["NOMBRE"]).strip().upper()
        user_id = users.get(username)
        if user_id is None:
            print(f"  ✖ Usuario no encontrado: {row['NOMBRE']}")
            errors += 1
            continue
        try:
            process_repo.create(
                fecha=row["FECHA"],
                proceso=str(row["PROCESO"]).strip().upper(),
                cantidad=int(row["CANTIDAD"]),
                usuario_id=user_id,
                observacion=str(row.get("OBSERVACION", "")).strip() or None,
            )
            ok += 1
        except Exception as e:
            print(f"  ✖ Error en fila {row.name}: {e}")
            errors += 1

    db.close()
    print(f"\nImportación completada: {ok} insertados, {errors} errores de {total} registros")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/import_administrative_processes.py archivo.xlsx")
        sys.exit(1)
    main(sys.argv[1])
