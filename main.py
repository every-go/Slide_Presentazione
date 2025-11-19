import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, List

# Logger minimale
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMP_PATTERNS = (
    ".pdf", ".lof", ".lot", ".log", ".aux", ".fls", ".out",
    ".fdb_latexmk", ".synctex.gz", ".toc", ".snm", ".nav"
)


def cleanup_temp_files(src_dir: Path) -> None:
    """Rimuove file temporanei LaTeX nella cartella."""
    for f in src_dir.iterdir():
        if f.is_file() and f.suffix in TEMP_PATTERNS:
            try:
                f.unlink()
            except Exception:
                logger.debug(f"Cannot delete {f}")


def compile_single_tex(
    tex_file: Path,
    latexmk_cmd: str = "latexmk",
    timeout_sec: int = 60
) -> Optional[Path]:
    """Compila un singolo file .tex in PDF."""
    if not tex_file.exists():
        logger.error(f"File .tex non trovato: {tex_file}")
        return None

    logger.info(f"Compilo {tex_file.name}...")

    result = subprocess.run(
        [latexmk_cmd, "-pdf", "-interaction=nonstopmode", "-f", tex_file.name],
        cwd=str(tex_file.parent),
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )

    if result.returncode != 0:
        logger.error(f"Errore in compilazione: {result.stderr.strip()}")
        return None

    pdf_path = tex_file.with_suffix(".pdf")
    if pdf_path.exists():
        logger.info(f"Compilato: {pdf_path}")
        return pdf_path

    logger.error("Compilazione completata ma PDF non trovato.")
    return None


if __name__ == "__main__":
    # Path della cartella corrente
    cwd = Path(".")

    # Trova il primo .tex nella cartella
    tex_files = list(cwd.glob("*.tex"))
    if not tex_files:
        logger.error("Nessun file .tex trovato nella cartella.")
        exit(1)

    tex_file = tex_files[0]  # Compila solo il primo file

    pdf = compile_single_tex(tex_file)
    cleanup_temp_files(cwd)

    if pdf:
        logger.info("Operazione completata.")
