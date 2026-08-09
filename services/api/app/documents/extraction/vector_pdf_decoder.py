"""Concrete vector/embedded-text PDF decoder — the first :class:`DecoderSeam`
implementation (M2-T015 unit 3k; architecture §§3-5, SB-S1).

This is the concrete stage-S4 decoder for the digitally-authored PDF routes
(format-policy rows 1-2: born-digital and vector PDF). It turns the immutable
original's exact bytes into structured, page-scoped extraction primitives by
composing the in-repo strict-subset reader built in units 3i-3a..3j:

    read_pdf_container(bytes)  -> ordered pages with decoded /Contents
    interpret_content(bytes)   -> device-space segments / rects / text runs

No third-party PDF library is used, no byte is executed, and the reader is a
pure function of bytes (units 3i docstrings). The decoder therefore inherits the
reader's fail-closed doctrine exactly:

* **Refusal is a value, never an exception.** Every reader/interpreter refusal is
  a frozen :class:`~app.documents.extraction.pdf_lexer.PdfSyntaxError` (malformed
  structure) or :class:`~app.documents.extraction.pdf_xref.UnsupportedPdfFeature`
  (a well-formed construct outside the strict survey subset — curves, images,
  rotated/sheared transforms, oversized streams). ``decode`` returns such a
  refusal as the SOLE element of its returned sequence rather than raising, so a
  caller in the isolated worker never crashes on hostile input and always has a
  typed reason to route to review.
* **All or nothing.** A refusal on ANY page fails the whole decode: the returned
  sequence is exactly ``(refusal,)`` and carries no partial page. A document that
  uses a feature outside the strict subset is not half-decoded and silently
  trusted — it routes to human review as one unit.

The decode path is reachable ONLY through
:func:`app.documents.extraction.routing.begin_extraction_job`, which consults the
fail-closed parser-isolation gate (:func:`app.documents.isolation.require_isolation`)
FIRST and hands out a decoder only inside an :class:`ExtractionJobAuthorized`; on
an unproven boundary no decoder is ever obtained (``isolation_unavailable``,
architecture §5). This module holds NO isolation-bypass affordance and consults no
ambient state: it decodes exactly the bytes it is given, and nothing else.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.documents.extraction.pdf_container import read_pdf_container
from app.documents.extraction.pdf_content import PageContent, interpret_content
from app.documents.extraction.pdf_lexer import PdfSyntaxError
from app.documents.extraction.pdf_xref import UnsupportedPdfFeature

__all__ = [
    "DecodedPage",
    "PdfDecodeRefusal",
    "VectorPdfDecoder",
    "pdf_decode_refusal",
]

#: The union of the reader's two frozen refusal values. A decode failure is always
#: one of these (never an exception), matching the strict-subset reader's contract.
PdfDecodeRefusal = PdfSyntaxError | UnsupportedPdfFeature


@dataclass(frozen=True)
class DecodedPage:
    """One decoded page: its depth-first page index, resolved ``/MediaBox`` (points),
    and the fully interpreted device-space :class:`PageContent` (segments, rects, text
    runs). A structured extraction primitive — never itself a survey fact; deterministic
    fact assembly (:mod:`app.documents.extraction.survey_pipeline`) is a separate stage.
    """

    index: int
    media_box: tuple[float, float, float, float]
    content: PageContent


class VectorPdfDecoder:
    """Concrete :class:`~app.documents.extraction.routing.DecoderSeam` for the
    digitally-authored PDF routes, backed by the in-repo strict-subset reader.

    Stateless and reusable: a single shared instance is safe because ``decode`` is a
    pure function of its ``original_bytes`` argument (the reader mutates no globals,
    performs no I/O, and consults no clock or randomness).
    """

    def decode(self, original_bytes: bytes) -> Sequence[object]:
        """Decode the exact original bytes into a sequence of :class:`DecodedPage`.

        Returns ``tuple[DecodedPage, ...]`` (possibly empty for a zero-page document)
        on success. On ANY reader or interpreter refusal — including a non-bytes input
        — returns the one-element sequence ``(refusal,)`` whose sole element is the
        frozen :class:`PdfSyntaxError` / :class:`UnsupportedPdfFeature`; use
        :func:`pdf_decode_refusal` to test for it. Never raises: hostile or malformed
        input is a routine typed outcome the isolated worker surfaces, not a crash.
        """
        if not isinstance(original_bytes, (bytes, bytearray, memoryview)):
            return (
                PdfSyntaxError(
                    0,
                    "raw original document bytes",
                    f"got {type(original_bytes).__name__}; a decoder consumes only the "
                    "exact stored original bytes",
                ),
            )
        document = read_pdf_container(bytes(original_bytes))
        if isinstance(document, (PdfSyntaxError, UnsupportedPdfFeature)):
            return (document,)
        decoded: list[DecodedPage] = []
        for page in document.pages:
            content = interpret_content(page.content)
            if isinstance(content, (PdfSyntaxError, UnsupportedPdfFeature)):
                # Fail-closed: one page outside the strict subset fails the whole
                # decode — no partial, silently-trusted document is ever produced.
                return (content,)
            decoded.append(
                DecodedPage(index=page.index, media_box=page.media_box, content=content)
            )
        return tuple(decoded)


def pdf_decode_refusal(primitives: Sequence[object]) -> PdfDecodeRefusal | None:
    """Return the decode refusal carried by ``primitives``, or ``None`` on success.

    :meth:`VectorPdfDecoder.decode` signals refusal as a one-element sequence whose
    sole element is a frozen :class:`PdfSyntaxError` / :class:`UnsupportedPdfFeature`.
    A successful single-page decode is ``(DecodedPage,)`` — also length 1 — so the
    element TYPE, not the length, discriminates: only a refusal value is returned here.
    """
    if len(primitives) == 1 and isinstance(
        primitives[0], (PdfSyntaxError, UnsupportedPdfFeature)
    ):
        return primitives[0]
    return None
