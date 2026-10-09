import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

cases = [
    ("Flow_01_NullArray", None, 2),
    ("Flow_02_DigitBelowZero", [12.8], -1),
    ("Flow_03_DigitAboveNine", [12.8], 10),
    ("Flow_04_Infinity", [math.inf], 2),
    ("Flow_05_EmptyArray", [], 2),
    ("Flow_06_MatchInUnits", [12.8], 2),
    ("Flow_07_SingleDigitWithoutMatch", [7.8], 2),
    ("Flow_08_MatchAfterDivision", [21.4], 2),
    ("Flow_09_MultipleDigitsWithoutMatch", [13.8], 2),
    ("Flow_10_ZeroMatchesZero", [0.0], 0),
    ("Flow_11_SeveralElements", [7.8, 12.8, -21.4], 2),
    ("Flow_12_LateNaN", [12.8, math.nan], 2),
]

cases.extend([
    ("Condition_01_DigitBelowMinimum", [0.0], -1),
    ("Condition_02_DigitAtMinimum", [10.5], 0),
    ("Condition_03_DigitAboveMinimum", [1.5], 1),
    ("Condition_04_DigitBelowMaximum", [8.5], 8),
    ("Condition_05_DigitAtMaximum", [9.5], 9),
    ("Condition_06_DigitAboveMaximum", [0.0], 10),
    ("Condition_07_DigitIntMinimum", [12.8], -2147483648),
    ("Condition_08_DigitIntMaximum", [12.8], 2147483647),
    ("Condition_09_CurrentDigitLess", [3.5], 5),
    ("Condition_10_CurrentDigitEqual", [5.5], 5),
    ("Condition_11_CurrentDigitGreater", [7.5], 5),
    ("Condition_12_DigitLoopStops", [1.5], 2),
    ("Condition_13_DigitLoopContinues", [15.5], 1),
    ("Condition_14_PositiveFinite", [15.5], 5),
    ("Condition_15_NegativeFinite", [-15.5], 5),
    ("Condition_16_NaN", [math.nan], 5),
    ("Condition_17_PositiveInfinity", [math.inf], 5),
    ("Condition_18_NegativeInfinity", [-math.inf], 5),
])

import random
import struct

max_value = float.fromhex("0x1.fffffffffffffp+1023")
min_positive = float.fromhex("0x0.0000000000001p-1022")

cases.extend([
    ("Equivalence_01_DoubleMinimum", [-max_value], 1),
    ("Equivalence_02_NegativeInterior", [-123.75], 2),
    ("Equivalence_03_Zero", [0.0], 0),
    ("Equivalence_04_PositiveInterior", [123.75], 2),
    ("Equivalence_05_DoubleMaximum", [max_value], 1),
    ("Equivalence_06_NextAfterMinimum", [math.nextafter(-max_value, 0.0)], 1),
    ("Equivalence_07_NextBeforeMaximum", [math.nextafter(max_value, 0.0)], 1),
    ("Equivalence_08_PositiveSubnormal", [min_positive], 0),
    ("Equivalence_09_NegativeSubnormal", [-min_positive], 0),
    ("Equivalence_10_PositiveFraction", [0.75], 0),
    ("Equivalence_11_NegativeFraction", [-0.75], 0),
    ("Equivalence_12_FractionWithoutMatch", [0.75, -0.75], 7),
    ("Equivalence_13_BelowOne", [math.nextafter(1.0, 0.0)], 0),
    ("Equivalence_14_AboveMinusOne", [math.nextafter(-1.0, 0.0)], 0),
    ("Equivalence_15_AboveOne", [math.nextafter(1.0, math.inf)], 1),
    ("Equivalence_16_BelowMinusOne", [math.nextafter(-1.0, -math.inf)], 1),
    ("Equivalence_17_MatchFirst", [12.8, 7.1, 35.4], 2),
    ("Equivalence_18_MatchMiddle", [7.1, 12.8, 35.4], 2),
    ("Equivalence_19_MatchLast", [7.1, 35.4, 12.8], 2),
    ("Equivalence_20_NoMatches", [17.8, 35.4, 46.2], 2),
    ("Equivalence_21_AllMatch", [12.8, 21.4, -22.6], 2),
    ("Equivalence_22_RepeatedDigit", [222.8], 2),
    ("Equivalence_23_RepeatedElements", [12.8, 12.8, 12.8], 2),
    ("Equivalence_24_Cancellation", [21.5, -21.5], 2),
    ("Equivalence_25_ZeroInsideInteger", [101.8, -20.9, 3.2], 0),
    ("Equivalence_26_DigitOnlyInFraction", [13.2, -45.2], 2),
    ("Equivalence_27_EmptyArray", [], 9),
    ("Equivalence_28_SingleMatch", [-90.5], 9),
    ("Equivalence_29_SingleWithoutMatch", [18.9], 9),
    ("Equivalence_30_SumBeyondDouble", [max_value, max_value], 1),
    ("Equivalence_31_LongArray", [float(i) + 0.5 for i in range(1000)], 7),
])

rng = random.Random(45)
for index in range(1, 10):
    numbers = []
    while len(numbers) < 5:
        bits = rng.getrandbits(64)
        number = struct.unpack(">d", bits.to_bytes(8, "big"))[0]
        if math.isfinite(number):
            numbers.append(number)
    cases.append((
        f"Equivalence_Random{index:02d}_FiniteBinary64",
        numbers,
        rng.randrange(10)
    ))

# END_OF_CASES


def expected_result(numbers, digit):
    if numbers is None:
        return {"error": "ArgumentNullException", "parameter": "numbers"}
    if digit < 0 or digit > 9:
        return {"error": "ArgumentOutOfRangeException", "parameter": "digit"}
    if any(not math.isfinite(number) for number in numbers):
        return {"error": "ArgumentException", "parameter": "numbers"}

    # Python searches a string; C# checks digits arithmetically.
    elements = [number for number in numbers
                if str(digit) in str(abs(int(number)))]
    return {"elements": elements, "sum": str(sum(int(x) for x in elements))}


def number_text(value):
    if math.isnan(value):
        return "NaN"
    if value == math.inf:
        return "Infinity"
    if value == -math.inf:
        return "-Infinity"
    return repr(float(value))


def cs_number(value):
    special = {"NaN": "double.NaN", "Infinity": "double.PositiveInfinity",
               "-Infinity": "double.NegativeInfinity",
               "1.7976931348623157e+308": "double.MaxValue",
               "-1.7976931348623157e+308": "double.MinValue",
               "5e-324": "double.Epsilon",
               "-5e-324": "-double.Epsilon"}
    text = number_text(value)
    return special[text] if text in special else text + "d"


def cs_array(values):
    if values is None:
        return "null!"
    return "new double[] { " + ", ".join(cs_number(x) for x in values) + " }"


lines = [
    "// Generated by tools/generate_tests.py.",
    "using System;", "using System.Numerics;", "using ArrayTask;", "using Xunit;",
    "", "namespace ArrayTask.Tests;", "", "public class GeneratedTests", "{",
]
records = []

for name, numbers, digit in cases:
    expected = expected_result(numbers, digit)
    group = name.split("_")[0]
    lines.extend([
        "    [Fact]", f'    [Trait("Group", "{group}")]',
        f"    public void {name}()", "    {",
        f"        double[] numbers = {cs_array(numbers)};",
    ])

    if "error" in expected:
        lines.extend([
            f'        var error = Assert.Throws<{expected["error"]}>(',
            f"            () => ArrayProcessor.FindByDigit(numbers, {digit}));",
            f'        Assert.Equal("{expected["parameter"]}", error.ParamName);',
        ])
        saved_expected = expected
        summary = expected["error"]
    else:
        lines.extend([
            "        double[] before = (double[])numbers.Clone();",
            f"        var result = ArrayProcessor.FindByDigit(numbers, {digit});",
            f'        double[] expectedElements = {cs_array(expected["elements"])};',
            "        Assert.Equal<double>(expectedElements, result.Elements);",
            f'        Assert.Equal(BigInteger.Parse("{expected["sum"]}"), result.Sum);',
            "        Assert.Equal<double>(before, numbers);",
        ])
        saved_expected = {
            "elements": [number_text(x) for x in expected["elements"]],
            "sum": expected["sum"]
        }
        summary = "sum=" + expected["sum"]

    lines.extend(["    }", ""])
    records.append({
        "name": name,
        "group": group,
        "numbers": None if numbers is None else [number_text(x) for x in numbers],
        "digit": digit,
        "expected": saved_expected
    })
    print(name + ": " + summary)

lines.append("}")
tests_folder = ROOT / "ArrayTask.Tests"
data_folder = ROOT / "test-data"
tests_folder.mkdir(exist_ok=True)
data_folder.mkdir(exist_ok=True)

(tests_folder / "GeneratedTests.cs").write_text(
    "\n".join(lines) + "\n", encoding="utf-8")
(data_folder / "cases.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8")

print("Generated tests:", len(cases))


