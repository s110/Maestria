"""
upload_to_gcs.py
----------------
Sube todos los archivos de datos generados (mockup) al bucket de GCS
de la zona raw del Data Lake de Lumina Bank.

Uso:
    python upload_to_gcs.py \
        --data-dir data/ \
        --project project-b028d063-61aa-48a0-ad5 \
        --bucket lumina-raw-bd-2026
"""

import argparse
import os
from pathlib import Path

from google.cloud import storage


def upload_directory_to_gcs(
    local_dir: str,
    bucket_name: str,
    project_id: str,
    gcs_prefix: str = "mockup",
    dry_run: bool = False,
):
    """Sube recursivamente todos los archivos de un directorio a GCS."""
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)

    local_path = Path(local_dir)
    if not local_path.exists():
        print(f"[ERROR] Directorio no encontrado: {local_dir}")
        return

    files = list(local_path.rglob("*"))
    files = [f for f in files if f.is_file()]

    print(f"[INFO] Encontrados {len(files)} archivos en {local_dir}")
    print(f"[INFO] Destino: gs://{bucket_name}/{gcs_prefix}/")

    total_bytes = 0
    for file_path in files:
        relative = file_path.relative_to(local_path)
        blob_name = f"{gcs_prefix}/{relative}"

        file_size = file_path.stat().st_size
        total_bytes += file_size

        if dry_run:
            print(f"  [DRY-RUN] {file_path} → gs://{bucket_name}/{blob_name} ({file_size / 1024:.1f} KB)")
        else:
            print(f"  Subiendo: {file_path} → gs://{bucket_name}/{blob_name}...", end="", flush=True)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(str(file_path))
            print(f" ✓ ({file_size / 1024:.1f} KB)")

    print(f"\n[OK] Total subido: {total_bytes / 1024 / 1024:.2f} MB")
    if not dry_run:
        print(f"[OK] Datos disponibles en: gs://{bucket_name}/{gcs_prefix}/")


def upload_single_file(
    local_file: str,
    bucket_name: str,
    project_id: str,
    gcs_path: str,
    dry_run: bool = False,
):
    """Sube un único archivo a GCS."""
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)

    file_path = Path(local_file)
    if not file_path.exists():
        print(f"[ERROR] Archivo no encontrado: {local_file}")
        return

    file_size = file_path.stat().st_size
    if dry_run:
        print(f"[DRY-RUN] {local_file} → gs://{bucket_name}/{gcs_path} ({file_size / 1024:.1f} KB)")
    else:
        print(f"[INFO] Subiendo {local_file} → gs://{bucket_name}/{gcs_path}...")
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(str(file_path))
        print(f"[OK] Subido ({file_size / 1024:.1f} KB): gs://{bucket_name}/{gcs_path}")


def main():
    parser = argparse.ArgumentParser(description="Uploader de datos mockup a GCS – Lumina Bank")
    parser.add_argument("--data-dir", default="data/", help="Directorio local con los datos generados")
    parser.add_argument("--project", default="project-b028d063-61aa-48a0-ad5")
    parser.add_argument("--bucket", default="lumina-raw-bd-2026")
    parser.add_argument("--prefix", default="mockup/raw", help="Prefijo en GCS (carpeta virtual)")
    parser.add_argument("--dry-run", action="store_true", help="Solo simula, no sube nada")
    args = parser.parse_args()

    print("=" * 60)
    print("  Lumina Bank – Data Lake Upload")
    print("=" * 60)
    print(f"  Directorio local : {args.data_dir}")
    print(f"  Bucket destino   : gs://{args.bucket}/{args.prefix}/")
    print(f"  Proyecto GCP     : {args.project}")
    print(f"  Modo dry-run     : {args.dry_run}")
    print("=" * 60)

    upload_directory_to_gcs(
        local_dir=args.data_dir,
        bucket_name=args.bucket,
        project_id=args.project,
        gcs_prefix=args.prefix,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
