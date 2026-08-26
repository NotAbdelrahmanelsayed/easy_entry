# Pure-Python Code 128B SVG barcode generator.
# No external dependencies — uses only the bar-pattern table from the spec.
# Exposed as a Jinja global via hooks.py so print format templates can call
# {{ code128_svg(value) }} to get an inline SVG with zero external HTTP requests.

# Bar patterns indexed 0-106.  Each integer's decimal digits are the bar/space
# bit-string (1 = black bar, 0 = white space).  Values 0-102 are data symbols,
# 103=START_A, 104=START_B, 105=START_C, 106=STOP (13 bits, hence a larger int).
_BARS = [
    11011001100, 11001101100, 11001100110, 10010011000, 10010001100,
    10001001100, 10011001000, 10011000100, 10001100100, 11001001000,
    11001000100, 11000100100, 10110011100, 10011011100, 10011001110,
    10111001100, 10011101100, 10011100110, 11001110010, 11001011100,
    11001001110, 11011100100, 11001110100, 11101101110, 11101001100,
    11100101100, 11100100110, 11101100100, 11100110100, 11100110010,
    11011011000, 11011000110, 11000110110, 10100011000, 10001011000,
    10001000110, 10110001000, 10001101000, 10001100010, 11010001000,
    11000101000, 11000100010, 10110111000, 10110001110, 10001101110,
    10111011000, 10111000110, 10001110110, 11101110110, 11010001110,
    11000101110, 11011101000, 11011100010, 11011101110, 11101011000,
    11101000110, 11100010110, 11101101000, 11101100010, 11100011010,
    11101111010, 11001000010, 11110001010, 10100110000, 10100001100,
    10010110000, 10010000110, 10000101100, 10000100110, 10110010000,
    10110000100, 10011010000, 10011000010, 10000110100, 10000110010,
    11000010010, 11001010000, 11110111010, 11000010100, 10001111010,
    10100111100, 10010111100, 10010011110, 10111100100, 10011110100,
    10011110010, 11110100100, 11110010100, 11110010010, 11011011110,
    11011110110, 11110110110, 10101111000, 10100011110, 10001011110,
    10111101000, 10111100010, 11110101000, 11110100010, 10111011110,
    10111101110, 11101011110, 11110101110, 11010000100, 11010010000,
    11010011100, 1100011101011,  # index 106 = STOP (13-bit pattern)
]

_START_B = 104
_STOP = 106
_QUIET = 10  # quiet-zone width in bar-module units on each side


def code128_svg(value, width_mm=50, height_mm=17):
    """Return a Code 128B barcode as an SVG string for inline Jinja embedding.

    The SVG is sized to width_mm × height_mm.  Non-encodable characters
    (outside ASCII 32-126) are silently replaced with a space.
    """
    value = str(value)

    # Map each character to its Code 128B symbol value (ASCII - 32).
    data_values = []
    for ch in value:
        c = ord(ch)
        if not (32 <= c <= 126):
            c = 32
        data_values.append(c - 32)

    # Checksum: START_B + sum of (1-based position × symbol value), mod 103.
    check_value = (_START_B + sum((i + 1) * v for i, v in enumerate(data_values))) % 103

    symbols = [_START_B] + data_values + [check_value, _STOP]

    # Build the full bit-string for all symbols.
    bits = "".join(str(_BARS[s]) for s in symbols)

    total_w = len(bits) + 2 * _QUIET  # barcode width in modules

    # Scale module units directly to mm so the viewBox aspect ratio matches
    # the physical output aspect ratio exactly.  wkhtmltopdf's WebKit does
    # not reliably honor preserveAspectRatio="none" — when the viewBox
    # aspect ratio differs from width_mm:height_mm, it falls back to
    # aspect-preserving "meet" scaling and edge-aligns the result (observed
    # as an empty gap on one side), the same class of bug as the SVG
    # height:100% collapse documented in CLAUDE.md.  Matching the aspect
    # ratios up front makes that fallback behavior a no-op.
    scale = width_mm / total_w

    # RLE-encode bits into SVG <rect> elements (only black bars need rects).
    rects = []
    x = _QUIET
    i = 0
    n = len(bits)
    while i < n:
        b = bits[i]
        j = i + 1
        while j < n and bits[j] == b:
            j += 1
        if b == "1":
            rects.append(
                f'<rect x="{x * scale:.3f}" y="0" width="{(j - i) * scale:.3f}" height="{height_mm}"/>'
            )
        x += j - i
        i = j

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{width_mm}mm" height="{height_mm}mm"'
        f' viewBox="0 0 {width_mm} {height_mm}"'
        f' preserveAspectRatio="none"'
        f' style="display:block">'
        + "".join(rects)
        + "</svg>"
    )
