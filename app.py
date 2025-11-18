import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import time

from genbank_parser import parse_genbank

# Optional Lottie animation
try:
    from streamlit_lottie import st_lottie
    import json
    LOTTIE_AVAILABLE = True
except:
    LOTTIE_AVAILABLE = False


# -----------------------------------------------------
# Page Setup + Elegant CSS
# -----------------------------------------------------
st.set_page_config(page_title="Genome Viewer", layout="wide")

st.markdown("""
<style>
.fade-in {
    animation: fadeIn 1.1s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.box {
    background: #f8f9fa;
    padding: 18px;
    border-radius: 14px;
    margin-top: 15px;
    margin-bottom: 20px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# Header
# -----------------------------------------------------
st.markdown("<h1 class='fade-in'>🧬 Genome Annotation Viewer</h1>", unsafe_allow_html=True)
st.write("A clean, animated genome viewer built using **Python**, **BioPython**, **Plotly**, and **Streamlit**.")

# DNA Animation if available
if LOTTIE_AVAILABLE:
    try:
        with open("dna.json", "r") as f:
            dna_anim = json.load(f)
        st_lottie(dna_anim, height=140)
    except:
        st.info("Add dna.json to enable Lottie animation.")


# -----------------------------------------------------
# Upload Box
# -----------------------------------------------------
st.markdown("<div class='box fade-in'>", unsafe_allow_html=True)
st.subheader("📁 Upload GenBank File")
uploaded = st.file_uploader("Upload a .gb or .gbff file", type=["gb", "gbff"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded is None:
    st.stop()


# -----------------------------------------------------
# Parse File (Animated Loader)
# -----------------------------------------------------
st.markdown("<div class='box fade-in'>", unsafe_allow_html=True)
st.subheader("🔄 Parsing Genome…")

with st.spinner("Reading and extracting features..."):
    time.sleep(0.4)
    
    file_content = uploaded.read().decode("utf-8")
    file_handle = io.StringIO(file_content)
    df, genome_length = parse_genbank(file_handle)

st.success(f"Genome loaded successfully — {genome_length:,} bp, {len(df)} features found.")
st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------
# Filters
# -----------------------------------------------------
st.sidebar.header("Filters")

types = sorted(df["Type"].unique().tolist())
selected_types = st.sidebar.multiselect("Feature Types", types, default=types)

filtered = df[df["Type"].isin(selected_types)].copy()

filtered["Start"] = filtered["Start"].astype(int)
filtered["End"] = filtered["End"].astype(int)
filtered["Length"] = filtered["End"] - filtered["Start"]


# -----------------------------------------------------
# LINEAR GENOME VIEW (Animated)
# -----------------------------------------------------
st.markdown("<div class='box fade-in'>", unsafe_allow_html=True)
st.subheader("📍 Linear Genome Map (Animated)")

# Unique Y labels
filtered = filtered.reset_index(drop=True)
filtered["y_label"] = (
    filtered.index.astype(str)
    + " | "
    + filtered["Type"]
    + " | "
    + filtered["Gene"].fillna("")
)

fig = go.Figure()

for ftype in filtered["Type"].unique():
    sub = filtered[filtered["Type"] == ftype]

    fig.add_trace(go.Bar(
        x=sub["Length"],
        y=sub["y_label"],
        base=sub["Start"],
        orientation="h",
        name=ftype,
        hovertemplate="Type: %{customdata[0]}<br>Gene: %{customdata[1]}<br>Start: %{base}<br>End: %{x+base}",
        customdata=sub[["Type", "Gene"]],
        marker_line_color="black",
        marker_line_width=0.6,
    ))

fig.update_traces(
    marker=dict(
        line=dict(width=1),
    ),
    hoverlabel=dict(bgcolor="white", font_size=14)
)

# Add animation
fig.update_layout(
    transition={"duration": 800, "easing": "cubic-in-out"},
    barmode="stack",
    height=700,
    title="Animated Linear Genome Visualization"
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)



# -----------------------------------------------------
# CIRCULAR GENOME VIEW (Animated)
# -----------------------------------------------------
st.markdown("<div class='box fade-in'>", unsafe_allow_html=True)
st.subheader("🔵 Circular Genome Map (Animated)")

# Convert Start/End to angles
filtered["angle_start"] = (filtered["Start"] / genome_length) * 360
filtered["angle_end"] = (filtered["End"] / genome_length) * 360
filtered["angle_mid"] = (filtered["angle_start"] + filtered["angle_end"]) / 2

circ_fig = go.Figure()

for _, row in filtered.iterrows():
    theta = [
        row["angle_start"],
        row["angle_mid"],
        row["angle_end"]
    ]
    r = [0.6, 1.0, 0.6]  # Arc thickness

    circ_fig.add_trace(go.Scatterpolar(
        r=r,
        theta=theta,
        mode="lines",
        fill="toself",
        line=dict(width=0),
        hoverinfo="text",
        text=(
            f"{row['Type']} | {row['Gene']}<br>"
            f"Start: {row['Start']}<br>"
            f"End: {row['End']}"
        ),
        name=row["Type"]
    ))

# Animate rotation on load
circ_fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=False),
        angularaxis=dict(
            rotation=90,
            direction="clockwise"
        )
    ),
    showlegend=False,
    height=700,
    margin=dict(l=0, r=0, t=40, b=0),
    title="Animated Circular Genome View",
    transition={"duration": 900, "easing": "cubic-in-out"},
)

st.plotly_chart(circ_fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)



# -----------------------------------------------------
# Feature Table
# -----------------------------------------------------
st.markdown("<div class='box fade-in'>", unsafe_allow_html=True)
st.subheader("📄 Feature Table")
st.dataframe(filtered, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
