#!/usr/bin/env python3
"""
CLI for H2FPEF Score Calculator for HFpEF Diagnosis.

Provides commands for H2FPEF score calculation and HFA-PEFF algorithm reference.
"""
import argparse
import json
import sys

from h2fpef_score import (
    calculate_h2fpef_score,
    calculate_h2fpef_from_bools,
    get_hfa_peff_algorithm,
    SCORE_COMPONENTS,
    INTERPRETATION,
)

from agents.base import AuditLogger, PHIGuard, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor


def cmd_calculate(args):
    """Calculate H2FPEF score."""
    result = calculate_h2fpef_score(
        bmi=args.bmi,
        num_antihypertensives=args.antihypertensives,
        af_present=args.af,
        pasp_mmhg=args.pasp,
        age=args.age,
        e_e_prime=args.e_e_prime,
    )

    print("=" * 60)
    print("  H2FPEF SCORE CALCULATOR")
    print("=" * 60)

    if args.bmi:
        print(f"  BMI: {args.bmi} kg/m^2")
    if args.age:
        print(f"  Age: {args.age} years")
    print(f"  Antihypertensives: {args.antihypertensives}")
    print(f"  AF: {'Yes' if args.af else 'No'}")
    if args.pasp:
        print(f"  PASP: {args.pasp} mmHg")
    if args.e_e_prime:
        print(f"  E/e': {args.e_e_prime}")

    print(f"\n  SCORE: {result['score']} / {result['max_score']}")
    print(f"\n  COMPONENTS:")
    for name, comp in result["components"].items():
        status = "+" + str(comp["points"]) if comp["met"] else " 0"
        marker = "X" if comp["met"] else " "
        val = f" ({comp['value']})" if comp["value"] is not None else ""
        print(f"    [{marker}] {comp['name']:20s} {comp['criteria']:30s} {status}{val}")

    print(f"\n  INTERPRETATION:")
    print(f"    Category:    {result['label']}")
    print(f"    Probability: {result['probability_percent']}%")
    print(f"    {result['description']}")
    print(f"    Recommendation: {result['recommendation']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_quick(args):
    """Quick H2FPEF score from boolean flags."""
    result = calculate_h2fpef_from_bools(
        heavy=args.heavy,
        hypertensive=args.hypertensive,
        af=args.af,
        pulmonary_pressure=args.pulmonary_pressure,
        elder=args.elder,
        filling_pressure=args.filling_pressure,
    )

    print("=" * 60)
    print("  H2FPEF SCORE (Quick)")
    print("=" * 60)
    print(f"  Score: {result['score']} / {result['max_score']}")
    print(f"  Category: {result['label']}")
    print(f"  Probability: {result['probability_percent']}%")
    print(f"  {result['recommendation']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_reference(args):
    """Show HFA-PEFF algorithm reference."""
    algo = get_hfa_peff_algorithm()

    print("=" * 60)
    print(f"  {algo['name']}")
    print(f"  {algo['description']}")
    print(f"  Reference: {algo['reference']}")
    print("=" * 60)

    for step_key, step in algo["steps"].items():
        print(f"\n  {step_key.upper()}: {step['name']}")
        print(f"  {step['description']}")
        if "criteria" in step:
            for c in step["criteria"]:
                print(f"    - {c}")
        if "domains" in step:
            for domain_name, domain in step["domains"].items():
                print(f"\n    Domain: {domain_name} (max {domain['max_points']} points)")
                for c in domain["criteria"]:
                    print(f"      - {c}")
        if "interpretation" in step:
            print(f"\n    Interpretation:")
            for k, v in step["interpretation"].items():
                print(f"      {k}: {v}")

    if args.json:
        print("\n" + json.dumps(algo, indent=2))
    return 0


def cmd_audit(args):
    """Run distributed component audit task."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id=args.task_id,
        target_identifier=args.target_identifier,
        primary_metric=args.primary_metric,
        secondary_metric=args.secondary_metric,
        status_descriptor=args.status_descriptor,
        is_critical_flag=args.is_critical_flag,
    )
    dossier = supervisor.process_task(payload)

    print("=" * 60)
    print("  DISTRIBUTED COMPONENT AUDIT")
    print("=" * 60)
    print(f"  Dossier ID:      {dossier.dossier_id}")
    print(f"  Task ID:         {dossier.task_id}")
    print(f"  Target:          {dossier.target_identifier}")
    print(f"  Overall Urgency: {dossier.overall_urgency.value}")
    print(f"  Integrity:       {dossier.integrity_status.value}")
    print(f"  Total Alerts:    {dossier.total_alerts}")
    print(f"  Audit Hash:      {dossier.audit_hash}")

    if dossier.alerts:
        print(f"\n  ALERTS:")
        for alert in dossier.alerts:
            print(f"    [{alert.urgency.value}] {alert.summary}")
            print(f"      Worker: {alert.origin_worker}")
            print(f"      Action: {alert.actionable_remediation}")

    if args.json:
        print("\n" + json.dumps(dossier.to_dict(), indent=2))
    return 0


def cmd_chat(args):
    """Query the supervisory chat assistant."""
    supervisor = SystemSupervisor(model_provider="mock")
    query = " ".join(args.query)
    try:
        response = supervisor.query_supervisory_chat(query)
        print(f"Response: {response}")
    except SecurityException as e:
        print(f"Security Error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_verify_audit(args):
    """Verify HMAC audit trail integrity."""
    verified = AuditLogger.verify_integrity()
    trail = AuditLogger.get_trail()

    print("=" * 60)
    print("  HMAC AUDIT TRAIL VERIFICATION")
    print("=" * 60)
    print(f"  Total Audit Blocks: {len(trail)}")
    print(f"  Integrity Verified: {'PASS' if verified else 'FAIL'}")

    if args.json:
        print("\n" + json.dumps({"verified": verified, "trail": trail}, indent=2))
    return 0 if verified else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="h2fpef",
        description="H2FPEF Score Calculator for HFpEF Diagnosis",
    )
    parser.add_argument("--json", action="store_true", help="Also output JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Full calculation
    p_calc = subparsers.add_parser("calculate", help="Calculate H2FPEF score")
    p_calc.add_argument("--bmi", type=float, help="BMI in kg/m^2")
    p_calc.add_argument("--antihypertensives", type=int, default=0, help="Number of antihypertensives")
    p_calc.add_argument("--af", action="store_true", help="Atrial fibrillation present")
    p_calc.add_argument("--pasp", type=float, help="PASP in mmHg")
    p_calc.add_argument("--age", type=float, help="Age in years")
    p_calc.add_argument("--e-e-prime", type=float, help="E/e' ratio")

    # Quick calculation from booleans
    p_quick = subparsers.add_parser("quick", help="Quick score from boolean flags")
    p_quick.add_argument("--heavy", action="store_true", help="BMI > 30")
    p_quick.add_argument("--hypertensive", action="store_true", help=">= 2 antihypertensives")
    p_quick.add_argument("--af", action="store_true", help="AF present")
    p_quick.add_argument("--pulmonary-pressure", action="store_true", help="PASP > 35")
    p_quick.add_argument("--elder", action="store_true", help="Age > 60")
    p_quick.add_argument("--filling-pressure", action="store_true", help="E/e' > 9")

    # Reference
    subparsers.add_parser("reference", help="Show HFA-PEFF algorithm")

    # Distributed component audit
    p_audit = subparsers.add_parser("audit", help="Run distributed component audit")
    p_audit.add_argument("--task-id", required=True, help="Task identifier")
    p_audit.add_argument("--target-identifier", default="KEY-01", help="Target identifier")
    p_audit.add_argument("--primary-metric", type=float, default=10.0, help="Primary metric value")
    p_audit.add_argument("--secondary-metric", type=float, default=2.0, help="Secondary metric value")
    p_audit.add_argument("--status-descriptor", default="NOMINAL", help="Status descriptor")
    p_audit.add_argument("--is-critical-flag", action="store_true", help="Critical flag")

    # Supervisory chat
    p_chat = subparsers.add_parser("chat", help="Query supervisory chat assistant")
    p_chat.add_argument("query", nargs="+", help="Query text")

    # Verify audit trail
    subparsers.add_parser("verify-audit", help="Verify HMAC audit trail integrity")

    args = parser.parse_args(argv)

    commands = {
        "calculate": cmd_calculate,
        "quick": cmd_quick,
        "reference": cmd_reference,
        "audit": cmd_audit,
        "chat": cmd_chat,
        "verify-audit": cmd_verify_audit,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
