import os
import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "Omkareshwar-17")
TOKEN = os.environ["GITHUB_TOKEN"]

# ---------------------------------------------------------
# FETCH REAL GITHUB CONTRIBUTIONS
# ---------------------------------------------------------

query = """
query($userName:String!) {
  user(login: $userName) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": query,
    "variables": {
        "userName": USERNAME
    }
}).encode()

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "batcomputer-contribution-generator"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode())

if "errors" in result:
    raise RuntimeError(result["errors"])

weeks = (
    result["data"]["user"]["contributionsCollection"]
    ["contributionCalendar"]["weeks"]
)

# ---------------------------------------------------------
# SVG SETTINGS
# ---------------------------------------------------------

WIDTH = 1200
HEIGHT = 330

CELL = 14
GAP = 5
STEP = CELL + GAP

GRID_X = 90
GRID_Y = 90

# Batman / Gotham palette
BACKGROUND = "#0d1117"
EMPTY = "#161b22"
LEVEL_1 = "#30363d"
LEVEL_2 = "#665c24"
LEVEL_3 = "#a68b18"
LEVEL_4 = "#F5C518"

TEXT = "#8b949e"
WHITE = "#f0f6fc"
YELLOW = "#F5C518"

# ---------------------------------------------------------
# CONTRIBUTION LEVEL
# ---------------------------------------------------------

all_counts = []

for week in weeks:
    for day in week["contributionDays"]:
        count = day["contributionCount"]
        if count > 0:
            all_counts.append(count)

maximum = max(all_counts) if all_counts else 1


def contribution_color(count):
    if count == 0:
        return EMPTY

    ratio = count / maximum

    if ratio <= 0.25:
        return LEVEL_1
    elif ratio <= 0.50:
        return LEVEL_2
    elif ratio <= 0.75:
        return LEVEL_3
    else:
        return LEVEL_4


# ---------------------------------------------------------
# BUILD CONTRIBUTION CELLS
# ---------------------------------------------------------

cells = []

for week_index, week in enumerate(weeks):

    for day_index, day in enumerate(week["contributionDays"]):

        x = GRID_X + week_index * STEP
        y = GRID_Y + day_index * STEP

        count = day["contributionCount"]
        color = contribution_color(count)

        cells.append(
            f'''
            <rect
                x="{x}"
                y="{y}"
                width="{CELL}"
                height="{CELL}"
                rx="3"
                fill="{color}">
            </rect>
            '''
        )


# ---------------------------------------------------------
# FINAL SVG
# ---------------------------------------------------------

svg = f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

    <defs>

        <!-- Headlight glow -->
        <filter id="yellowGlow"
                x="-100%"
                y="-100%"
                width="300%"
                height="300%">

            <feGaussianBlur
                stdDeviation="6"
                result="blur"/>

            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>

        </filter>

        <!-- Headlight beam -->
        <linearGradient
            id="headlightBeam"
            x1="0"
            x2="1">

            <stop
                offset="0%"
                stop-color="{YELLOW}"
                stop-opacity="0.65"/>

            <stop
                offset="100%"
                stop-color="{YELLOW}"
                stop-opacity="0"/>

        </linearGradient>

    </defs>


    <!-- BACKGROUND -->

    <rect
        width="{WIDTH}"
        height="{HEIGHT}"
        fill="{BACKGROUND}"/>


    <!-- TITLE -->

    <text
        x="{WIDTH / 2}"
        y="40"
        text-anchor="middle"
        fill="{YELLOW}"
        font-family="monospace"
        font-size="21"
        font-weight="bold">

        BATCOMPUTER // GOTHAM NIGHT PATROL

    </text>


    <!-- CONTRIBUTION GRID -->

    <g id="contribution-grid">

        {''.join(cells)}

    </g>


    <!-- ROAD -->

    <line
        x1="30"
        y1="245"
        x2="1170"
        y2="245"
        stroke="#30363d"
        stroke-width="3"/>


    <!-- ROAD MARKINGS -->

    <line
        x1="40"
        y1="267"
        x2="1160"
        y2="267"
        stroke="#21262d"
        stroke-width="2"
        stroke-dasharray="30 22"/>


    <!-- ================================================= -->
    <!-- BATMOBILE                                         -->
    <!-- ================================================= -->

    <g id="batmobile">

        <animateTransform
            attributeName="transform"
            type="translate"
            values="
                -260 0;
                100 0;
                430 0;
                760 0;
                1260 0
            "
            keyTimes="
                0;
                0.18;
                0.45;
                0.72;
                1
            "
            dur="8s"
            repeatCount="indefinite"/>


        <!-- HEADLIGHT BEAM -->

        <polygon
            points="
                215,218
                470,180
                470,250
            "
            fill="url(#headlightBeam)"/>


        <!-- REAR BAT FIN -->

        <path
            d="
                M25 218
                L5 165
                L65 205
                Z
            "
            fill="#050505"
            stroke="#6e7681"
            stroke-width="2"/>


        <!-- MAIN BODY -->

        <path
            d="
                M20 220
                L48 205
                L72 176
                L125 169
                L163 194
                L205 202
                L225 218
                L215 232
                L25 232
                Z
            "
            fill="#050505"
            stroke="#8b949e"
            stroke-width="2"/>


        <!-- COCKPIT -->

        <path
            d="
                M78 177
                L100 153
                L132 156
                L160 194
                Z
            "
            fill="#161b22"
            stroke="#6e7681"
            stroke-width="2"/>


        <!-- FRONT FIN -->

        <path
            d="
                M175 198
                L211 166
                L200 207
                Z
            "
            fill="#050505"
            stroke="#6e7681"
            stroke-width="2"/>


        <!-- YELLOW BODY DETAIL -->

        <path
            d="
                M55 212
                L177 212
            "
            stroke="{YELLOW}"
            stroke-width="3"/>


        <!-- REAR WHEEL -->

        <circle
            cx="65"
            cy="230"
            r="20"
            fill="#010101"
            stroke="#6e7681"
            stroke-width="4"/>

        <circle
            cx="65"
            cy="230"
            r="7"
            fill="{YELLOW}"/>


        <!-- FRONT WHEEL -->

        <circle
            cx="178"
            cy="230"
            r="20"
            fill="#010101"
            stroke="#6e7681"
            stroke-width="4"/>

        <circle
            cx="178"
            cy="230"
            r="7"
            fill="{YELLOW}"/>


        <!-- HEADLIGHT -->

        <circle
            cx="215"
            cy="211"
            r="7"
            fill="{YELLOW}"
            filter="url(#yellowGlow)"/>


        <!-- REAR LIGHT -->

        <circle
            cx="25"
            cy="213"
            r="4"
            fill="#b62324"/>

    </g>


    <!-- STATUS -->

    <text
        x="{WIDTH / 2}"
        y="310"
        text-anchor="middle"
        fill="{TEXT}"
        font-family="monospace"
        font-size="14">

        REAL CONTRIBUTION DATA // BATMOBILE PATROL ACTIVE

    </text>

</svg>
'''

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

output = Path("dist")
output.mkdir(exist_ok=True)

file_path = output / "batmobile-contributions.svg"

file_path.write_text(svg, encoding="utf-8")

print(f"Generated: {file_path}")
print(f"Contribution weeks: {len(weeks)}")
print(f"Maximum daily contributions: {maximum}")
