#!/usr/bin/env python3
"""Generate and maintain web-derived risk records.

Behavior:
- Fetches safety guidance sources.
- Auto-discovers additional relevant sources from fetched pages.
- Appends newly found risk records into web-risk-database.json by default.
- Supports --force to rebuild web-derived records from scratch.
"""

from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import argparse
import json
from pathlib import Path
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

WORKSPACE_FILE = Path(__file__).with_name("web-risk-database.json")
DATAPOL_FILE = Path(__file__).with_name("datapol.json")
DATAPOL_JS_FILE = Path(__file__).with_name("datapol-data.js")
SOURCE_REGISTRY_FILE = Path(__file__).with_name("web-source-registry.json")
TIMEOUT_SECONDS = 8
MAX_DISCOVERED_SOURCES = 60
MAX_SOURCES_PER_RUN = 8

BASE_SOURCES = [
    {
        "name": "OSHA Highway Work Zones",
        "url": "https://www.osha.gov/highway-workzones",
        "kind": "base",
    },
    {
        "name": "OSHA MUTCD Part 6",
        "url": "https://www.osha.gov/highway-workzones/mutcd-part6",
        "kind": "base",
    },
    {
        "name": "FHWA MUTCD Part 6",
        "url": "https://mutcd.fhwa.dot.gov/htm/2009/part6/part6_toc.htm",
        "kind": "base",
    },
    {
        "name": "FHWA Work Zones",
        "url": "https://highways.dot.gov/safety/other/work-zone/work-zones",
        "kind": "base",
    },
    {
        "name": "FHWA Ops Work Zone Program",
        "url": "https://ops.fhwa.dot.gov/wz/",
        "kind": "base",
    },
]

SOURCE_FALLBACKS = {
    "https://highways.dot.gov/safety/other/work-zone/work-zones": [
        "https://highways.dot.gov/safety/other/work-zone",
        "https://www.fhwa.dot.gov/workzones/",
    ],
    "https://ops.fhwa.dot.gov/wz/": [
        "https://ops.fhwa.dot.gov/wz/resources/",
    ],
}

ALLOWED_SOURCE_DOMAINS = (
    "osha.gov",
    "dot.gov",
    "fhwa.dot.gov",
    "highways.dot.gov",
    "ops.fhwa.dot.gov",
    "mutcd.fhwa.dot.gov",
    "safety.fhwa.dot.gov",
)

SOURCE_DISCOVERY_KEYWORDS = (
    "work-zone",
    "workzone",
    "temporary-traffic",
    "traffic-control",
    "mutcd",
    "highway-workzones",
    "barrier",
    "crash-cushion",
    "roadway",
    "safety",
)

GUIDANCE_INCLUDE_FRAGMENTS = (
    "highway-workzones",
    "work-zone",
    "workzone",
    "mutcd",
    "temporary-traffic",
    "traffic-control",
    "workersafety",
    "worker-safety",
    "barrier",
    "crash-cushion",
    "guidance",
    "guide",
    "manual",
    "standard",
    "standards",
    "bulletin",
    "bulletins",
    "training",
    "final-rule",
    "rule",
    "policy",
)

GUIDANCE_EXCLUDE_FRAGMENTS = (
    "/resources",
    "/resource",
    "/sitemap",
    "/site-map",
    "/search",
    "/contact",
    "/about",
    "/news",
    "/newsroom",
    "/press",
    "/media",
    "/careers",
    "/staff",
    "/foia",
    "/privacy",
    "/budget",
    "/civil-rights",
    "/facebook",
    "/twitter",
    "/instagram",
    "/youtube",
    "/linkedin",
    "/flickr",
    "/res-outside",
    "/res-notices",
    "/res-resources",
    "/safety-management",
)

STRICT_DISCOVERY_WHITELIST = (
    "https://www.osha.gov/highway-workzones",
    "https://www.osha.gov/highway-workzones/mutcd-part6",
    "https://www.osha.gov/highway-workzones/standards",
    "https://www.osha.gov/highway-workzones/bulletins",
    "https://www.osha.gov/highway-workzones/training",
    "https://www.osha.gov/highway-workzones/final-rule",
    "https://www.osha.gov/highway-workzones/fhwa-safety",
    "https://www.osha.gov/highway-workzones/mutcd",
    "https://mutcd.fhwa.dot.gov/htm/2009/part6/part6_toc.htm",
    "https://mutcd.fhwa.dot.gov/res-policy.htm",
    "https://ops.fhwa.dot.gov/wz",
    "https://ops.fhwa.dot.gov/workersafety/index.htm",
    "https://highways.dot.gov/safety/other/work-zone/work-zones",
    "https://safety.fhwa.dot.gov/wz",
)

STRICT_DISCOVERY_WHITELIST_SET = set(STRICT_DISCOVERY_WHITELIST)

# Fallback guidance signals used when a source blocks scraping.
FALLBACK_SIGNAL_TEXT = """
struck-by hazards from passing traffic and construction vehicles
falls electrical caught between
temporary traffic control zones advance warning transition activity area termination area
pedestrian and worker safety accessibility considerations
flagger control high-visibility safety apparel
portable changeable message signs arrow boards channelizing devices
temporary traffic barriers crash cushions
detours and diversions lane closures merge tapers
queue management and work zone mobility
""".strip().lower()

RISK_TEMPLATES = [
    {
        "catID": "TMG",
        "hazard": "Live-lane Worker Struck-By Due to Intrusion",
        "mechanism": "Passing traffic or site vehicles enter the activity area because separation and warning controls are insufficient.",
        "impact": "Severe worker injury/fatality and immediate site shutdown.",
        "initialLikelihood": "Likely (4)",
        "initialConsequence": "Catastrophic (5)",
        "residualLikelihood": "Unlikely (2)",
        "residualConsequence": "Major (4)",
        "riskOwner": "Traffic Control Supervisor",
        "action": "Strengthen positive protection, buffer controls, and intrusion response procedures before shift start.",
        "reference": "OSHA Highway Work Zones; MUTCD Part 6D",
        "triggers": ["struck-by", "worker safety", "activity area"],
        "mitigations": [
            "Install positive protection and maintain compliant lateral offsets in active work areas.",
            "Deploy shadow vehicles/TMA where exposure to live traffic exists.",
            "Brief crews on emergency intrusion response and safe refuge points each shift.",
        ],
    },
    {
        "catID": "TMG",
        "hazard": "Queue-End Rear-End Collision in Work Zone Approach",
        "mechanism": "Insufficient advance warning and speed harmonization causes late braking into stopped queues.",
        "impact": "High-energy multi-vehicle crash near the work zone.",
        "initialLikelihood": "Likely (4)",
        "initialConsequence": "Major (4)",
        "residualLikelihood": "Unlikely (2)",
        "residualConsequence": "Moderate (3)",
        "riskOwner": "Traffic Engineer",
        "action": "Implement queue detection triggers and dynamic warning treatment on approaches.",
        "reference": "FHWA Work Zone Management Program; MUTCD 6C",
        "triggers": ["advance warning", "transition area", "queue", "mobility"],
        "mitigations": [
            "Add upstream queue warning and variable message boards based on observed queue length.",
            "Re-check taper length and warning sign spacing against operating speed.",
            "Adjust staging windows to avoid peak-period queue growth where practical.",
        ],
    },
    {
        "catID": "TMG",
        "hazard": "Flagger Visibility and Positioning Failure",
        "mechanism": "Flagger station placement and conspicuity do not provide adequate sight distance for approaching drivers.",
        "impact": "Delayed driver compliance, unsafe stop maneuvers, and worker exposure.",
        "initialLikelihood": "Possible (3)",
        "initialConsequence": "Major (4)",
        "residualLikelihood": "Rare (1)",
        "residualConsequence": "Moderate (3)",
        "riskOwner": "Traffic Control Supervisor",
        "action": "Audit flagger station placement each shift and enforce high-visibility apparel requirements.",
        "reference": "MUTCD Chapter 6E; OSHA Highway Work Zones",
        "triggers": ["flagger", "high-visibility", "sight distance"],
        "mitigations": [
            "Position flagger stations to preserve stopping sight distance and clear escape routes.",
            "Use compliant STOP/SLOW devices and high-visibility PPE for all flaggers.",
            "Apply radio protocol checks for handover periods and low-light operations.",
        ],
    },
    {
        "catID": "BDR",
        "hazard": "Temporary Barrier Gap at Transition or Terminal",
        "mechanism": "Mismatch or discontinuity at temporary barrier transitions creates a non-redirective snag point.",
        "impact": "Vehicle penetration or severe redirection failure into workers/hazards.",
        "initialLikelihood": "Possible (3)",
        "initialConsequence": "Catastrophic (5)",
        "residualLikelihood": "Unlikely (2)",
        "residualConsequence": "Major (4)",
        "riskOwner": "Barrier Designer",
        "action": "Verify transition compatibility and terminal details during install hold-point inspections.",
        "reference": "MUTCD 6F.85 Temporary Traffic Barriers; FHWA Work Zones",
        "triggers": ["temporary traffic barriers", "crash cushions", "terminal"],
        "mitigations": [
            "Inspect every transition and end treatment against manufacturer and project requirements.",
            "Replace damaged or non-compatible transition components before opening to traffic.",
            "Confirm working width and barrier alignment with surveyed setout checks.",
        ],
    },
    {
        "catID": "TMG",
        "hazard": "Pedestrian Detour Non-Compliance and DDA Conflict",
        "mechanism": "Temporary footpath/crossing arrangement lacks continuity, detectable edging, or accessible routing.",
        "impact": "Pedestrians enter live traffic space or trip/fall through non-compliant detours.",
        "initialLikelihood": "Possible (3)",
        "initialConsequence": "Major (4)",
        "residualLikelihood": "Rare (1)",
        "residualConsequence": "Moderate (3)",
        "riskOwner": "Site Supervisor",
        "action": "Approve and monitor pedestrian detours daily with accessibility checks.",
        "reference": "MUTCD 6D and 6F.74",
        "triggers": ["pedestrian", "accessibility", "crosswalk", "detectable edging"],
        "mitigations": [
            "Provide continuous protected pedestrian pathways with compliant surface and width.",
            "Install detectable edging and clear detour wayfinding at each closure point.",
            "Inspect detour condition after weather and shift changes.",
        ],
    },
    {
        "catID": "TMG",
        "hazard": "Portable Device Failure (PCMS/Arrow Board) During Stage",
        "mechanism": "Power loss, misconfiguration, or poor placement of temporary warning devices reduces driver guidance.",
        "impact": "Driver confusion, late merges, and elevated side-swipe/rear-end crash potential.",
        "initialLikelihood": "Possible (3)",
        "initialConsequence": "Major (4)",
        "residualLikelihood": "Rare (1)",
        "residualConsequence": "Moderate (3)",
        "riskOwner": "Traffic Control Supervisor",
        "action": "Add pre-open functionality checks and redundancy for all portable warning devices.",
        "reference": "MUTCD 6F.60 and 6F.61",
        "triggers": ["portable changeable message signs", "arrow boards"],
        "mitigations": [
            "Run pre-start checks for visibility, battery/solar status, and message accuracy.",
            "Position devices to meet approach visibility and lane guidance requirements.",
            "Maintain spare devices for rapid replacement during active shifts.",
        ],
    },
    {
        "catID": "ETT",
        "hazard": "Incorrect Taper Length for Posted Speed",
        "mechanism": "Temporary taper geometry is undersized for approach speed and does not provide sufficient merge distance.",
        "impact": "Abrupt lane changes, side-swipes, and loss-of-control events at merge points.",
        "initialLikelihood": "Possible (3)",
        "initialConsequence": "Major (4)",
        "residualLikelihood": "Rare (1)",
        "residualConsequence": "Moderate (3)",
        "riskOwner": "Design Engineer",
        "action": "Recalculate taper geometry against current speed environment before deployment.",
        "reference": "MUTCD Table 6C-3 and 6C-4",
        "triggers": ["taper", "table 6c-3", "speed"],
        "mitigations": [
            "Verify taper calculations and field lengths against current speed and lane width.",
            "Update traffic control diagrams when speed environment or lane configuration changes.",
            "Use independent verification sign-off before opening altered staging.",
        ],
    },
    {
        "catID": "BDR",
        "hazard": "Crash Cushion Not Restored After Impact",
        "mechanism": "Impact attenuator remains in compromised condition after strike, reducing energy absorption performance.",
        "impact": "Increased crash severity for subsequent impacts.",
        "initialLikelihood": "Possible (3)",
        "initialConsequence": "Major (4)",
        "residualLikelihood": "Rare (1)",
        "residualConsequence": "Moderate (3)",
        "riskOwner": "Maintenance Lead",
        "action": "Set maximum response times and inspection logs for impact device reset/replacement.",
        "reference": "MUTCD 6F.86 Crash Cushions",
        "triggers": ["crash cushions", "impact"],
        "mitigations": [
            "Inspect all cushions after reported or suspected impact events.",
            "Quarantine damaged units and replace cartridges/modules before reopening lanes.",
            "Track repair turnaround and escalate overdue resets to site leadership.",
        ],
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_html(raw_html: str) -> str:
    no_script = re.sub(r"<script[\s\S]*?</script>", " ", raw_html, flags=re.IGNORECASE)
    no_style = re.sub(r"<style[\s\S]*?</style>", " ", no_script, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", no_style)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return ""

    host = (parsed.netloc or "").lower()
    scheme = parsed.scheme
    if scheme == "http" and any(host.endswith(domain) for domain in ALLOWED_SOURCE_DOMAINS):
        scheme = "https"

    clean = parsed._replace(fragment="", query="")
    clean = clean._replace(scheme=scheme, netloc=host)
    text = clean.geturl()
    return text[:-1] if text.endswith("/") else text


def is_allowed_source_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    return any(host.endswith(domain) for domain in ALLOWED_SOURCE_DOMAINS)


def is_discovery_candidate(url: str) -> bool:
    if not is_allowed_source_url(url):
        return False

    normalized = normalize_url(url)
    if normalized in STRICT_DISCOVERY_WHITELIST:
        return True

    parsed = urlparse(url)
    lowered_path = (parsed.path or "").lower()
    blocked_suffixes = (
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".xml",
        ".rss",
        ".pdf",
    )
    if lowered_path.endswith(blocked_suffixes):
        return False

    lowered = url.lower()
    if any(fragment in lowered for fragment in GUIDANCE_EXCLUDE_FRAGMENTS):
        return False

    has_guidance_fragment = any(fragment in lowered for fragment in GUIDANCE_INCLUDE_FRAGMENTS)
    has_discovery_keyword = any(keyword in lowered for keyword in SOURCE_DISCOVERY_KEYWORDS)
    return has_guidance_fragment and has_discovery_keyword and normalized in STRICT_DISCOVERY_WHITELIST


def fetch_raw_html(url: str) -> tuple[str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RiskAnalysisBot/1.2",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "close",
        },
    )
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        body = response.read().decode("utf-8", errors="ignore")
        final_url = response.geturl()
    return body, final_url


def fetch_source_with_fallbacks(source_url: str) -> tuple[str, str, str]:
    candidates = [source_url, *SOURCE_FALLBACKS.get(source_url, [])]
    last_error: Exception | None = None

    for candidate in candidates:
        try:
            raw_html, final_url = fetch_raw_html(candidate)
            return _strip_html(raw_html), normalize_url(final_url) or normalize_url(candidate), raw_html
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc

    if last_error is None:
        raise RuntimeError("No source candidates were available")
    raise last_error


def extract_links(raw_html: str, base_url: str) -> list[str]:
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', raw_html, flags=re.IGNORECASE)
    out: list[str] = []
    seen: set[str] = set()

    for href in hrefs:
        absolute = urljoin(base_url, href)
        norm = normalize_url(absolute)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)

    return out


def load_registry() -> dict[str, Any]:
    if not SOURCE_REGISTRY_FILE.exists():
        return {"metadata": {"updatedAt": now_iso()}, "sources": []}

    try:
        payload = json.loads(SOURCE_REGISTRY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"metadata": {"updatedAt": now_iso()}, "sources": []}

    if not isinstance(payload, dict):
        return {"metadata": {"updatedAt": now_iso()}, "sources": []}

    if "sources" not in payload or not isinstance(payload["sources"], list):
        payload["sources"] = []
    if "metadata" not in payload or not isinstance(payload["metadata"], dict):
        payload["metadata"] = {}

    cleaned_by_url: dict[str, dict[str, Any]] = {}
    for row in payload.get("sources", []):
        if not isinstance(row, dict):
            continue
        url = normalize_url(str(row.get("url", "")))
        if not url:
            continue

        kind = str(row.get("kind", "discovered"))
        if kind != "base" and not is_discovery_candidate(url):
            continue

        normalized_row = {
            "name": row.get("name") or "Discovered Source",
            "url": url,
            "kind": "base" if kind == "base" else "discovered",
            "addedAt": row.get("addedAt") or now_iso(),
            "lastStatus": row.get("lastStatus") or "unknown",
            "lastSeen": row.get("lastSeen") or now_iso(),
            "discoveredFrom": row.get("discoveredFrom") or "",
        }

        existing = cleaned_by_url.get(url)
        if existing is None:
            cleaned_by_url[url] = normalized_row
            continue

        if normalized_row["kind"] == "base":
            cleaned_by_url[url] = normalized_row

    payload["sources"] = list(cleaned_by_url.values())

    return payload


def save_registry(registry: dict[str, Any]) -> None:
    registry.setdefault("metadata", {})["updatedAt"] = now_iso()
    sources = registry.get("sources", [])
    if isinstance(sources, list):
        registry["sources"] = [
            row for row in sources
            if isinstance(row, dict)
            and normalize_url(str(row.get("url", ""))) in STRICT_DISCOVERY_WHITELIST_SET
        ]
    SOURCE_REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def upsert_source(registry: dict[str, Any], source: dict[str, Any]) -> None:
    sources: list[dict[str, Any]] = registry.setdefault("sources", [])
    url = normalize_url(str(source.get("url", "")))
    if not url:
        return
    if url not in STRICT_DISCOVERY_WHITELIST_SET and not any(normalize_url(s["url"]) == url for s in BASE_SOURCES):
        return

    for row in sources:
        if normalize_url(str(row.get("url", ""))) == url:
            # Base sources should stay marked as base if re-encountered.
            incoming_kind = source.get("kind")
            if incoming_kind == "base":
                row["kind"] = "base"
            for key in ("name", "kind", "lastStatus", "lastSeen", "discoveredFrom"):
                value = source.get(key)
                if value:
                    row[key] = value
            return

    sources.append(
        {
            "name": source.get("name") or "Discovered Source",
            "url": url,
            "kind": source.get("kind") or "discovered",
            "addedAt": source.get("addedAt") or now_iso(),
            "lastStatus": source.get("lastStatus") or "new",
            "lastSeen": source.get("lastSeen") or now_iso(),
            "discoveredFrom": source.get("discoveredFrom") or "",
        }
    )


def seed_registry_with_base_sources(registry: dict[str, Any]) -> None:
    for source in BASE_SOURCES:
        upsert_source(registry, source)
    for url in STRICT_DISCOVERY_WHITELIST:
        if any(normalize_url(source["url"]) == url for source in BASE_SOURCES):
            continue
        upsert_source(
            registry,
            {
                "name": "Whitelisted guidance source",
                "url": url,
                "kind": "discovered",
                "lastStatus": "whitelisted",
                "lastSeen": now_iso(),
            },
        )


def discover_sources(raw_html: str, from_url: str) -> list[dict[str, Any]]:
    discovered: list[dict[str, Any]] = []
    for link in extract_links(raw_html, from_url):
        if not is_discovery_candidate(link):
            continue
        discovered.append(
            {
                "name": f"Discovered from {urlparse(from_url).netloc}",
                "url": link,
                "kind": "discovered",
                "discoveredFrom": from_url,
                "lastStatus": "discovered",
                "lastSeen": now_iso(),
            }
        )
    return discovered


def get_active_sources(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows = registry.get("sources", [])
    if not isinstance(rows, list):
        return BASE_SOURCES[:]

    base = [r for r in rows if str(r.get("kind", "")) == "base"]
    discovered = [r for r in rows if str(r.get("kind", "")) != "base"]

    discovered = sorted(
        discovered,
        key=lambda r: str(r.get("lastSeen", "")),
        reverse=True,
    )[:MAX_DISCOVERED_SOURCES]

    active = base + discovered
    return active[:MAX_SOURCES_PER_RUN]


def load_existing_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]

    if isinstance(payload, dict):
        risks = payload.get("risks", [])
        if isinstance(risks, list):
            return [p for p in risks if isinstance(p, dict)]

    return []


def template_triggered(template: dict[str, Any], text_blob: str) -> bool:
    return any(trigger in text_blob for trigger in template["triggers"])


def template_signal_count(template: dict[str, Any], text_blob: str) -> int:
    return sum(1 for trigger in template["triggers"] if trigger in text_blob)


def rank_templates(selected_templates: list[dict[str, Any]], text_blob: str) -> list[dict[str, Any]]:
    return sorted(
        selected_templates,
        key=lambda tpl: (
            template_signal_count(tpl, text_blob),
            len(tpl.get("triggers", [])),
            str(tpl.get("hazard", "")),
        ),
        reverse=True,
    )


def select_templates(text_blob: str) -> list[dict[str, Any]]:
    selected = [tpl for tpl in RISK_TEMPLATES if template_triggered(tpl, text_blob)]
    if len(selected) < 5:
        selected = RISK_TEMPLATES[:]
    return selected


def build_id(cat_id: str, index: int) -> str:
    return f"WEB-{cat_id}-{index:03d}"


def build_records(
    selected_templates: list[dict[str, Any]],
    existing_ids: set[str],
    text_blob: str,
    force: bool,
) -> list[dict[str, Any]]:
    cat_counts = {"SPA": 0, "BDR": 0, "TMG": 0, "ETT": 0}
    out: list[dict[str, Any]] = []
    submitted_at = now_iso()

    for template in rank_templates(selected_templates, text_blob):
        cat_id = template["catID"]
        cat_counts[cat_id] = cat_counts.get(cat_id, 0) + 1
        rec_id = build_id(cat_id, cat_counts[cat_id])

        if (not force) and rec_id in existing_ids:
            continue

        evidence_hits = [trigger for trigger in template["triggers"] if trigger in text_blob]

        out.append(
            {
                "id": rec_id,
                "catID": cat_id,
                "hazard": template["hazard"],
                "mechanism": template["mechanism"],
                "impact": template["impact"],
                "initialLikelihood": template["initialLikelihood"],
                "initialConsequence": template["initialConsequence"],
                "residualLikelihood": template["residualLikelihood"],
                "residualConsequence": template["residualConsequence"],
                "riskOwner": template["riskOwner"],
                "action": template["action"],
                "reference": template["reference"],
                "mitigations": template["mitigations"],
                "evidenceSignals": evidence_hits,
                "submittedBy": "Web Risk Analyzer",
                "submittedAt": submitted_at,
                "source": "web-analysis",
            }
        )

    return out


def merge_records(
    existing_records: list[dict[str, Any]],
    generated_records: list[dict[str, Any]],
    force: bool,
) -> list[dict[str, Any]]:
    if force:
        # Keep any non-web-analysis records and replace all web-analysis rows.
        static_records = [r for r in existing_records if str(r.get("source", "")) != "web-analysis"]
        return static_records + generated_records

    by_id: dict[str, dict[str, Any]] = {}
    for row in existing_records:
        rid = str(row.get("id", "")).strip()
        if not rid:
            continue
        by_id[rid] = row

    for row in generated_records:
        rid = str(row.get("id", "")).strip()
        if not rid:
            continue
        if rid not in by_id:
            by_id[rid] = row

    return list(by_id.values())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate web-derived risk records.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild web-analysis records from templates and overwrite old web-analysis rows.",
    )
    return parser.parse_args()


def run() -> int:
    args = parse_args()

    registry = load_registry()
    seed_registry_with_base_sources(registry)

    scraped_text_parts: list[str] = [FALLBACK_SIGNAL_TEXT]
    source_status: list[dict[str, str]] = []

    active_sources = get_active_sources(registry)

    for source in active_sources:
        source_name = str(source.get("name", "Unnamed source"))
        source_url = normalize_url(str(source.get("url", "")))
        if not source_url:
            continue

        try:
            text_blob, used_url, raw_html = fetch_source_with_fallbacks(source_url)
            scraped_text_parts.append(text_blob)
            status = "ok"
            if normalize_url(used_url) != source_url:
                status = f"ok (fallback/redirect used: {used_url})"

            source_status.append({"name": source_name, "url": source_url, "status": status})
            upsert_source(
                registry,
                {
                    "name": source_name,
                    "url": source_url,
                    "kind": source.get("kind") or "discovered",
                    "lastStatus": status,
                    "lastSeen": now_iso(),
                },
            )

            # Expand source list only from trusted base seeds to avoid uncontrolled crawl growth.
            if str(source.get("kind", "")) == "base":
                for discovered in discover_sources(raw_html, used_url):
                    upsert_source(registry, discovered)

        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            status = f"unavailable: {type(exc).__name__}"
            source_status.append({"name": source_name, "url": source_url, "status": status})
            upsert_source(
                registry,
                {
                    "name": source_name,
                    "url": source_url,
                    "kind": source.get("kind") or "discovered",
                    "lastStatus": status,
                    "lastSeen": now_iso(),
                },
            )

    save_registry(registry)

    combined_text = " ".join(scraped_text_parts)
    selected_templates = select_templates(combined_text)

    existing_records = load_existing_records(WORKSPACE_FILE)
    existing_ids = {str(r.get("id", "")).strip() for r in existing_records if isinstance(r, dict)}
    generated_records = build_records(selected_templates, existing_ids, combined_text, args.force)
    all_records = merge_records(existing_records, generated_records, args.force)

    payload = {
        "metadata": {
            "generatedAt": now_iso(),
            "method": "keyword-risk-signal-mapping",
            "sources": source_status,
            "sourceRegistryFile": SOURCE_REGISTRY_FILE.name,
            "recordCount": len(all_records),
            "newRecordsAdded": len(generated_records),
            "forcedRefresh": bool(args.force),
        },
        "risks": all_records,
    }

    WORKSPACE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Maintain a second synchronized output for downstream consumers expecting "datapol".
    datapol_payload = {
        "metadata": {
            "syncedAt": now_iso(),
            "source": WORKSPACE_FILE.name,
            "recordCount": len(all_records),
        },
        "risks": all_records,
    }
    DATAPOL_FILE.write_text(json.dumps(datapol_payload, indent=2), encoding="utf-8")
    DATAPOL_JS_FILE.write_text(
        "window.DATAPOL_SYNC_DATA = " + json.dumps(datapol_payload, indent=2) + ";\n",
        encoding="utf-8",
    )

    print(f"Total records in database: {len(all_records)}")
    print(f"New records added this run: {len(generated_records)}")
    print(f"Output file: {WORKSPACE_FILE.name}")
    print(f"Source registry: {SOURCE_REGISTRY_FILE.name}")
    print(f"Datapol sync file: {DATAPOL_FILE.name}")
    print(f"Datapol JS file: {DATAPOL_JS_FILE.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
