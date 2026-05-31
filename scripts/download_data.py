"""
Script de descarga de datos del DANE.

Descarga los anexos Excel de la GEIH para el rango de fechas especificado.
Usa caché local para evitar re-descargas innecesarias.

Uso:
    python scripts/download_data.py --start 2015 --end 2026
    python scripts/download_data.py --historic  # Solo el archivo histórico
    python scripts/download_data.py --month 2026-04  # Un mes específico
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import asyncio
from datetime import datetime

import httpx
from loguru import logger
from tqdm import tqdm

from src.utils.paths import RAW_DIR

# Configurar logging
logger.add("logs/download.log", rotation="10 MB", retention="30 days")

DANE_GEIH_URL = "https://www.dane.gov.co/files/operaciones/GEIH/anex-GEIH-{mes_abrev}{año}.xlsx"
DANE_HISTORIC_URL = (
    "https://www.dane.gov.co/files/investigaciones/boletines/ech/"
    "nuevo-enfoque-conceptual-metodologico-2018/"
    "anexo-mercado-laboral-segun-proyecciones-CNPV2018.xlsx"
)

# Mapeo de números de mes a abreviatura DANE
MES_ABREV = {
    1: "ene", 2: "feb", 3: "mar", 4: "abr",
    5: "may", 6: "jun", 7: "jul", 8: "ago",
    9: "sep", 10: "oct", 11: "nov", 12: "dic",
}


def build_url(year: int, month: int) -> str:
    """Construye la URL de descarga para un mes/año específico."""
    mes_abrev = MES_ABREV[month]
    return DANE_GEIH_URL.format(mes_abrev=mes_abrev, año=year)


async def download_file(
    client: httpx.AsyncClient,
    url: str,
    dest_path: Path,
    desc: str = "",
) -> bool:
    """
    Descarga un archivo de forma asíncrona con barra de progreso.

    Returns:
        True si la descarga fue exitosa, False en caso contrario.
    """
    if dest_path.exists():
        logger.info(f"Ya existe: {dest_path.name} (skip)")
        return True

    try:
        async with client.stream("GET", url, follow_redirects=True) as response:
            if response.status_code != 200:
                logger.warning(f"No disponible ({response.status_code}): {url}")
                return False

            total = int(response.headers.get("content-length", 0))
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dest_path, "wb") as f:
                with tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc=desc,
                    leave=False,
                ) as pbar:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))

        logger.success(f"Descargado: {dest_path.name}")
        return True

    except Exception as e:
        logger.error(f"Error descargando {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()  # Borrar archivo parcial
        return False


async def download_range(start_year: int, end_year: int):
    """Descarga anexos GEIH para un rango de años."""
    dest_dir = RAW_DIR / "geih"
    dest_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                # No descargar meses futuros
                now = datetime.now()
                if year == now.year and month > now.month:
                    continue

                url = build_url(year, month)
                filename = f"anex-GEIH-{MES_ABREV[month]}{year}.xlsx"
                dest_path = dest_dir / filename
                desc = f"{MES_ABREV[month]} {year}"

                tasks.append(download_file(client, url, dest_path, desc))

        # Ejecutar en lotes de 5 para no saturar
        for i in range(0, len(tasks), 5):
            batch = tasks[i : i + 5]
            await asyncio.gather(*batch)


async def download_historic():
    """Descarga el archivo histórico empalmado (2001-2021)."""
    dest_path = RAW_DIR / "geih" / "historico_empalmado_2001_2021.xlsx"
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=120.0) as client:
        await download_file(client, DANE_HISTORIC_URL, dest_path, "Histórico 2001-2021")


async def download_month(year: int, month: int):
    """Descarga un mes específico."""
    url = build_url(year, month)
    filename = f"anex-GEIH-{MES_ABREV[month]}{year}.xlsx"
    dest_path = RAW_DIR / "geih" / filename
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=60.0) as client:
        await download_file(client, url, dest_path, f"{MES_ABREV[month]} {year}")


def main():
    parser = argparse.ArgumentParser(description="Descarga datos de desempleo del DANE")
    parser.add_argument(
        "--start", type=int, default=2015,
        help="Año inicial (default: 2015)"
    )
    parser.add_argument(
        "--end", type=int, default=datetime.now().year,
        help="Año final (default: año actual)"
    )
    parser.add_argument(
        "--historic", action="store_true",
        help="Descargar solo archivo histórico empalmado"
    )
    parser.add_argument(
        "--month", type=str,
        help="Descargar un mes específico (formato: YYYY-MM)"
    )

    args = parser.parse_args()

    if args.historic:
        logger.info("Descargando archivo histórico empalmado...")
        asyncio.run(download_historic())
    elif args.month:
        year, month = map(int, args.month.split("-"))
        logger.info(f"Descargando anexo {args.month}...")
        asyncio.run(download_month(year, month))
    else:
        logger.info(f"Descargando rango {args.start}-{args.end}...")
        logger.info("Esto puede tomar varios minutos. Los archivos existentes se omiten.")
        asyncio.run(download_range(args.start, args.end))

    logger.success("¡Descarga completada!")


if __name__ == "__main__":
    main()
