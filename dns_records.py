#!/usr/bin/env python3
"""Inventorie les enregistrements DNS publiquement accessibles d'un domaine."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

try:
    import dns.exception
    import dns.query
    import dns.resolver
    import dns.rdatatype
    import dns.zone
except ImportError:
    print(
        "Dépendance manquante : installez-la avec "
        "`python3 -m pip install -r requirements.txt`.",
        file=sys.stderr,
    )
    raise SystemExit(2)


# ANY est volontairement absent : de nombreux serveurs le refusent ou renvoient
# une réponse incomplète. Interroger chaque type donne un résultat plus fiable.
APEX_TYPES = (
    "A", "AAAA", "CAA", "CDNSKEY", "CDS", "CNAME", "DNSKEY", "DS", "HTTPS",
    "LOC", "MX", "NAPTR", "NS", "OPENPGPKEY", "PTR", "RP", "SMIMEA", "SOA",
    "SRV", "SSHFP", "SVCB", "TLSA", "TXT", "URI",
)

POLICY_NAMES = (
    ("_dmarc", "TXT"),
    ("_mta-sts", "TXT"),
    ("_smtp._tls", "TXT"),
)

DEFAULT_DKIM_SELECTORS = (
    "default", "selector1", "selector2", "google", "k1", "mail", "smtp",
)


@dataclass(frozen=True, order=True)
class Record:
    name: str
    ttl: int
    type: str
    value: str


def absolute_name(name: str) -> str:
    """Normalise un nom DNS en nom absolu."""
    return name.rstrip(".").lower() + "."


def query(
    resolver: "dns.resolver.Resolver",
    name: str,
    record_type: str,
) -> list[Record]:
    """Interroge un type précis ; une absence de donnée n'est pas une erreur."""
    try:
        answer = resolver.resolve(
            name, record_type, search=False, raise_on_no_answer=False
        )
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ):
        return []

    if answer.rrset is None:
        return []
    return [
        Record(
            name=answer.rrset.name.to_text(),
            ttl=answer.rrset.ttl,
            type=dns.rdatatype.to_text(rdata.rdtype),
            value=rdata.to_text(),
        )
        for rdata in answer
    ]


def try_axfr(domain: str, timeout: float) -> tuple[list[Record], list[str]]:
    """Tente un transfert auprès de chaque serveur faisant autorité."""
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    errors: list[str] = []
    records: set[Record] = set()

    try:
        nameservers = resolver.resolve(domain, "NS", search=False)
    except dns.exception.DNSException as exc:
        return [], [f"Impossible de trouver les NS : {exc}"]

    for nameserver in nameservers:
        host = nameserver.target.to_text()
        try:
            addresses = resolver.resolve(host, "A", search=False)
        except dns.exception.DNSException as exc:
            errors.append(f"{host}: résolution impossible ({exc})")
            continue

        for address in addresses:
            try:
                transfer = dns.query.xfr(
                    str(address), domain, lifetime=timeout, relativize=False
                )
                zone = dns.zone.from_xfr(transfer, relativize=False)
                for name, node in zone.nodes.items():
                    for rdataset in node.rdatasets:
                        record_type = dns.rdatatype.to_text(rdataset.rdtype)
                        for rdata in rdataset:
                            records.add(
                                Record(
                                    name=name.to_text(),
                                    ttl=rdataset.ttl,
                                    type=record_type,
                                    value=rdata.to_text(),
                                )
                            )
            except dns.exception.DNSException as exc:
                errors.append(f"{host} ({address}): AXFR refusé ou échoué ({exc})")

    return sorted(records), errors


def discover(
    domain: str,
    selectors: Iterable[str],
    timeout: float,
) -> list[Record]:
    """Effectue l'inventaire sans transfert de zone."""
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    found: set[Record] = set()

    for record_type in APEX_TYPES:
        found.update(query(resolver, domain, record_type))

    for prefix, record_type in POLICY_NAMES:
        found.update(query(resolver, f"{prefix}.{domain}", record_type))

    for selector in selectors:
        found.update(query(resolver, f"{selector}._domainkey.{domain}", "TXT"))

    return sorted(found)


def output_text(records: Sequence[Record]) -> None:
    if not records:
        print("Aucun enregistrement trouvé.")
        return
    for record in records:
        print(f"{record.name:<45} {record.ttl:>8} {record.type:<10} {record.value}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventorie les enregistrements DNS accessibles. Un résultat ne peut "
            "être garanti exhaustif que si --axfr réussit."
        )
    )
    parser.add_argument("domain", help="domaine à examiner, par ex. example.com")
    parser.add_argument(
        "--dkim-selector",
        action="append",
        default=[],
        metavar="SELECTEUR",
        help="sélecteur DKIM à tester (option répétable)",
    )
    parser.add_argument(
        "--no-common-dkim",
        action="store_true",
        help="ne pas tester les sélecteurs DKIM courants",
    )
    parser.add_argument(
        "--axfr",
        action="store_true",
        help="tenter un transfert complet de zone auprès des NS autoritaires",
    )
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    parser.add_argument(
        "--timeout", type=float, default=4.0, help="délai DNS en secondes (défaut: 4)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    domain = absolute_name(args.domain)
    selectors = set(args.dkim_selector)
    if not args.no_common_dkim:
        selectors.update(DEFAULT_DKIM_SELECTORS)

    records: set[Record] = set(discover(domain, selectors, args.timeout))
    axfr_errors: list[str] = []
    axfr_succeeded = False
    if args.axfr:
        transferred, axfr_errors = try_axfr(domain, args.timeout)
        records.update(transferred)
        axfr_succeeded = bool(transferred)

    ordered = sorted(records)
    if args.json:
        print(
            json.dumps(
                {
                    "domain": domain,
                    "records": [asdict(record) for record in ordered],
                    "axfr_requested": args.axfr,
                    "axfr_succeeded": axfr_succeeded,
                    "axfr_errors": axfr_errors,
                    "exhaustive": axfr_succeeded,
                    "note": (
                        "Sans AXFR réussi, les sous-domaines et sélecteurs DKIM "
                        "ne sont pas énumérables de façon générale."
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        output_text(ordered)
        print(
            "\nExhaustivité : "
            + (
                "transfert AXFR réussi."
                if axfr_succeeded
                else "non garantie (aucun transfert AXFR réussi)."
            ),
            file=sys.stderr,
        )
        for error in axfr_errors:
            print(f"AXFR: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
