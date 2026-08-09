"""Deterministic synthetic fixture-pack builder for survey-document ingestion (M2-T015).

Surveys are private licensed documents with NO live official source (unlike the
MapPLUTO geometry pack, which captures a keyless official service). Every fixture in
this pack is therefore **all-synthetic**, generated deterministically from bytes this
module constructs — never a real client survey, never a captured official response, no
private document. Each fixture is labelled ``classification: synthetic`` in the
MANIFEST and carries an honest ``extraction_status`` that states whether its extraction
path is live in the shipped pipeline (units 3a-3l) or deferred to a later unit.

The PDF builders mirror the in-repo test suite byte-for-byte (``_assemble_pdf`` /
``_one_page_pdf`` from ``test_survey_pipeline.py`` and ``test_vector_pdf_decoder.py``)
so the committed fixtures are exactly the shapes the decoder + pipeline tests exercise.
The raster fixtures are structural PNG stubs (signature + IHDR + IEND with valid CRCs,
no pixel IDAT): they exercise the S1 magic sniff and the raster route (which defers to
the OCR/raster unit), and use only ``binascii.crc32`` so regeneration is byte-identical
on every host (no zlib-version dependence). The malicious fixtures reuse the exact
threat vectors from ``test_gate.py`` (T01 executable-renamed, T02 HTML-renamed).

The MANIFEST records, per fixture: ``file``, ``fixture_id``, ``classification``,
``category``, ``format``, ``builder``, ``extraction_status``, ``purpose``,
``supported_scenarios``, and a ``sha256:<hex>`` digest over the EXACT committed bytes.
The MANIFEST carries no wall-clock timestamp so the pack round-trips deterministically:
re-running this builder regenerates byte-identical fixtures and a byte-identical
MANIFEST (asserted by ``tests/documents/test_survey_fixture_pack.py``).

Usage (from services/api):
    python tests/documents/fixtures/survey_documents/build_fixture_pack.py
"""

from __future__ import annotations

import binascii
import hashlib
import json
import struct
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
TASK = "M2-T015"
SUBJECT_BBL = "1002920001"  # the clean-survey subject BBL used across the pipeline tests
WRONG_BBL = "3001230045"  # a different, syntactically valid NYC BBL (SB-S7)


# --------------------------------------------------------------- PDF byte builders
# Byte-for-byte identical to the assemblers in test_survey_pipeline.py and
# test_vector_pdf_decoder.py so fixtures match exactly what those tests exercise.


def _assemble_pdf(bodies: list[bytes], root: bytes = b"1 0 R") -> bytes:
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(bodies, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref_offset = len(out)
    out += b"xref\n0 %d\n" % (len(bodies) + 1) + b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %s >>\n" % (len(bodies) + 1, root)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(out)


def _stream_body(payload: bytes) -> bytes:
    return b"<< /Length %d >>\nstream\n" % len(payload) + payload + b"\nendstream"


def _one_page_pdf(content: bytes, page_extra: bytes = b" /MediaBox [0 0 612 792]") -> bytes:
    return _assemble_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R%s /Contents 4 0 R >>" % page_extra,
            _stream_body(content),
        ]
    )


def _two_page_pdf(content_a: bytes, content_b: bytes) -> bytes:
    return _assemble_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 6 0 R >>",
            _stream_body(content_a),
            _stream_body(content_b),
        ]
    )


# --------------------------------------------------------------- raster byte builders
# Structural PNG stub: signature + IHDR + IEND with valid CRC32 (no IDAT). Enough for
# the S1 magic sniff + raster routing; real pixel scans come from the OCR/raster unit.


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    )


def _raster_png_stub(width: int, height: int) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)  # 8-bit grayscale
    return signature + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IEND", b"")


# Threat vectors, verbatim from test_gate.py.
EXE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00"  # PE executable header (T01)
HTML_BYTES = b"<!DOCTYPE html><html><body>not a survey</body></html>"  # (T02)


# --------------------------------------------------------------- the fixture plan
# Each entry: (file, fixture_id, category, format, builder, extraction_status,
# supported_scenarios, purpose, bytes). Kept in one place so the MANIFEST and the
# committed files can never drift.


def generate_fixtures() -> list[dict]:
    """Deterministically build every fixture in memory (no disk writes).

    Returns a list of fixture descriptors in stable file order. Called by the builder
    ``main()`` to write the pack and by the integrity test to compare against committed
    bytes — so the two can never disagree.
    """
    plan: list[dict] = [
        {
            "file": "SVY01_digital_scale_bbl.pdf",
            "fixture_id": "SVY01",
            "category": "digital_pdf",
            "format": "born_digital_pdf",
            "builder": "_one_page_pdf(embedded_text)",
            "extraction_status": "live-embedded-text-extraction",
            "supported_scenarios": ["SB-S1", "SB-S8"],
            "purpose": (
                "Clean digitally-authored survey: canonical 1:240 scale statement + the "
                "subject BBL 1002920001 in embedded text. Decodes via "
                "embedded_text_extraction and promotes to auto_extracted through the H5 "
                "gate when every check passes (the SB-S1 happy path)."
            ),
            "bytes": _one_page_pdf(
                b"BT /F1 12 Tf 100 700 Td (1:240) Tj 100 680 Td (%s) Tj ET"
                % SUBJECT_BBL.encode("ascii")
            ),
        },
        {
            "file": "SVY02_vector_segments_rect.pdf",
            "fixture_id": "SVY02",
            "category": "vector_pdf",
            "format": "vector_pdf",
            "builder": "_one_page_pdf(vector_ops)",
            "extraction_status": "live-vector-object-extraction",
            "supported_scenarios": ["SB-S1"],
            "purpose": (
                "Vector-authored survey primitives: a straight segment (m/l S) and a "
                "rectangle (re f) inside the strict straight-line survey subset. Decodes "
                "via vector_object_extraction into device-space VectorSegment/VectorRect "
                "primitives (no curve operator, so no decode refusal)."
            ),
            "bytes": _one_page_pdf(b"10 20 m 110 20 l S 5 5 40 30 re f"),
        },
        {
            "file": "SVY03_clean_scan.png",
            "fixture_id": "SVY03",
            "category": "clean_scan",
            "format": "png",
            "builder": "_raster_png_stub(64, 64)",
            "extraction_status": "deferred-to-OCR/raster-unit",
            "supported_scenarios": ["SB-S2"],
            "purpose": (
                "Clean raster scan (structural PNG stub, 64x64 grayscale IHDR, valid "
                "CRCs, no pixel IDAT). Exercises the S1 magic sniff and the raster route: "
                "PNG is a supported format but has no concrete decoder yet, so the "
                "pipeline returns DecoderUnavailable. Real pixel content and OCR land in "
                "the deferred OCR/raster unit."
            ),
            "bytes": _raster_png_stub(64, 64),
        },
        {
            "file": "SVY04_poor_scan.png",
            "fixture_id": "SVY04",
            "category": "poor_scan",
            "format": "png",
            "builder": "_raster_png_stub(8, 8)",
            "extraction_status": "deferred-to-OCR/raster-unit",
            "supported_scenarios": ["SB-S2"],
            "purpose": (
                "Poor/low-resolution raster scan (structural PNG stub, 8x8 grayscale "
                "IHDR) — distinct bytes from the clean scan to represent a degraded "
                "capture. Same raster route/DecoderUnavailable behavior; OCR quality "
                "handling is the deferred OCR/raster unit's responsibility."
            ),
            "bytes": _raster_png_stub(8, 8),
        },
        {
            "file": "SVY05_rotated_page.pdf",
            "fixture_id": "SVY05",
            "category": "rotated_pages",
            "format": "born_digital_pdf",
            "builder": "_one_page_pdf(embedded_text, /Rotate 90)",
            "extraction_status": "deferred-to-rotation-normalization-unit",
            "supported_scenarios": ["SB-S1", "SB-S2"],
            "purpose": (
                "Digitally-authored page carrying a /Rotate 90 page attribute. The "
                "content stream still decodes (embedded text), but mapping rotated "
                "device space into a normalized survey orientation is deferred to a "
                "later rotation-normalization unit, so rotation-aware extraction is not "
                "asserted live."
            ),
            "bytes": _one_page_pdf(
                b"BT /F1 12 Tf 100 700 Td (1:240) Tj ET",
                page_extra=b" /MediaBox [0 0 612 792] /Rotate 90",
            ),
        },
        {
            "file": "SVY06_mixed_units.pdf",
            "fixture_id": "SVY06",
            "category": "mixed_units",
            "format": "born_digital_pdf",
            "builder": "_one_page_pdf(embedded_text)",
            "extraction_status": "deferred-to-distance/unit-normalization-unit",
            "supported_scenarios": ["SB-S3"],
            "purpose": (
                "A survey stating a boundary distance in FEET on one course and METERS "
                "on another (mixed units). units.py is the deterministic authority that "
                "refuses mixed/unsupported units (never coerces), but assembling "
                "distance facts from free text is a deferred distance-normalization "
                "unit; unit 3k classifies only scale + BBL, so no distance fact is "
                "fabricated here."
            ),
            "bytes": _one_page_pdf(
                b"BT /F1 12 Tf 100 700 Td (COURSE 1: 100.00 FEET) Tj "
                b"100 680 Td (COURSE 2: 30.5 METERS) Tj ET"
            ),
        },
        {
            "file": "SVY07_decimal_ambiguity.pdf",
            "fixture_id": "SVY07",
            "category": "decimal_ambiguities",
            "format": "born_digital_pdf",
            "builder": "_one_page_pdf(embedded_text)",
            "extraction_status": "deferred-to-distance/bearing-normalization-unit",
            "supported_scenarios": ["SB-S3"],
            "purpose": (
                "A value written with ambiguous decimal/thousands separators "
                "(1,234.5 vs 1.234,5) that must never be silently disambiguated. "
                "Numeric distance/bearing normalization is the deferred normalization "
                "unit's job (fail-closed on ambiguity); 3k assembles no numeric distance "
                "fact from this text."
            ),
            "bytes": _one_page_pdf(
                b"BT /F1 12 Tf 100 700 Td (DIST 1,234.5) Tj "
                b"100 680 Td (ALT 1.234,5) Tj ET"
            ),
        },
        {
            "file": "SVY08_conflicting_scale.pdf",
            "fixture_id": "SVY08",
            "category": "conflicting_dimensions",
            "format": "born_digital_pdf",
            "builder": "_one_page_pdf(embedded_text)",
            "extraction_status": "live-embedded-text-extraction",
            "supported_scenarios": ["SB-S3"],
            "purpose": (
                "Two conflicting scale statements (1:240 and 1:480) in one document. Unit "
                "3k assembles two scale_statement facts and the deterministic "
                "scale_consistency check FAILS, routing the document to needs_review "
                "(never a silent pass) — a live SB-S3 fail-closed path."
            ),
            "bytes": _one_page_pdf(
                b"BT /F1 12 Tf 100 700 Td (1:240) Tj 100 680 Td (1:480) Tj ET"
            ),
        },
        {
            "file": "SVY09_incomplete_boundary.pdf",
            "fixture_id": "SVY09",
            "category": "incomplete_boundaries",
            "format": "vector_pdf",
            "builder": "_one_page_pdf(vector_ops)",
            "extraction_status": "deferred-to-boundary-reconstruction-unit",
            "supported_scenarios": ["SB-S3"],
            "purpose": (
                "An open (non-closing) polyline of three straight segments — a partial "
                "boundary. The segments decode via vector_object_extraction, but "
                "boundary closure / lot-area reconstruction (and the tax-lot AREA "
                "cross-check that follows it) is a deferred reconstruction unit, so no "
                "boundary/area fact is reconstructed here."
            ),
            "bytes": _one_page_pdf(b"10 10 m 110 10 l 110 90 l S"),
        },
        {
            "file": "SVY10_multipage_survey.pdf",
            "fixture_id": "SVY10",
            "category": "multi_page",
            "format": "born_digital_pdf",
            "builder": "_two_page_pdf(embedded_text, embedded_text)",
            "extraction_status": "live-embedded-text-extraction",
            "supported_scenarios": ["SB-S1"],
            "purpose": (
                "A two-page survey: the scale statement on page 1 and the subject BBL on "
                "page 2. The decoder returns both DecodedPages in order and 3k assembles "
                "one fact per page — proving multi-page decode, not a page-1-only "
                "shortcut."
            ),
            "bytes": _two_page_pdf(
                b"BT /F1 12 Tf 100 700 Td (1:240) Tj ET",
                b"BT /F1 12 Tf 100 700 Td (%s) Tj ET" % SUBJECT_BBL.encode("ascii"),
            ),
        },
        {
            "file": "SVY11_wrong_bbl.pdf",
            "fixture_id": "SVY11",
            "category": "wrong_address",
            "format": "born_digital_pdf",
            "builder": "_one_page_pdf(embedded_text)",
            "extraction_status": "live-embedded-text-extraction",
            "supported_scenarios": ["SB-S7"],
            "purpose": (
                "A well-formed survey whose stated BBL (3001230045) does NOT match the "
                "subject property. The address_bbl_match check fails and the document "
                "routes to needs_review with the typed wrong-address routing value — "
                "never silently ingested (SB-S7)."
            ),
            "bytes": _one_page_pdf(
                b"BT /F1 12 Tf 100 700 Td (1:240) Tj 100 680 Td (%s) Tj ET"
                % WRONG_BBL.encode("ascii")
            ),
        },
        {
            "file": "SVY12_exe_renamed_as_pdf.pdf",
            "fixture_id": "SVY12",
            "category": "malicious_oversized",
            "format": "octet-stream (PE executable)",
            "builder": "EXE_BYTES (test_gate T01)",
            "extraction_status": "live-S1-gate-rejected",
            "supported_scenarios": ["SB-S2"],
            "purpose": (
                "Threat T01: a PE executable (MZ header) renamed with a .pdf extension. "
                "The S1 content sniff recognizes it is not a PDF and "
                "check_extension_matches raises the typed ExtensionMismatchError — "
                "content decides, never the extension."
            ),
            "bytes": EXE_BYTES,
        },
        {
            "file": "SVY13_html_renamed_as_tiff.tiff",
            "fixture_id": "SVY13",
            "category": "malicious_oversized",
            "format": "text/html",
            "builder": "HTML_BYTES (test_gate T02)",
            "extraction_status": "live-S1-gate-rejected",
            "supported_scenarios": ["SB-S2"],
            "purpose": (
                "Threat T02: an HTML document renamed with a .tiff extension. Its bytes "
                "sniff as unrecognized (never guessed) and check_extension_matches "
                "raises the typed ExtensionMismatchError for the declared tiff extension."
            ),
            "bytes": HTML_BYTES,
        },
        {
            "file": "SVY14_oversize_sentinel.pdf",
            "fixture_id": "SVY14",
            "category": "malicious_oversized",
            "format": "born_digital_pdf",
            "builder": "_one_page_pdf(embedded_text)",
            "extraction_status": "live-S1-streaming-cap (boundary tested in-memory)",
            "supported_scenarios": ["SB-S2"],
            "purpose": (
                "Threat T03 sentinel: oversize uploads are rejected by the S1 streaming "
                "byte cap (UploadTooLargeError at MAX_UPLOAD_BYTES + 1). A >50 MiB file "
                "is intentionally NOT committed (thin-client storage policy); this small "
                "valid PDF documents the category, and the cap boundary is proven "
                "in-memory in test_survey_fixture_pack.py and test_gate.py without "
                "allocating a 50 MiB fixture."
            ),
            "bytes": _one_page_pdf(b"BT /F1 12 Tf 100 700 Td (oversize sentinel) Tj ET"),
        },
    ]
    return plan


# --------------------------------------------------------------- MANIFEST


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def build_manifest(fixtures: list[dict]) -> dict:
    """Build the MANIFEST dict from the in-memory fixtures (no wall-clock, so the pack
    round-trips byte-identically)."""
    entries = []
    for fx in fixtures:
        entries.append(
            {
                "file": fx["file"],
                "fixture_id": fx["fixture_id"],
                "classification": "synthetic",
                "category": fx["category"],
                "format": fx["format"],
                "builder": fx["builder"],
                "extraction_status": fx["extraction_status"],
                "byte_size": len(fx["bytes"]),
                "sha256": _sha256(fx["bytes"]),
                "purpose": fx["purpose"],
                "supported_scenarios": fx["supported_scenarios"],
            }
        )
    return {
        "manifest_version": 1,
        "task": TASK,
        "pack": "survey_documents",
        "classification": "all-synthetic",
        "source": (
            "No live official source exists for private survey documents; every fixture "
            "is deterministically synthesized by build_fixture_pack.py. No real client "
            "survey, captured official response, or private document is present."
        ),
        "generated_by": "build_fixture_pack.py",
        "digest_algorithm": "sha256:<hex> over the exact committed fixture bytes",
        "categories": sorted({fx["category"] for fx in fixtures}),
        "fixtures": entries,
    }


def _write(path: Path, data: bytes) -> None:
    path.write_bytes(data)
    print(f"wrote {path.name} ({len(data)} bytes)")


def main() -> None:
    fixtures = generate_fixtures()
    for fx in fixtures:
        _write(FIXTURE_DIR / fx["file"], fx["bytes"])
    manifest = build_manifest(fixtures)
    manifest_bytes = (
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    _write(FIXTURE_DIR / "MANIFEST.json", manifest_bytes)
    print(f"wrote MANIFEST.json ({len(fixtures)} fixtures)")


if __name__ == "__main__":
    main()
