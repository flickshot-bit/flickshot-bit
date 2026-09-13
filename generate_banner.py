from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import html
import random

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

WIDTH = 1180
HEIGHT = 610

PHOTO_PATH = ASSETS / "profile.png"
OUTPUT_DARK = ROOT / "dark.svg"
OUTPUT_LIGHT = ROOT / "light.svg"

GRID_W = 105
GRID_H = 118

random.seed(42)


def load_portrait():
    image = Image.open(PHOTO_PATH).convert("RGB")

    target_ratio = GRID_W / GRID_H
    image_ratio = image.width / image.height

    if image_ratio > target_ratio:
        new_width = int(image.height * target_ratio)
        left = (image.width - new_width) // 2

        image = image.crop(
            (
                left,
                0,
                left + new_width,
                image.height
            )
        )
    else:
        new_height = int(image.width / target_ratio)
        top = max(0, (image.height - new_height) // 2)

        image = image.crop(
            (
                0,
                top,
                image.width,
                top + new_height
            )
        )

    image = image.resize(
        (GRID_W, GRID_H),
        Image.Resampling.LANCZOS
    )

    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image, cutoff=1)

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.3)

    image = image.filter(
        ImageFilter.UnsharpMask(
            radius=3,
            percent=140,
            threshold=3
        )
    )

    return image


def dither(image):
    pixels = image.load()

    matrix = [
        [
            float(pixels[x, y])
            for x in range(image.width)
        ]
        for y in range(image.height)
    ]

    for y in range(image.height):
        reverse = y % 2 == 1

        if reverse:
            xs = range(
                image.width - 1,
                -1,
                -1
            )
        else:
            xs = range(image.width)

        for x in xs:
            old = matrix[y][x]

            new = 255 if old >= 128 else 0

            error = old - new

            matrix[y][x] = new

            direction = -1 if reverse else 1

            next_x = x + direction

            if 0 <= next_x < image.width:
                matrix[y][next_x] += (
                    error * 7 / 16
                )

            if y + 1 < image.height:
                matrix[y + 1][x] += (
                    error * 5 / 16
                )

                prev_x = x - direction
                next_x = x + direction

                if 0 <= prev_x < image.width:
                    matrix[y + 1][prev_x] += (
                        error * 3 / 16
                    )

                if 0 <= next_x < image.width:
                    matrix[y + 1][next_x] += (
                        error * 1 / 16
                    )

    return matrix


def portrait_points():
    image = load_portrait()
    matrix = dither(image)

    points = []

    left = 65
    top = 110

    frame_w = 380
    frame_h = 385

    cell_w = frame_w / GRID_W
    cell_h = frame_h / GRID_H

    for y in range(GRID_H):
        for x in range(GRID_W):
            value = matrix[y][x]

            if value < 128:
                px = (
                    left
                    + x * cell_w
                    + cell_w / 2
                )

                py = (
                    top
                    + y * cell_h
                    + cell_h / 2
                )

                jitter_x = random.uniform(
                    -0.9,
                    0.9
                )

                jitter_y = random.uniform(
                    -0.9,
                    0.9
                )

                radius = random.uniform(
                    0.65,
                    1.35
                )

                points.append(
                    (
                        px + jitter_x,
                        py + jitter_y,
                        radius
                    )
                )

    return points


def circles(points):
    output = []

    for x, y, radius in points:
        output.append(
            (
                f'<circle '
                f'cx="{x:.2f}" '
                f'cy="{y:.2f}" '
                f'r="{radius:.2f}"/>'
            )
        )

    return "".join(output)


def text(
    x,
    y,
    value,
    size=13,
    weight="400",
    opacity=1
):
    safe = html.escape(value)

    return (
        f'<text '
        f'x="{x}" '
        f'y="{y}" '
        f'font-family="ui-monospace,'
        f'SFMono-Regular,Menlo,Monaco,'
        f'Consolas,monospace" '
        f'font-size="{size}px" '
        f'font-weight="{weight}" '
        f'fill="currentColor" '
        f'opacity="{opacity}">'
        f'{safe}'
        f'</text>'
    )


def line(
    x1,
    y1,
    x2,
    y2,
    opacity=1
):
    return (
        f'<line '
        f'x1="{x1}" '
        f'y1="{y1}" '
        f'x2="{x2}" '
        f'y2="{y2}" '
        f'stroke="currentColor" '
        f'opacity="{opacity}"/>'
    )


def build_svg(points, dark=True):
    bg = (
        "#090b10"
        if dark
        else "#ffffff"
    )

    fg = (
        "#f3f4f6"
        if dark
        else "#111827"
    )

    muted = (
        "#8b949e"
        if dark
        else "#6b7280"
    )

    red = "#ff4d4d"

    portrait = circles(points)

    info = [
        (
            "Subject",
            "Aditya Kumar"
        ),
        (
            "Role",
            "Full Stack Developer"
        ),
        (
            "Focus",
            "DSA · Full Stack · Cloud Security"
        ),
        (
            "Status",
            "Learning · Building · Shipping"
        ),
        (
            "ToolChain",
            "VS Code · Git · GitHub · Figma · Postman"
        ),
        (
            "Core.Lang",
            "C++ · Python · JavaScript"
        ),
        (
            "Core.Frontend",
            "React.js · Next.js · GSAP · Framer"
        ),
        (
            "Core.Backend",
            "FastAPI"
        ),
        (
            "Core.Database",
            "PostgreSQL · SQL"
        ),
        (
            "Core.Cloud",
            "AWS"
        ),
        (
            "Core.Infra",
            "Docker · GitHub Actions"
        )
    ]

    info_markup = []

    start_y = 155

    for index, (label, value) in enumerate(info):
        y = start_y + index * 29

        info_markup.append(
            text(
                510,
                y,
                label,
                12,
                "700"
            )
        )

        info_markup.append(
            text(
                655,
                y,
                value,
                11,
                "400",
                0.92
            )
        )

        info_markup.append(
            line(
                510,
                y + 9,
                1110,
                y + 9,
                0.10
            )
        )

    social = [
        (
            "MAIL",
            "Available on request"
        ),
        (
            "PORTFOLIO",
            "Coming soon"
        ),
        (
            "LINKEDIN",
            "linkedin.com/in/adityakumar"
        ),
        (
            "GITHUB",
            "github.com/flickshot-bit"
        )
    ]

    social_markup = []

    for index, (label, value) in enumerate(social):
        y = 470 + index * 22

        social_markup.append(
            text(
                510,
                y,
                label,
                10,
                "700"
            )
        )

        social_markup.append(
            text(
                655,
                y,
                value,
                10,
                "400",
                0.80
            )
        )

    logo_sequence = """
    <g id="logo-cpp" opacity="0">
        <rect
            x="910"
            y="75"
            width="105"
            height="42"
            rx="21"
            fill="currentColor"
            opacity="0.06"
            stroke="currentColor"
            stroke-width="1"
            stroke-opacity="0.18"/>

        <text
            x="962.5"
            y="103"
            text-anchor="middle"
            font-family="Arial,sans-serif"
            font-size="21"
            font-weight="800"
            fill="currentColor">
            C++
        </text>
    </g>

    <g id="logo-react" opacity="0">
        <rect
            x="910"
            y="75"
            width="105"
            height="42"
            rx="21"
            fill="currentColor"
            opacity="0.06"
            stroke="currentColor"
            stroke-width="1"
            stroke-opacity="0.18"/>

        <g
            transform="
                translate(962.5 96)
                scale(0.20)
            "
        >
            <circle
                cx="0"
                cy="0"
                r="46"
                fill="none"
                stroke="currentColor"
                stroke-width="7"/>

            <ellipse
                cx="0"
                cy="0"
                rx="75"
                ry="25"
                fill="none"
                stroke="currentColor"
                stroke-width="7"/>

            <ellipse
                cx="0"
                cy="0"
                rx="75"
                ry="25"
                transform="rotate(60)"
                fill="none"
                stroke="currentColor"
                stroke-width="7"/>

            <ellipse
                cx="0"
                cy="0"
                rx="75"
                ry="25"
                transform="rotate(-60)"
                fill="none"
                stroke="currentColor"
                stroke-width="7"/>

            <circle
                cx="0"
                cy="0"
                r="9"
                fill="currentColor"/>
        </g>
    </g>

    <g id="logo-aws" opacity="0">
        <rect
            x="910"
            y="75"
            width="105"
            height="42"
            rx="21"
            fill="currentColor"
            opacity="0.06"
            stroke="currentColor"
            stroke-width="1"
            stroke-opacity="0.18"/>

        <text
            x="962.5"
            y="101"
            text-anchor="middle"
            font-family="Arial,sans-serif"
            font-size="21"
            font-weight="800"
            fill="currentColor">
            aws
        </text>

        <path
            d="M940 106 Q962.5 117 985 106"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"/>
    </g>
    """

    svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

    <style>
        svg {{
            color: {fg};
            background: {bg};
        }}

        .terminal {{
            fill: {bg};
            stroke: currentColor;
            stroke-width: 1.5;
        }}

        .portrait {{
            fill: currentColor;
        }}

        .live {{
            animation:
                pulse 1.5s ease-in-out infinite;
        }}

        #portrait {{
            animation:
                portraitIntro 3.2s ease-out 1;
            transform-origin:
                255px 300px;
        }}

        #logo-cpp {{
            animation:
                cppMorph 14.2s linear infinite;
        }}

        #logo-react {{
            animation:
                reactMorph 14.2s linear infinite;
        }}

        #logo-aws {{
            animation:
                awsMorph 14.2s linear infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}

            50% {{
                opacity: 0.35;
            }}
        }}

        @keyframes portraitIntro {{
            0% {{
                opacity: 0;
                transform: scale(0.94);
            }}

            70% {{
                opacity: 1;
            }}

            100% {{
                opacity: 1;
                transform: scale(1);
            }}
        }}

        @keyframes cppMorph {{
            0%, 21% {{
                opacity: 1;
            }}

            23%, 100% {{
                opacity: 0;
            }}
        }}

        @keyframes reactMorph {{
            0%, 23% {{
                opacity: 0;
            }}

            30%, 51% {{
                opacity: 1;
            }}

            53%, 100% {{
                opacity: 0;
            }}
        }}

        @keyframes awsMorph {{
            0%, 53% {{
                opacity: 0;
            }}

            60%, 81% {{
                opacity: 1;
            }}

            83%, 100% {{
                opacity: 0;
            }}
        }}

        text {{
            dominant-baseline: alphabetic;
        }}
    </style>

    <rect
        class="terminal"
        x="10"
        y="10"
        width="1160"
        height="590"
        rx="18"/>

    <circle
        cx="35"
        cy="35"
        r="5"
        fill="#ff5f57"/>

    <circle
        cx="53"
        cy="35"
        r="5"
        fill="#febc2e"/>

    <circle
        cx="71"
        cy="35"
        r="5"
        fill="#28c840"/>

    {text(
        590,
        40,
        "profile.sh --live",
        12,
        "600"
    )}

    <rect
        x="1050"
        y="22"
        width="82"
        height="27"
        rx="13.5"
        fill="{red}"
        opacity="0.16"/>

    <circle
        cx="1067"
        cy="35.5"
        r="4"
        fill="{red}"
        class="live"/>

    {text(
        1078,
        40,
        "LIVE",
        10,
        "800"
    )}

    {line(
        25,
        62,
        1155,
        62,
        0.18
    )}

    <rect
        x="45"
        y="78"
        width="420"
        height="480"
        rx="12"
        fill="none"
        stroke="currentColor"
        opacity="0.22"/>

    {text(
        65,
        103,
        "VISUAL.MAP",
        11,
        "700"
    )}

    <g
        id="portrait"
        class="portrait"
    >
        {portrait}
    </g>

    {text(
        510,
        103,
        "SYSTEM.INFO",
        11,
        "700"
    )}

    <g id="tech-morph">
        {logo_sequence}
    </g>

    {''.join(info_markup)}

    {''.join(social_markup)}

    {line(
        510,
        565,
        1110,
        565,
        0.15
    )}

    {text(
        510,
        585,
        "C++ → React → AWS",
        10,
        "600",
        0.55
    )}

    {text(
        920,
        585,
        "BUILD • SHIP • LEARN",
        10,
        "600",
        0.55
    )}

    </svg>
    """

    return svg


def main():
    points = portrait_points()

    dark_svg = build_svg(
        points,
        dark=True
    )

    light_svg = build_svg(
        points,
        dark=False
    )

    OUTPUT_DARK.write_text(
        dark_svg,
        encoding="utf-8"
    )

    OUTPUT_LIGHT.write_text(
        light_svg,
        encoding="utf-8"
    )

    print(
        f"Generated: {OUTPUT_DARK}"
    )

    print(
        f"Generated: {OUTPUT_LIGHT}"
    )

    print(
        f"Portrait particles: {len(points)}"
    )


if __name__ == "__main__":
    main()