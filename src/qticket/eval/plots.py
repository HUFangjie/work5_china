from __future__ import annotations

import struct
import zlib
from pathlib import Path


def _write_png(path: Path, text: str) -> None:
    width, height = 480, 120
    bg = b'\xff\xff\xff'
    row = b'\x00' + bg * width
    raw = row * height

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    path.write_bytes(data)


def _write_pdf(path: Path, text: str) -> None:
    payload = f"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 400 120] /Contents 4 0 R>>endobj\n4 0 obj<< /Length 44 >>stream\nBT /F1 12 Tf 20 60 Td ({text[:40]}) Tj ET\nendstream endobj\nxref\n0 5\n0000000000 65535 f \ntrailer<< /Size 5 /Root 1 0 R >>\nstartxref\n300\n%%EOF"
    path.write_text(payload, encoding='latin-1')


def _save_stub(fig_dir: Path, name: str, text: str) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    _write_png(fig_dir / f"{name}.png", text)
    _write_pdf(fig_dir / f"{name}.pdf", text)


def plot_handover(rows, fig_dir: Path) -> None:
    _save_stub(fig_dir, 'fig1_cdf', 'handover latency CDF')
    _save_stub(fig_dir, 'fig2_p95_vs_freq', 'P95 latency vs frequency')


def plot_attack(rows, fig_dir: Path) -> None:
    _save_stub(fig_dir, 'fig1_attack_success', 'attack success rate')
    _save_stub(fig_dir, 'fig2_reject_reasons', 'rejection reason distribution')


def plot_revocation(rows, fig_dir: Path) -> None:
    _save_stub(fig_dir, 'fig1_revocation_latency', 'revocation effect latency')


def plot_microbench(rows, fig_dir: Path) -> None:
    _save_stub(fig_dir, 'fig1_microbench_stack', 'microbench path decomposition')


def plot_scalability(rows, fig_dir: Path) -> None:
    _save_stub(fig_dir, 'fig1_concurrency_vs_p95', 'concurrency vs p95 latency')
    _save_stub(fig_dir, 'fig2_throughput_vs_concurrency', 'throughput vs concurrency')
    _save_stub(fig_dir, 'fig3_cpu_vs_concurrency', 'cpu vs concurrency')
