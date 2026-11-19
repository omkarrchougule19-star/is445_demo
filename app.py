import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(page_title="Illinois State Buildings", layout="wide")

DATA_URL = ("https://raw.githubusercontent.com/UIUC-iSchool-DataViz/"
            "is445_data/main/building_inventory.csv")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # Year 0 means "unknown" in this dataset; drop those rows and empty buildings
    df = df[(df["Year Constructed"] >= 1800) & (df["Square Footage"] > 0)].copy()
    df["Decade Constructed"] = (df["Year Constructed"] // 10) * 10
    df["Agency Name"] = df["Agency Name"].str.strip()
    df["Usage Description"] = df["Usage Description"].str.strip()
    return df


df = load_data()

st.title("Who Builds Illinois? A Look at the State Building Inventory")
st.markdown(
    "This report explores the **Illinois State Building Inventory**: "
    f"{len(df):,} state-owned buildings with a known construction year. "
    "Each building lists its owning agency, its use, the year it was built "
    "and its square footage."
)

# ------------------------------------------------------------------ Plot 1
st.header("1. Floor space by agency, and when it was built")

status_options = sorted(df["Bldg Status"].dropna().unique())
status = st.multiselect("Building status to include", status_options,
                        default=status_options)
d1 = df[df["Bldg Status"].isin(status)]

top_agencies = (d1.groupby("Agency Name")["Square Footage"].sum()
                  .nlargest(10).index)
d1 = d1[d1["Agency Name"].isin(top_agencies)]

agency_sel = alt.selection_point(fields=["Agency Name"], empty=True)

bars = (
    alt.Chart(d1)
    .mark_bar()
    .encode(
        y=alt.Y("Agency Name:N", sort="-x", title=None),
        x=alt.X("sum(Square Footage):Q", title="Total floor space (sq ft)",
                axis=alt.Axis(format="~s")),
        color=alt.condition(agency_sel, alt.value("#1f5a96"),
                            alt.value("#d3d3d3")),
        tooltip=[alt.Tooltip("Agency Name:N", title="Agency"),
                 alt.Tooltip("sum(Square Footage):Q", title="Sq ft",
                             format=","),
                 alt.Tooltip("count():Q", title="Buildings")],
    )
    .add_params(agency_sel)
    .properties(height=320, title="Top 10 agencies by floor space (click a bar)")
)

timeline = (
    alt.Chart(d1)
    .mark_bar(color="#1f5a96")
    .encode(
        x=alt.X("Decade Constructed:O", title="Decade constructed"),
        y=alt.Y("sum(Square Footage):Q", title="Floor space built (sq ft)",
                axis=alt.Axis(format="~s")),
        tooltip=[alt.Tooltip("Decade Constructed:O", title="Decade"),
                 alt.Tooltip("sum(Square Footage):Q", title="Sq ft",
                             format=","),
                 alt.Tooltip("count():Q", title="Buildings")],
    )
    .transform_filter(agency_sel)
    .properties(height=260,
                title="Floor space built per decade (selected agency)")
)

st.altair_chart(alt.vconcat(bars, timeline).configure_axis(
    labelFontSize=12, titleFontSize=13).configure_title(fontSize=15),
    use_container_width=True)

st.markdown("""
**Write-up.** This plot shows which state agencies own the most floor space
and when that space was built. Clicking a bar in the top chart filters the
bottom chart to that agency (shift-click selects more than one, and clicking
empty space resets it). The status filter above the chart also lets the reader
include or exclude buildings by status. Together they show, for example, that
the University of Illinois and the Department of Corrections own the most
space, and that the 1960s were the biggest decade of construction overall. I used horizontal
bars sorted by size because agency names are long and easier to read along the
y-axis, and ordering makes ranks easy to compare. Square footage is on a
linear scale starting at zero so bar lengths are honest, with SI-style labels
(e.g. "20M") to keep the axis readable. Decades are used instead of single
years to smooth out noisy year-to-year counts. I used one blue for selected
data and light grey for unselected bars, since agency is already labelled on
the axis and a rainbow of colors would add no information. With more time I
would show floor space per building as well as the total, add a percent-of-
total view, and let readers pick any agency instead of only the top 10.
""")

# ------------------------------------------------------------------ Plot 2
st.header("2. What kinds of buildings were built in each era")

d2 = df[df["Decade Constructed"] >= 1850]
top_uses = d2["Usage Description"].value_counts().nlargest(10).index
d2 = d2[d2["Usage Description"].isin(top_uses)]

heat = (
    alt.Chart(d2)
    .mark_rect()
    .encode(
        x=alt.X("Decade Constructed:O", title="Decade constructed"),
        y=alt.Y("Usage Description:N", title="Primary use",
                sort=alt.EncodingSortField(op="count", order="descending")),
        color=alt.Color("count():Q", title="Buildings",
                        scale=alt.Scale(scheme="blues", type="log")),
        tooltip=[alt.Tooltip("Usage Description:N", title="Use"),
                 alt.Tooltip("Decade Constructed:O", title="Decade"),
                 alt.Tooltip("count():Q", title="Buildings")],
    )
    .properties(height=360,
                title="Number of buildings by primary use and decade built")
    .configure_axis(labelFontSize=12, titleFontSize=13)
    .configure_title(fontSize=15)
)
st.altair_chart(heat, use_container_width=True)

st.markdown("""
**Write-up.** This heatmap shows how the *mix* of state buildings has changed
over time by counting buildings for each combination of primary use and decade
built. It highlights that storage and "unusual" structures (sheds, shelters,
park facilities) dominate the inventory in every era, and that detention and
correctional buildings peak in the 1980s and 1990s. A heatmap suits two
categorical variables with many combinations better than grouped bars would.
I used rectangle marks and a single-hue sequential blue scheme because count
is an ordered quantity, so darker means more. The color scale is logarithmic
because a few cells hold hundreds of buildings while most hold only a few; on a
linear scale everything except the largest cells would look almost white.
Use categories are sorted by total count and limited to the ten most common so
the chart stays readable. With more time I would add a toggle between building
count and square footage, link this chart to the agency selection in Plot 1,
and annotate notable eras such as the post-war university expansion.
""")

# ------------------------------------------------------------------ HW5 note
st.header("Overlap with Homework #5")
st.markdown(
    "There is **no overlap** with Homework #5. Neither the dataset, the "
    "plots nor any write-up text in this app was used in Homework #5; "
    "everything here was made new for this assignment."
)
