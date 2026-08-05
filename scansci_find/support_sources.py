from __future__ import annotations

import os
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

from scansci_find.adapters import HttpProvider, ProviderConfigurationError, normalize_doi


class UnpaywallProvider(HttpProvider):
    name = "unpaywall"

    def __init__(self, email: str = "") -> None:
        super().__init__()
        self.email = email

    def resolve_doi(self, doi: str) -> Dict[str, Any]:
        normalized = normalize_doi(doi)
        if not normalized:
            raise ValueError("doi must not be empty")
        email = (
            self.email
            or os.environ.get("UNPAYWALL_EMAIL")
            or os.environ.get("SCANSCI_FIND_CONTACT_EMAIL")
            or ""
        ).strip()
        if not email:
            raise ProviderConfigurationError("Unpaywall requires UNPAYWALL_EMAIL or SCANSCI_FIND_CONTACT_EMAIL")
        url = "https://api.unpaywall.org/v2/" + urllib.parse.quote(normalized, safe="") + "?" + urllib.parse.urlencode({"email": email})
        payload = self._json(url)
        best = payload.get("best_oa_location") or {}
        return {
            "status": "resolved",
            "source": "Unpaywall",
            "doi": normalized,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "is_oa": bool(payload.get("is_oa")),
            "oa_status": payload.get("oa_status") or "unknown",
            "pdf_url": best.get("url_for_pdf") or "",
            "landing_page_url": best.get("url_for_landing_page") or best.get("url") or "",
            "license": best.get("license") or "",
            "version": best.get("version") or "",
            "host_type": best.get("host_type") or "",
            "repository_institution": best.get("repository_institution") or "",
            "location_count": len(payload.get("oa_locations") or []),
            "data_standard": payload.get("data_standard"),
        }


def resolve_open_access(
    candidates: Iterable[Dict[str, Any]],
    *,
    provider: Optional[Any] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    provider = provider or UnpaywallProvider()
    rows = [dict(candidate) for candidate in candidates]
    selected = rows if limit is None else rows[: max(0, int(limit))]
    counts: Counter[str] = Counter()
    for candidate in selected:
        doi = normalize_doi(candidate.get("doi"))
        if not doi:
            report = {"status": "unsupported", "source": "Unpaywall", "message": "candidate has no DOI"}
        else:
            try:
                report = provider.resolve_doi(doi)
            except Exception as exc:
                report = {
                    "status": getattr(exc, "status", "error"),
                    "source": "Unpaywall",
                    "doi": doi,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
        candidate["oa_resolution"] = report
        counts[str(report.get("status") or "unknown")] += 1
        if report.get("status") == "resolved":
            links = dict(candidate.get("links") or {})
            if report.get("pdf_url") and not links.get("pdf"):
                links["pdf"] = report["pdf_url"]
            if report.get("landing_page_url") and not links.get("fulltext"):
                links["fulltext"] = report["landing_page_url"]
            candidate["links"] = links
            access = dict(candidate.get("access") or {})
            if report.get("is_oa"):
                access.update({"fulltext_hint": "oa", "requires_login": False, "requires_institution": False})
            access["oa_status"] = report.get("oa_status") or "unknown"
            access["license"] = report.get("license") or ""
            candidate["access"] = access
            support_records = list(candidate.get("support_records") or [])
            support_records.append({"source": "Unpaywall", "doi": doi, "status": report.get("status")})
            candidate["support_records"] = support_records
    return {
        "candidates": rows,
        "checked": len(selected),
        "unchecked": len(rows) - len(selected),
        "status_counts": dict(sorted(counts.items())),
        "oa_found": sum(1 for item in selected if (item.get("oa_resolution") or {}).get("is_oa")),
    }
