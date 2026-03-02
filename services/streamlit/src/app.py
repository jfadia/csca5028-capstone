import streamlit as st
import altair as alt
import requests
from utils.db import pull_data
import os


def _refresh_data():
    response = requests.get(
        os.environ["DATA_COLLECTOR_ENDPOINT"],
        params={
            "start_date": st.session_state.get("date_selector")[0],
            "end_date": st.session_state.get("date_selector")[1],
        },
    )
    if response.status_code == 200:
        response = requests.get(os.environ["DATA_ANALYZER_ENDPOINT"])
        if response.status_code != 200:
            st.error("Failed to analyze data. Please try again later.")
    else:
        st.error("Failed to refresh data. Please try again later.")


def main():
    analysis, gains = pull_data()
    st.title("Bitcoin Price Analysis")
    st.write(f"This app visualizes Bitcoin price data along with buy/sell signals.")

    st.date_input(
        "Use the selector below to adjust the date range:",
        value=(analysis["date"].min(), analysis["date"].max()),
        format="YYYY-MM-DD",
        key="date_selector",
    )
    st.button("Refresh Data", on_click=_refresh_data)

    realized_gain = gains["realized_gain"].iloc[0]
    unrealized_gain = gains["unrealized_gain"].iloc[0]
    with st.container(border=True):
        st.subheader("Gains Summary")
        st.write(f"Realized Gain: \\${realized_gain:,.2f}")
        st.write(f"Unrealized Gain: \\${unrealized_gain:,.2f}")

    layer = (
        alt.Chart(analysis)
        .mark_line(color="white")
        .encode(
            x="date:T",
            y="price:Q",
            tooltip=["date:T", "price:Q", "signal:N"],
        )
        + alt.Chart(analysis[analysis["signal"] == "BUY"])
        .mark_circle(size=500, opacity=0.7, color="green")
        .encode(x="date:T", y="price:Q", tooltip=["date:T", "price:Q", "signal:N"])
        + alt.Chart(analysis[analysis["signal"] == "SELL"])
        .mark_circle(size=500, opacity=0.7, color="red")
        .encode(x="date:T", y="price:Q", tooltip=["date:T", "price:Q", "signal:N"])
    )

    st.altair_chart(layer, width="stretch")

    st.dataframe(analysis[analysis["signal"] != "HOLD"], hide_index=True)


if __name__ == "__main__":
    main()
