import argparse
import csv
import json
import struct
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def same_result(expected, actual):
    if "error" in expected:
        return expected == actual
    if set(actual) != {"elements", "sum"}:
        return False
    left, right = expected["elements"], actual["elements"]
    return (
        expected["sum"] == actual["sum"]
        and len(left) == len(right)
        and all(struct.pack(">d", float(a)) == struct.pack(">d", float(b))
                for a, b in zip(left, right))
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="test-data")
    args = parser.parse_args()
    folder = Path(args.results)
    if not folder.is_absolute():
        folder = ROOT / folder

    cases = json.loads(
        (ROOT / "test-data/cases.json").read_text(encoding="utf-8-sig"))
    if len(cases) < 30:
        raise SystemExit("At least 30 tests are required")

    trx = ET.parse(folder / "tests.trx").getroot()
    outcomes = {}
    for result in trx.findall(".//{*}UnitTestResult"):
        name = result.attrib["testName"].rsplit(".", 1)[-1]
        if name in outcomes:
            raise SystemExit("Duplicate test result: " + name)
        outcomes[name] = result.attrib["outcome"]

    names = {case["name"] for case in cases}
    if len(names) != len(cases) or set(outcomes) != names:
        raise SystemExit("TRX test names do not match cases.json")

    rows = []
    for case in cases:
        actual = json.loads(
            (folder / "actual-results" / (case["name"] + ".json"))
            .read_text(encoding="utf-8-sig"))
        passed = (
            outcomes[case["name"]] == "Passed"
            and same_result(case["expected"], actual))
        rows.append({
            **case, "actual": actual,
            "outcome": outcomes[case["name"]], "passed": passed})

    coverage_files = list(folder.rglob("coverage.cobertura.xml"))
    if not coverage_files:
        raise SystemExit("Coverage file not found")

    coverage_file = max(coverage_files, key=lambda path: path.stat().st_mtime)
    coverage = ET.parse(coverage_file).getroot()
    line_rate = Decimal(coverage.attrib["line-rate"])
    branch_rate = Decimal(coverage.attrib["branch-rate"])

    if (int(coverage.attrib["lines-valid"]) == 0
            or int(coverage.attrib["branches-valid"]) == 0):
        raise SystemExit("Coverage contains no measured lines or branches")

    with (folder / "protocol.csv").open(
            "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([
            "Название теста", "Группа", "Исходные данные",
            "Ожидаемые результаты", "Фактические результаты", "Вывод"])

        for row in rows:
            source = {"array": row["numbers"], "digit": row["digit"]}
            writer.writerow([
                row["name"], row["group"],
                json.dumps(source, ensure_ascii=False),
                json.dumps(row["expected"], ensure_ascii=False),
                json.dumps(row["actual"], ensure_ascii=False),
                "Пройден" if row["passed"] else "Не пройден"])

    (folder / "protocol.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    passed_count = sum(row["passed"] for row in rows)
    summary = [
        f"Tests: {len(rows)}",
        f"Passed: {passed_count}",
        f"Failed: {len(rows) - passed_count}",
        f"Line coverage: {line_rate * 100}%",
        f"Branch coverage: {branch_rate * 100}%"]

    (folder / "coverage-summary.txt").write_text(
        "\n".join(summary) + "\n", encoding="utf-8")

    print("\n".join(summary))
    print("Groups:", dict(Counter(row["group"] for row in rows)))
    print("Protocol:", folder / "protocol.csv")

    if passed_count != len(rows) or line_rate != 1 or branch_rate != 1:
        raise SystemExit("Tests or 100% coverage check failed")


if __name__ == "__main__":
    main()
