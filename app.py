import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

import requests
import certifi
from io import StringIO

from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Pro-social Card Propagation Graph Demo", layout="wide")

st.title("BoomTown Behaviour Card Analysis")

st_autorefresh(interval=2000, key="refresh")

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

cardtype_colors = {
    "Recognition": "#F5A623",
    "Generosity": "#2ECC71",
    "Bridge-building": "#8E44AD",
    "Reciprocity": "#3498DB",
}

col1, col2, col3 = st.columns(3)

col1.metric("Total scans", len(df))
col2.metric("Active attendees", df["AppId"].nunique())
col3.metric("Inferred graph edges", len(edges_df))

st.subheader("Pro-social card propagation graph")

nodes = [
    Node(
        id=attendee,
        label=attendee,
        size=25,
    )
    for attendee in sorted(df["AppId"].unique())
]

graph_edges = [
    Edge(
        source=row["from"],
        target=row["to"],
        label=f'{row["card_type"]} ({row["card_id"]})',
    )
    for _, row in edges_df.iterrows()
]

config = Config(
    width="100%",
    height=500,
    directed=True,
    physics=True,
    hierarchical=False,
    edges={
        "font": {
            "size": 9,
            # "align": "middle"
        },
        "smooth": True
    }
)

agraph(nodes=nodes, edges=graph_edges, config=config)

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

st.subheader("Derived graph edges")
st.dataframe(edges_df, use_container_width=True)

st.subheader("Raw card scan events")
st.dataframe(df, use_container_width=True)