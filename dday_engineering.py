"""
DDay Controls — Engineering calculation core.

Pure-Python module: no Qt, no I/O.  Imported by engineering_calculator and
re-exported from dday_controls_common so all tool files that do
``from dday_controls_common import *`` get everything.

Covers the maths behind the Engineering Calculator:
  * base-aware integer expression evaluation (programmer calculator)
  * analog raw-count <-> engineering-unit scaling
  * Ohm's law / power wheel
  * motor, drive and gearbox relationships
  * encoder resolution and motion travel
"""

from __future__ import annotations

import math
import re
from collections import OrderedDict


# ******************************************************************************
#
# BASE EXPRESSION EVALUATOR
#
# ******************************************************************************
#
# A programmer-style integer calculator.  Values are evaluated as Python
# integers and wrapped to the selected word size after every operation, so the
# result matches what a PLC or controller would hold in the same register.
#
# Bare literals are read in the currently selected base.  Prefixes override
# that base:  0x = hex, 0o = octal, 0b = binary.  Because "b" is itself a hex
# digit, the 0b prefix is NOT honoured while the selected base is HEX — there
# 0b10 reads as the hex value 0B10.
#


BASE_NAMES = ("DEC", "HEX", "BIN", "OCT")

BASE_RADIX = {"DEC": 10, "HEX": 16, "BIN": 2, "OCT": 8}

BASE_DIGITS = {
    "DEC": "0123456789",
    "HEX": "0123456789abcdef",
    "BIN": "01",
    "OCT": "01234567",
}

CALC_BIT_WIDTHS = ("8-bit", "16-bit", "32-bit", "64-bit")

# The names a programmer calculator normally puts on those widths.
CALC_WORD_SIZES = OrderedDict({
    "BYTE  (8-bit)": 8,
    "WORD  (16-bit)": 16,
    "DWORD (32-bit)": 32,
    "QWORD (64-bit)": 64,
})

# Operator precedence, lowest binding first.  Mirrors C so that results match
# what the same expression does in structured text or a C-family language.
_PRECEDENCE = [
    ("|",),
    ("^",),
    ("&",),
    ("<<", ">>"),
    ("+", "-"),
    ("*", "/", "%"),
]

_PREFIX_BASES = {"x": "HEX", "o": "OCT", "b": "BIN"}


class CalcError(ValueError):
    """Raised when an expression cannot be parsed or evaluated."""


# ------------------------------------------------------------------------------
# Return the bit width for a calculator width label
def calc_bit_width(text: str) -> int:
    if text in CALC_WORD_SIZES:
        return CALC_WORD_SIZES[text]
    return {"8-bit": 8, "16-bit": 16, "32-bit": 32, "64-bit": 64}.get(text, 16)


# ------------------------------------------------------------------------------
# Wrap an integer into the given word size and signedness
def wrap_to_word(value: int, bits: int, signed: bool) -> int:
    masked = value & ((1 << bits) - 1)
    if signed and masked >= (1 << (bits - 1)):
        masked -= 1 << bits
    return masked


# ------------------------------------------------------------------------------
# Divide truncating toward zero, matching C and IEC 61131 semantics
def trunc_div(a: int, b: int) -> int:
    if b == 0:
        raise CalcError("Division by zero.")
    quotient = abs(a) // abs(b)
    return -quotient if (a < 0) != (b < 0) else quotient


# ------------------------------------------------------------------------------
# Remainder matching truncated division, so the sign follows the dividend
def trunc_mod(a: int, b: int) -> int:
    if b == 0:
        raise CalcError("Division by zero.")
    return a - trunc_div(a, b) * b


# ------------------------------------------------------------------------------
# Split expression text into number, operator, and parenthesis tokens
def tokenize_expression(text: str, base: str) -> list[tuple[str, object]]:
    if base not in BASE_RADIX:
        raise CalcError(f"Unknown base '{base}'.")

    digits = BASE_DIGITS[base]
    tokens: list[tuple[str, object]] = []
    index = 0
    length = len(text)

    while index < length:
        char = text[index]

        # Whitespace and digit-group separators carry no meaning.
        if char.isspace() or char in "_,":
            index += 1
            continue

        if char in "()":
            tokens.append(("paren", char))
            index += 1
            continue

        two = text[index:index + 2]
        if two in ("<<", ">>"):
            tokens.append(("op", two))
            index += 2
            continue

        if char in "+-*/%&|^~":
            tokens.append(("op", char))
            index += 1
            continue

        # A literal starts with a digit valid in the active base, or with a
        # prefixed zero that selects a different base.
        if char.lower() in digits or char == "0":
            radix = BASE_RADIX[base]
            allowed = digits

            if char == "0" and index + 1 < length:
                marker = text[index + 1].lower()
                prefix_base = _PREFIX_BASES.get(marker)
                # "b" is a hex digit, so the 0b prefix is ambiguous in hex mode.
                if prefix_base is not None and not (base == "HEX" and marker == "b"):
                    radix = BASE_RADIX[prefix_base]
                    allowed = BASE_DIGITS[prefix_base]
                    index += 2
                    if index >= length or text[index].lower() not in allowed:
                        raise CalcError(f"'0{marker}' prefix needs at least one digit.")

            start = index
            while index < length and (text[index].lower() in allowed or text[index] in "_,"):
                index += 1

            literal = re.sub(r"[_,]", "", text[start:index])
            if not literal:
                raise CalcError(f"Invalid number near '{text[start:start + 6]}'.")

            # Catch a trailing character that is a digit somewhere else but not
            # in this base — "19" typed while BIN is selected, for example.
            if index < length and text[index].isalnum():
                raise CalcError(f"'{text[index]}' is not a valid {base} digit.")

            tokens.append(("num", int(literal, radix)))
            continue

        if char.isalnum():
            raise CalcError(f"'{char}' is not a valid {base} digit.")

        raise CalcError(f"Unexpected character '{char}'.")

    return tokens


# ------------------------------------------------------------------------------
# Evaluate a tokenized expression with a recursive-descent parser
class _ExpressionParser:

    def __init__(self, tokens: list[tuple[str, object]], bits: int, signed: bool) -> None:
        self.tokens = tokens
        self.position = 0
        self.bits = bits
        self.signed = signed
        self.overflow = False

    # --------------------------------------------------------------------------
    # Return the current token without consuming it
    def peek(self) -> tuple[str, object] | None:
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    # --------------------------------------------------------------------------
    # Wrap a result, recording whether the word size truncated it
    def wrap(self, value: int) -> int:
        wrapped = wrap_to_word(value, self.bits, self.signed)
        if wrapped != value:
            self.overflow = True
        return wrapped

    # --------------------------------------------------------------------------
    # Parse a binary-operator level, descending to the next tighter level
    def parse_binary(self, level: int) -> int:
        if level >= len(_PRECEDENCE):
            return self.parse_unary()

        operators = _PRECEDENCE[level]
        value = self.parse_binary(level + 1)

        while True:
            token = self.peek()
            if token is None or token[0] != "op" or token[1] not in operators:
                return value
            self.position += 1
            right = self.parse_binary(level + 1)
            value = self.wrap(self.apply(str(token[1]), value, right))

    # --------------------------------------------------------------------------
    # Apply one binary operator to already-wrapped operands
    def apply(self, operator: str, left: int, right: int) -> int:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            return trunc_div(left, right)
        if operator == "%":
            return trunc_mod(left, right)
        if operator == "&":
            return left & right
        if operator == "|":
            return left | right
        if operator == "^":
            return left ^ right
        if operator in ("<<", ">>"):
            if right < 0:
                raise CalcError("Shift count cannot be negative.")
            # Clamping keeps a huge shift count from allocating a huge integer;
            # every bit has already left the word by then anyway.
            count = min(right, self.bits)
            return left << count if operator == "<<" else left >> count
        raise CalcError(f"Unknown operator '{operator}'.")

    # --------------------------------------------------------------------------
    # Parse unary minus, plus, and bitwise NOT
    def parse_unary(self) -> int:
        token = self.peek()
        if token is not None and token[0] == "op" and token[1] in ("-", "+", "~"):
            self.position += 1
            operand = self.parse_unary()
            if token[1] == "-":
                return self.wrap(-operand)
            if token[1] == "~":
                return self.wrap(~operand)
            return operand
        return self.parse_primary()

    # --------------------------------------------------------------------------
    # Parse a number literal or a parenthesized sub-expression
    def parse_primary(self) -> int:
        token = self.peek()
        if token is None:
            raise CalcError("Expression ends unexpectedly.")

        if token[0] == "num":
            self.position += 1
            return self.wrap(int(token[1]))

        if token[0] == "paren" and token[1] == "(":
            self.position += 1
            value = self.parse_binary(0)
            closing = self.peek()
            if closing is None or closing[1] != ")":
                raise CalcError("Missing closing parenthesis.")
            self.position += 1
            return value

        if token[0] == "paren":
            raise CalcError("Unmatched closing parenthesis.")

        raise CalcError(f"Operator '{token[1]}' is missing a value.")


# ------------------------------------------------------------------------------
# Evaluate an expression in the given base and word size
def evaluate_expression(text: str, base: str, bits: int, signed: bool) -> tuple[int, bool]:
    """Return (wrapped result, overflow flag) for an integer expression."""
    if not text.strip():
        raise CalcError("No expression entered.")

    tokens = tokenize_expression(text, base)
    if not tokens:
        raise CalcError("No expression entered.")

    parser = _ExpressionParser(tokens, bits, signed)
    value = parser.parse_binary(0)

    remaining = parser.peek()
    if remaining is not None:
        if remaining[0] == "paren":
            raise CalcError("Unmatched closing parenthesis.")
        raise CalcError(f"Unexpected trailing '{remaining[1]}'.")

    return value, parser.overflow


# ------------------------------------------------------------------------------
# Render a value so it can be typed straight back into the display
def literal_in_base(value: int, base: str, bits: int) -> str:
    """No padding and no digit grouping, which would tokenize as two numbers."""
    if base == "DEC":
        return str(value)

    unsigned = value + (1 << bits) if value < 0 else value
    if base == "HEX":
        return f"{unsigned:X}"
    if base == "OCT":
        return f"{unsigned:o}"
    if base == "BIN":
        return f"{unsigned:b}"

    raise CalcError(f"Unknown base '{base}'.")


# ******************************************************************************
#
# ANALOG SCALING
#
# ******************************************************************************
#
# Raw-count ranges for the analog cards and signal types seen most often on a
# controls job.  Each entry is (raw low, raw high, description).
#


ANALOG_RAW_PRESETS: OrderedDict[str, tuple[float, float, str]] = OrderedDict({
    "Siemens S7 unipolar": (0.0, 27648.0, "Normalized range for 0-10 V or 4-20 mA"),
    "Siemens S7 bipolar": (-27648.0, 27648.0, "Normalized range for +/-10 V"),
    "Allen-Bradley SLC 4-20 mA": (3277.0, 16384.0, "1746-NI4 raw counts across 4-20 mA"),
    "12-bit unipolar": (0.0, 4095.0, "Common low-cost analog input"),
    "13-bit unipolar": (0.0, 8191.0, "13-bit converter"),
    "14-bit unipolar": (0.0, 16383.0, "14-bit converter"),
    "15-bit unipolar": (0.0, 32767.0, "15-bit converter"),
    "16-bit unsigned": (0.0, 65535.0, "Full unsigned word"),
    "16-bit signed": (-32768.0, 32767.0, "Full signed word"),
    "Percent": (0.0, 100.0, "Already scaled to percent"),
    "4-20 mA signal": (4.0, 20.0, "Raw milliamps rather than counts"),
    "0-10 V signal": (0.0, 10.0, "Raw volts rather than counts"),
})


# ------------------------------------------------------------------------------
# Map a value from one linear range onto another
def scale_linear(
    value: float,
    in_low: float,
    in_high: float,
    out_low: float,
    out_high: float,
    clamp: bool = False,
) -> float:
    if in_low == in_high:
        raise CalcError("Input range low and high cannot be equal.")

    scaled = out_low + (value - in_low) * (out_high - out_low) / (in_high - in_low)

    if clamp:
        low, high = min(out_low, out_high), max(out_low, out_high)
        scaled = min(max(scaled, low), high)

    return scaled


# ------------------------------------------------------------------------------
# Scale a raw count to engineering units with range and resolution detail
def scale_analog(
    raw: float,
    raw_low: float,
    raw_high: float,
    eu_low: float,
    eu_high: float,
    clamp: bool = False,
) -> dict:
    """Return the engineering value plus the context an integrator wants to see."""
    eu = scale_linear(raw, raw_low, raw_high, eu_low, eu_high, clamp)
    raw_span = raw_high - raw_low
    eu_span = eu_high - eu_low

    return {
        "eu": eu,
        "raw_span": raw_span,
        "eu_span": eu_span,
        # Engineering units represented by a single raw count.
        "resolution": eu_span / raw_span if raw_span else math.nan,
        "percent": scale_linear(raw, raw_low, raw_high, 0.0, 100.0),
        "under_range": raw < min(raw_low, raw_high),
        "over_range": raw > max(raw_low, raw_high),
    }


# ------------------------------------------------------------------------------
# Scale an engineering value back to the raw count a controller would hold
def unscale_analog(
    eu: float,
    raw_low: float,
    raw_high: float,
    eu_low: float,
    eu_high: float,
    clamp: bool = False,
) -> dict:
    raw = scale_linear(eu, eu_low, eu_high, raw_low, raw_high, clamp)

    return {
        "raw": raw,
        "raw_rounded": round(raw),
        "percent": scale_linear(eu, eu_low, eu_high, 0.0, 100.0),
        "under_range": eu < min(eu_low, eu_high),
        "over_range": eu > max(eu_low, eu_high),
    }


# ******************************************************************************
#
# OHM'S LAW AND POWER
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Solve the power wheel from any two known quantities
def solve_ohms_law(
    volts: float | None = None,
    amps: float | None = None,
    ohms: float | None = None,
    watts: float | None = None,
) -> dict:
    """Return all four of V, I, R and P given exactly two of them."""
    known = [name for name, value in
             (("volts", volts), ("amps", amps), ("ohms", ohms), ("watts", watts))
             if value is not None]

    if len(known) != 2:
        raise CalcError("Enter exactly two values.")

    v, i, r, p = volts, amps, ohms, watts

    if v is not None and i is not None:
        if i == 0:
            raise CalcError("Current cannot be zero when solving for resistance.")
        r, p = v / i, v * i

    elif v is not None and r is not None:
        if r == 0:
            raise CalcError("Resistance cannot be zero when solving for current.")
        i = v / r
        p = v * v / r

    elif v is not None and p is not None:
        if v == 0:
            raise CalcError("Voltage cannot be zero when solving from power.")
        i = p / v
        if p == 0:
            raise CalcError("Power cannot be zero when solving for resistance.")
        r = v * v / p

    elif i is not None and r is not None:
        v = i * r
        p = i * i * r

    elif i is not None and p is not None:
        if i == 0:
            raise CalcError("Current cannot be zero when solving from power.")
        v = p / i
        r = p / (i * i)

    elif r is not None and p is not None:
        if r < 0 or p < 0:
            raise CalcError("Resistance and power must be positive.")
        v = math.sqrt(p * r)
        if r == 0:
            raise CalcError("Resistance cannot be zero when solving for current.")
        i = math.sqrt(p / r)

    return {"volts": v, "amps": i, "ohms": r, "watts": p}


# ******************************************************************************
#
# MOTOR, DRIVE AND GEARBOX
#
# ******************************************************************************

WATTS_PER_HP = 745.6998715822702        # Mechanical horsepower
FOOT_POUNDS_PER_HP_MINUTE = 33000.0     # Definition of one horsepower

# Torque constants derived from P = T * omega rather than rounded off, so the
# imperial and metric sides of the tool agree with each other.
HP_TORQUE_CONSTANT = FOOT_POUNDS_PER_HP_MINUTE / (2.0 * math.pi)   # ~5252.11
KW_TORQUE_CONSTANT = 60000.0 / (2.0 * math.pi)                     # ~9549.30


# ------------------------------------------------------------------------------
# Convert horsepower to kilowatts
def hp_to_kw(hp: float) -> float:
    return hp * WATTS_PER_HP / 1000.0


# ------------------------------------------------------------------------------
# Convert kilowatts to horsepower
def kw_to_hp(kw: float) -> float:
    return kw * 1000.0 / WATTS_PER_HP


# ------------------------------------------------------------------------------
# Return shaft torque in lb-ft and N-m for a power and speed
def torque_from_power(hp: float, rpm: float) -> dict:
    if rpm == 0:
        raise CalcError("Speed cannot be zero when solving for torque.")

    kw = hp_to_kw(hp)
    return {
        "kw": kw,
        "lb_ft": HP_TORQUE_CONSTANT * hp / rpm,
        "n_m": KW_TORQUE_CONSTANT * kw / rpm,
    }


# ------------------------------------------------------------------------------
# Return shaft power for a torque in lb-ft and a speed
def power_from_torque(lb_ft: float, rpm: float) -> dict:
    hp = lb_ft * rpm / HP_TORQUE_CONSTANT
    kw = hp_to_kw(hp)
    return {"hp": hp, "kw": kw, "n_m": lb_ft * 1.3558179483314004}


# ------------------------------------------------------------------------------
# Return synchronous speed in RPM for a line frequency and pole count
def synchronous_speed(hertz: float, poles: int) -> float:
    if poles <= 0:
        raise CalcError("Pole count must be greater than zero.")
    if poles % 2:
        raise CalcError("Pole count must be even.")
    return 120.0 * hertz / poles


# ------------------------------------------------------------------------------
# Return percent slip between synchronous and actual shaft speed
def slip_percent(sync_rpm: float, actual_rpm: float) -> float:
    if sync_rpm == 0:
        raise CalcError("Synchronous speed cannot be zero.")
    return (sync_rpm - actual_rpm) / sync_rpm * 100.0


# ------------------------------------------------------------------------------
# Return apparent, real and reactive power for a motor circuit
def motor_power(volts: float, amps: float, power_factor: float, three_phase: bool = True) -> dict:
    if not 0.0 <= power_factor <= 1.0:
        raise CalcError("Power factor must be between 0 and 1.")

    phase_factor = math.sqrt(3.0) if three_phase else 1.0
    kva = phase_factor * volts * amps / 1000.0
    kw = kva * power_factor
    kvar = kva * math.sqrt(max(0.0, 1.0 - power_factor * power_factor))

    return {"kva": kva, "kw": kw, "kvar": kvar, "hp": kw_to_hp(kw)}


# ------------------------------------------------------------------------------
# Return full-load current drawn by a motor of a given output rating
def full_load_amps(
    hp: float,
    volts: float,
    power_factor: float,
    efficiency: float,
    three_phase: bool = True,
) -> float:
    if volts == 0:
        raise CalcError("Voltage cannot be zero.")
    if not 0.0 < power_factor <= 1.0:
        raise CalcError("Power factor must be between 0 and 1.")
    if not 0.0 < efficiency <= 1.0:
        raise CalcError("Efficiency must be between 0 and 1.")

    phase_factor = math.sqrt(3.0) if three_phase else 1.0
    return hp * WATTS_PER_HP / (phase_factor * volts * power_factor * efficiency)


# ------------------------------------------------------------------------------
# Return gearbox output speed and torque for a reduction ratio
def gearbox_output(
    input_rpm: float,
    ratio: float,
    input_torque: float = 0.0,
    efficiency: float = 1.0,
) -> dict:
    if ratio == 0:
        raise CalcError("Gear ratio cannot be zero.")
    if not 0.0 < efficiency <= 1.0:
        raise CalcError("Efficiency must be between 0 and 1.")

    return {
        "output_rpm": input_rpm / ratio,
        "output_torque": input_torque * ratio * efficiency,
    }


# ******************************************************************************
#
# ENCODER AND MOTION
#
# ******************************************************************************

QUADRATURE_MODES = OrderedDict({
    "x1 (single edge)": 1,
    "x2 (both edges, one channel)": 2,
    "x4 (both edges, A and B)": 4,
})

MECHANISM_TYPES = ("Leadscrew / belt pitch", "Pulley / roller diameter", "Rotary (degrees)")


# ------------------------------------------------------------------------------
# Return travel produced by one revolution of the driven mechanism
def travel_per_revolution(mechanism: str, dimension: float) -> float:
    if mechanism == "Leadscrew / belt pitch":
        return dimension
    if mechanism == "Pulley / roller diameter":
        return math.pi * dimension
    if mechanism == "Rotary (degrees)":
        return 360.0
    raise CalcError(f"Unknown mechanism '{mechanism}'.")


# ------------------------------------------------------------------------------
# Return encoder resolution and travel figures for a drive train
def encoder_resolution(
    ppr: float,
    quadrature: int,
    mechanism: str,
    dimension: float,
    gear_ratio: float = 1.0,
) -> dict:
    """Resolve pulses per revolution into counts and distance per count."""
    if ppr <= 0:
        raise CalcError("Pulses per revolution must be greater than zero.")
    if quadrature not in (1, 2, 4):
        raise CalcError("Quadrature multiplier must be 1, 2 or 4.")
    if gear_ratio <= 0:
        raise CalcError("Gear ratio must be greater than zero.")

    counts = ppr * quadrature
    # The gearbox sits between encoder and load, so the load moves less per
    # encoder revolution by exactly the reduction ratio.
    load_travel_per_rev = travel_per_revolution(mechanism, dimension) / gear_ratio

    return {
        "counts_per_rev": counts,
        "travel_per_rev": load_travel_per_rev,
        "distance_per_count": load_travel_per_rev / counts,
        "counts_per_unit": counts / load_travel_per_rev if load_travel_per_rev else math.nan,
    }


# ------------------------------------------------------------------------------
# Return the counts a given travel distance produces
def counts_for_distance(distance: float, distance_per_count: float) -> float:
    if distance_per_count == 0:
        raise CalcError("Distance per count cannot be zero.")
    return distance / distance_per_count


# ------------------------------------------------------------------------------
# Return encoder output frequency in Hz at a given shaft speed
def pulse_frequency(counts_per_rev: float, rpm: float) -> float:
    return counts_per_rev * rpm / 60.0


# ******************************************************************************
#
# NUMBER FORMATTING
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Format a calculated float for display without trailing noise
def format_engineering_number(value: float, significant: int = 7) -> str:
    """Render to a fixed number of significant digits, dropping trailing zeros.

    Significant digits rather than decimal places: a resolution of 0.0012207
    and a frequency of 204800 both want to stay readable, and a fixed number
    of decimals cannot do both.
    """
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return "—"
        if math.isinf(value):
            return "∞" if value > 0 else "-∞"
    if value == 0:
        return "0"

    # "g" drops trailing zeros and switches to exponential on the same rule
    # JavaScript's toPrecision uses, so both builds of the tool agree.
    return f"{value:.{significant}g}"
