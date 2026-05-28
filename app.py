import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

import requests
import certifi
from io import StringIO

import streamlit.components.v1 as components

# from streamlit_autorefresh import st_autorefresh

from pathlib import Path
import base64

def image_to_base64(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        return None

    suffix = image_path.suffix.lower().replace(".", "")
    mime = "jpeg" if suffix in ["jpg", "jpeg"] else "png"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    return f"data:image/{mime};base64,{encoded}"

st.set_page_config(page_title="Pro-social Card Propagation Graph Demo", layout="wide")

st.markdown(
    """
    <style>
    /* Main app text */
    .stApp {
        color: #F7F1E8;
    }

    /* Reduce vertical gap after horizontal rule */
    hr {
        margin-top: 1.2rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Reduce Streamlit block spacing generally */
    div[data-testid="stVerticalBlock"] {
        gap: 0.8rem !important;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Main page headings */
    h1 {
        color: #FFE8B5 !important;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.2rem !important;
    }

    h2, h3 {
        color: #F7F1E8 !important;
        font-weight: 750 !important;
        font-size: 1.5rem !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.4rem !important;
    }

    # p {
    #     font-size: 1.0rem !important;
    # }

    /* Normal markdown text */
    .stMarkdown, .stMarkdown p {
        color: #D9D3E8 !important;
    }

    /* Metric labels */
    div[data-testid="stMetricLabel"] {
        color: #C9BFEA !important;
        font-size: 0.75rem !important;
    }

    /* Metric values */
    div[data-testid="stMetricValue"] {
        color: #FFB347 !important;
        font-weight: 800 !important;
        font-size: 1.55rem !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 18px;
        padding: 10px 14px !important;
        min-height: 70px;
    }

    /* Expander text */
    details, summary {
        color: #F7F1E8 !important;
    }

    @keyframes floatDeck {
        0% {
            transform: translateY(0px) rotate(0deg);
        }
        50% {
            transform: translateY(-5px) rotate(0.8deg);
        }
        100% {
            transform: translateY(0px) rotate(0deg);
        }
    }

    .floating-card-deck {
        animation: floatDeck 5.5s ease-in-out infinite;
    }
    </style>
    """,
    unsafe_allow_html=True
)

title_col, card_col = st.columns([4.2, 1.3])

with title_col:
    st.markdown(
        """
        <h1 style="color:#FFE8B5; margin-top:8px; margin-bottom:0;">
            Behaviour Cards - Recognition in Motion
        </h1>
        <p style="color:#D9D3E8; font-size:18px; margin-top:8px;">
            A card starts as recognition. The graph shows how recognition spreads.
        </p>
        <hr style="border:0.5px solid rgba(255,255,255,0.14); margin: 18px 0 10px 0;">
        """,
        unsafe_allow_html=True
    )

with card_col:
    card_paths = [
        "assets/cards/Botanist.png",
        "assets/cards/Creator.png",
        "assets/cards/Healer.png",
        "assets/cards/Distruptor.png",
    ]

    # card_paths = [
    #     "assets/cards/dummy.png",
    #     "assets/cards/dummy.png",
    #     "assets/cards/dummy.png",
    #     "assets/cards/dummy.png",
    # ]

    card_images = [image_to_base64(path) for path in card_paths]
    card_images = [img for img in card_images if img is not None]

    if card_images:
        cards_html = ""

        rotations = [-8, -2, 2, 8]
        offsets = [0, 46, 92, 138]

        for i, img in enumerate(card_images):
            cards_html += f"""
            <img src="{img}" style="
                position:absolute;
                left:{offsets[i]}px;
                top:8px;
                width:64px;
                border-radius:8px;
                border:1.5px solid rgba(255,255,255,0.45);
                background:rgba(255,255,255,0.04);
                transform:rotate({rotations[i]}deg);
                box-shadow:0 8px 22px rgba(0,0,0,0.45);
                z-index:{i + 1};
            ">
            """

        with card_col:
            st.markdown(
                f"""
                <div class="floating-card-deck" style="
                    position:relative;
                    height:140px;
                    width:235px;
                    overflow:visible;
                    margin-top:36px;
                    margin-left:auto;
                    margin-right:10px;
                ">
                    {cards_html}
                </div>
                """,
                unsafe_allow_html=True
            )


# st_autorefresh(interval=2000, key="refresh")

sheet_id = "1unenIebQ7hrO1tfDIYCxTVNaVPeLdb2k1EvKmeLWXYE"
gid = "0"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"


response = requests.get(url, verify=certifi.where())
response.raise_for_status()

df = pd.read_csv(StringIO(response.text))

# st.dataframe(df)


# df = pd.read_csv("card_scans.csv")
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

edges = []

for card_id, group in df.groupby("CardId"):
    group = group.sort_values("Timestamp")

    previous_row = None

    for _, row in group.iterrows():
        if previous_row is not None:
            edges.append({
                "from": previous_row["AppId"],
                "to": row["AppId"],
                "card_id": card_id,
                "card_type": row["CardType"],
                "Timestamp": row["Timestamp"]
            })

        previous_row = row

edges_df = pd.DataFrame(edges)


col1, col2, col3 = st.columns(3)

col1.metric("Total scans", len(df))
col2.metric("Active attendees", df["AppId"].nunique())
col3.metric("Inferred graph edges", len(edges_df))

scan_counts = df["AppId"].value_counts().to_dict()


nodes = [
    Node(
        id=attendee,
        label=attendee,
        size=32,
        color={
            "background": "#123C4A",   # muted deep teal
            "border": "#48C6C8",       # soft cyan outline
            "highlight": {
                "background": "#1F6F7A",
                "border": "#8BE9E9",
            },
        },
        font={
            "color": "#F7F1E8",
            "size": 18,
            "face": "sans-serif",
            "strokeWidth": 0,
        },
    )
    for attendee in sorted(df["AppId"].unique())
]

palette = [
    "#2ECC71",  # green
    "#F5A623",  # amber
    "#9B59B6",  # purple
    "#3498DB",  # blue
    "#FF6B6B",  # coral
    "#1ABC9C",  # teal
    "#E67E22",  # orange
    "#E84393",  # pink
]

card_types = sorted(df["CardType"].dropna().unique())

cardtype_colors = {
    card_type: palette[i % len(palette)]
    for i, card_type in enumerate(card_types)
}

graph_edges = [
    Edge(
        source=row["from"],
        target=row["to"],
        label=f'{row["card_id"]}',
        color=cardtype_colors.get(row["card_type"], "#F5A623"),
        width=2,
        font={
            "color": "#F7F1E8",
            "size": 12,
            "strokeWidth": 0,
            "align": "middle",
        },
        arrows={
            "to": {
                "enabled": True,
                "scaleFactor": 0.7,
            }
        },
    )
    for _, row in edges_df.iterrows()
]

legend_items = " ".join(
    [
        f'<span style="color:{colour};">● {card_type}</span>&nbsp;&nbsp;'
        for card_type, colour in cardtype_colors.items()
    ]
)


config = Config(
    width="100%",
    height=560,
    directed=True,
    physics=True,
    hierarchical=False,
    nodeHighlightBehavior=True,
    highlightColor="#F5A623",
    collapsible=False,
)

# Dynamic vertical legend from backend/card types
legend_html = "".join(
    [
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:8px;
            margin-bottom:6px;
            font-size:14px;
            color:#D9D3E8;
        ">
            <span style="
                width:11px;
                height:11px;
                border-radius:50%;
                background:{colour};
                display:inline-block;
                box-shadow:0 0 10px {colour};
            "></span>
            <span>{card_type}</span>
        </div>
        """
        for card_type, colour in cardtype_colors.items()
    ]
)

header_col, legend_col = st.columns([3, 1])

# st.subheader("Pro-social card propagation graph")

with header_col:
    st.subheader("Pro-social card propagation graph")

with legend_col:
    st.markdown(
        f"""
        <div style="
            padding-top:10px;
            text-align:left;
        ">
            <p style="
                color:#FFE8B5;
                font-weight:700;
                margin-bottom:8px;
                font-size:14px;
            ">
                Card type colours
            </p>
            {legend_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# agraph(nodes=nodes, edges=graph_edges, config=config)

components.html(
    f"""
    <div id="graph-container" style="
        width:100%;
        height:560px;
        border-radius:16px;
        background:transparent;
        overflow:hidden;
    "></div>

    <div id="graph-status" style="
        color:#BFB7D8;
        font-family:sans-serif;
        font-size:13px;
        margin-top:8px;
    ">
        Listening for new scans...
    </div>

    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>

    <script>
    const csvUrl = "{url}";

    const palette = [
        "#2ECC71",
        "#F5A623",
        "#9B59B6",
        "#3498DB",
        "#FF6B6B",
        "#1ABC9C",
        "#E67E22",
        "#E84393"
    ];

    const nodes = new vis.DataSet([]);
    const edges = new vis.DataSet([]);

    const seenNodes = new Set();
    const seenEdges = new Set();

    const container = document.getElementById("graph-container");

    const data = {{
        nodes: nodes,
        edges: edges
    }};

    const options = {{
        autoResize: true,

        layout: {{
            improvedLayout: true,
            randomSeed: 12
        }},

        nodes: {{
            shape: "dot",
            size: 20,
            color: {{
                background: "#123C4A",
                border: "#48C6C8",
                highlight: {{
                    background: "#1F6F7A",
                    border: "#8BE9E9"
                }}
            }},
            font: {{
                color: "#F7F1E8",
                size: 16,
                face: "sans-serif",
                strokeWidth: 0
            }},
            borderWidth: 2
        }},

        edges: {{
            width: 2,
            arrows: {{
                to: {{
                    enabled: true,
                    scaleFactor: 0.65
                }}
            }},
            font: {{
                color: "#F7F1E8",
                size: 11,
                strokeWidth: 0,
                align: "middle"
            }},
            smooth: {{
                enabled: true,
                type: "continuous",
                roundness: 0.4
            }}
        }},

        physics: {{
            enabled: true,
            solver: "repulsion",
            repulsion: {{
                nodeDistance: 100,
                centralGravity: 0.012,
                springLength: 75,
                springConstant: 0.07,
                damping: 0.34
            }},
            stabilization: {{
                enabled: true,
                iterations: 160,
                updateInterval: 25,
                fit: true
            }},
            minVelocity: 0.5
        }},

        interaction: {{
            hover: true,
            tooltipDelay: 100,
            dragNodes: true,
            zoomView: true,
            dragView: true
        }}
    }};

    const network = new vis.Network(container, data, options);

    function getCardTypeColours(rows) {{
        const cardTypes = [...new Set(rows.map(r => r.CardType).filter(Boolean))].sort();
        const colours = {{}};

        cardTypes.forEach((type, index) => {{
            colours[type] = palette[index % palette.length];
        }});

        return colours;
    }}

    function deriveEdges(rows) {{
        const grouped = {{}};

        rows.forEach(row => {{
            if (!row.Timestamp || !row.AppId || !row.CardId || !row.CardType) return;

            if (!grouped[row.CardId]) {{
                grouped[row.CardId] = [];
            }}

            grouped[row.CardId].push(row);
        }});

        const derived = [];

        Object.keys(grouped).forEach(cardId => {{
            const group = grouped[cardId].sort((a, b) => {{
                return new Date(a.Timestamp) - new Date(b.Timestamp);
            }});

            for (let i = 1; i < group.length; i++) {{
                const previous = group[i - 1];
                const current = group[i];

                if (previous.AppId !== current.AppId) {{
                    derived.push({{
                        source: previous.AppId,
                        target: current.AppId,
                        cardId: cardId,
                        cardType: current.CardType,
                        timestamp: current.Timestamp
                    }});
                }}
            }}
        }});

        return derived;
    }}

    async function updateGraph() {{
        try {{
            const response = await fetch(csvUrl + "&cacheBust=" + Date.now());
            const csvText = await response.text();

            const parsed = Papa.parse(csvText, {{
                header: true,
                skipEmptyLines: true
            }});

            const rows = parsed.data;
            const cardTypeColours = getCardTypeColours(rows);
            const derivedEdges = deriveEdges(rows);

            rows.forEach(row => {{
                if (!row.AppId) return;

                if (!seenNodes.has(row.AppId)) {{
                    seenNodes.add(row.AppId);

                    nodes.add({{
                        id: row.AppId,
                        label: row.AppId
                    }});
                }}
            }});

            derivedEdges.forEach(edge => {{
                const edgeId = edge.source + "__" + edge.target + "__" + edge.cardId + "__" + edge.timestamp;

                if (!seenEdges.has(edgeId)) {{
                    seenEdges.add(edgeId);

                    edges.add({{
                        id: edgeId,
                        from: edge.source,
                        to: edge.target,
                        label: edge.cardId,
                        color: {{
                            color: cardTypeColours[edge.cardType] || "#F5A623"
                        }},
                        title: edge.cardType + " card " + edge.cardId
                    }});
                }}
            }});

            document.getElementById("graph-status").innerHTML =
                "Live graph connected " +
                " · Last checked: " + new Date().toLocaleTimeString();

        }} catch (error) {{
            document.getElementById("graph-status").innerHTML =
                "Could not update graph: " + error;
        }}
    }}

    updateGraph();
    setInterval(updateGraph, 3000);
    </script>
    """,
    height=600,
)

st.subheader("Emerging pro-social insights")

if not edges_df.empty:
    most_travelled_card = (
        df.groupby("CardId")["AppId"]
        .nunique()
        .sort_values(ascending=False)
        .index[0]
    )

    most_travelled_count = df.groupby("CardId")["AppId"].nunique().max()

    most_common_cardtype = df["CardType"].value_counts().idxmax()

    latest_event = df.sort_values("Timestamp").iloc[-1]

    c1, c2, c3 = st.columns(3)

    c1.success(
        f"Card **{most_travelled_card}** has travelled through "
        f"**{most_travelled_count} attendees**."
    )

    c2.info(
        f"The most active pro-social signal so far is "
        f"**{most_common_cardtype}**."
    )

    c3.warning(
        f"Latest scan: **{latest_event['AppId']}** scanned "
        f"**{latest_event['CardType']}** card **{latest_event['CardId']}**."
    )
else:
    st.info("Not enough scans yet to infer card propagation.")

with st.expander("Technical detail: derived card journeys", expanded=False):
    st.dataframe(edges_df, use_container_width=True)

with st.expander("Technical detail: raw card scan events", expanded=False):
    st.dataframe(df, use_container_width=True)