# app.py
# Run with:
# pip install streamlit pandas matplotlib numpy
# streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Crypto PnL Simulator",
    layout="wide"
)

st.markdown("""
<style>

/* Hide hamburger menu */
#MainMenu {
    visibility: hidden;
}
            
/* Hide header */
header {
    visibility: hidden;
}
            
/* Hide footer */
footer {
    visibility: hidden;
}

/* Remove top padding */
.block-container {
    padding-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

st.title("Trading PnL Simulator")

st.markdown("""
    This app simulate profit & loss for trades across multiple leverage levels. It helps you to answer trading questions such as “If price moves here, what happens to my PnL"
    """)

# =========================
# CONSTANTS
# =========================

DEFAULT_LEVERAGES = [1, 2, 5, 10, 20, 50, 100]

# =========================
# HELPER FUNCTIONS
# =========================

def calculate_liquidation_price(
    entry_price,
    leverage,
    position_type
):
    """
    Simplified liquidation price calculation
    for isolated margin trading.
    """

    if leverage <= 0:
        return None

    if position_type == "Long":

        liquidation_price = (
            entry_price *
            (1 - (1 / leverage))
        )

    else:

        liquidation_price = (
            entry_price *
            (1 + (1 / leverage))
        )

    return max(liquidation_price, 0)

def calculate_pnl(position, leverage, pct_change, margin):
    """
    Calculate PnL based on:
    pnl = margin * leverage * percentage_move
    """

    move = pct_change / 100

    if position == "Long":
        return margin * leverage * move
    else:
        return margin * leverage * (-move)

def generate_price_data(
    entry_price,
    range_mode,
    price_move_pct=None,
    min_price=None,
    max_price=None,
    steps=None
):
    """
    Generate prices and percentage changes.
    """

    if range_mode == "Percentage Movement":

        price_changes = np.arange(
            -price_move_pct,
            price_move_pct + 1,
            1
        )

        prices = entry_price * (1 + price_changes / 100)

    else:

        prices = np.linspace(min_price, max_price, steps)

        price_changes = (
            (prices - entry_price) / entry_price
        ) * 100

    return prices, price_changes

def build_results_dataframe(
    prices,
    price_changes,
    leverages,
    position_type,
    margin
):
    """
    Build results dataframe with leverage columns.
    """

    results = pd.DataFrame({
        "Price ($)": np.round(prices, 2),
        "Price Change %": np.round(price_changes, 2)
    })

    for lev in leverages:

        pnl_values = [
            calculate_pnl(
                position_type,
                lev,
                pct,
                margin
            )
            for pct in price_changes
        ]

        # FIXED COLUMN NAME
        results[f"{lev}x PnL ($)"] = np.round(
            pnl_values,
            2
        )

    return results

def plot_pnl_chart(
    results,
    leverages,
    position_type,
    entry_price
):
    """
    Plot leverage PnL chart
    with liquidation lines.
    """

    fig, ax = plt.subplots(figsize=(12, 6))

    x_min = results["Price ($)"].min()
    x_max = results["Price ($)"].max()

    for lev in leverages:

        # Main PnL line
        line, = ax.plot(
            results["Price ($)"],
            results[f"{lev}x PnL ($)"],
            label=f"{lev}x",
            linewidth=2
        )

        # Get matching line color
        line_color = line.get_color()

        # Calculate liquidation price
        liq_price = calculate_liquidation_price(
            entry_price=entry_price,
            leverage=lev,
            position_type=position_type
        )

        # Draw liquidation line
        ax.axvline(
            x=liq_price,
            color=line_color,
            linestyle="--",
            linewidth=1.5,
            alpha=0.8
        )

        # Label
        ax.text(
            liq_price,
            ax.get_ylim()[1] * 0.95,
            f"{lev}x Liq",
            rotation=90,
            color=line_color,
            fontsize=8,
            verticalalignment="top",
            horizontalalignment="right"
        )

    # Extend lines fully to chart edges
    ax.set_xlim(x_min, x_max)
    ax.margins(x=0)

    # Zero reference line
    ax.axhline(
        0,
        linestyle=":",
        linewidth=1,
        color="gray"
    )

    ax.set_xlabel("Asset Price ($)")
    ax.set_ylabel("PnL ($)")

    ax.set_title(
        f"{position_type} Position PnL Across Leverages"
    )

    ax.legend()

    ax.grid(alpha=0.2)

    return fig

def build_example_summary(
    leverages,
    pnl_pct,
    position_type,
    margin
):
    """
    Build example scenario table.
    """

    summary_data = []

    for lev in leverages:

        pnl = calculate_pnl(
            position_type,
            lev,
            pnl_pct,
            margin
        )

        summary_data.append({
            "Leverage": f"{lev}x",
            f"If Price Moves {pnl_pct}%":
                f"${pnl:,.2f}"
        })

    return pd.DataFrame(summary_data)


# # =========================
# # SIDEBAR
# # =========================

# st.sidebar.header("Trade Settings")

# position_type = st.sidebar.selectbox(
#     "Position Type",
#     ["Long", "Short"]
# )

# entry_price = st.sidebar.number_input(
#     "Entry Price ($)",
#     min_value=0.0001,
#     value=300.0,
#     step=10.0
# )

# margin = st.sidebar.number_input(
#     "Margin ($)",
#     min_value=1.0,
#     value=100.0,
#     step=10.0
# )

# # NEW: MULTISELECT LEVERAGES
# leverages = st.sidebar.multiselect(
#     "Select Leverages",
#     DEFAULT_LEVERAGES,
#     default=DEFAULT_LEVERAGES
# )

# # Prevent empty selection 
# if not leverages: 
#     st.warning("Please select at least one leverage.") 
#     st.stop()

# range_mode = st.sidebar.radio(
#     "Price Range Input",
#     ["Percentage Movement", "Target Prices"]
# )

# # =========================
# # PRICE RANGE INPUTS
# # =========================

# if range_mode == "Percentage Movement":

#     price_move_pct = st.sidebar.slider(
#         "Price Movement Range (%)",
#         min_value=1,
#         max_value=100,
#         value=80
#     )

#     prices, price_changes = generate_price_data(
#         entry_price=entry_price,
#         range_mode=range_mode,
#         price_move_pct=price_move_pct
#     )

# else:

#     min_price = st.sidebar.number_input(
#         "Minimum Price ($)",
#         min_value=0.01,
#         value=entry_price * 0.7
#     )

#     max_price = st.sidebar.number_input(
#         "Maximum Price ($)",
#         min_value=0.01,
#         value=entry_price * 1.3
#     )

#     steps = st.sidebar.slider(
#         "Number of Price Steps",
#         min_value=10,
#         max_value=200,
#         value=50,
#         help="""
#             Controls how many simulated price points are generated 
#             between the minimum and maximum price.

#             Higher values create:
#             • smoother charts
#             • more detailed tables
#             • more calculations

#             Lower values create:
#             • faster performance
#             • simpler visualization
#             """
#     )

#     prices, price_changes = generate_price_data(
#         entry_price=entry_price,
#         range_mode=range_mode,
#         min_price=min_price,
#         max_price=max_price,
#         steps=steps
#         )


# =========================
# Instead of SIDEBAR (compatible for smartphone)
# =========================

st.header("Trade Settings")

position_type = st.selectbox(
    "Position Type",
    ["Long", "Short"]
)

entry_price = st.number_input(
    "Entry Price ($)",
    min_value=0.0001,
    value=300.0,
    step=10.0
)

margin = st.number_input(
    "Margin ($)",
    min_value=1.0,
    value=100.0,
    step=10.0
)

# NEW: MULTISELECT LEVERAGES
leverages = st.multiselect(
    "Select Leverages",
    DEFAULT_LEVERAGES,
    default=DEFAULT_LEVERAGES
)

# Prevent empty selection 
if not leverages: 
    st.warning("Please select at least one leverage.") 
    st.stop()

range_mode = st.radio(
    "Price Range Input",
    ["Percentage Movement", "Target Prices"]
)

# =========================
# PRICE RANGE INPUTS
# =========================

if range_mode == "Percentage Movement":

    price_move_pct = st.slider(
        "Price Movement Range (%)",
        min_value=1,
        max_value=100,
        value=80
    )

    prices, price_changes = generate_price_data(
        entry_price=entry_price,
        range_mode=range_mode,
        price_move_pct=price_move_pct
    )

else:

    min_price = st.number_input(
        "Minimum Price ($)",
        min_value=0.01,
        value=entry_price * 0.7
    )

    max_price = st.number_input(
        "Maximum Price ($)",
        min_value=0.01,
        value=entry_price * 1.3
    )

    steps = st.slider(
        "Number of Price Steps",
        min_value=10,
        max_value=200,
        value=50,
        help="""
            Controls how many simulated price points are generated 
            between the minimum and maximum price.

            Higher values create:
            • smoother charts
            • more detailed tables
            • more calculations

            Lower values create:
            • faster performance
            • simpler visualization
            """
    )

    prices, price_changes = generate_price_data(
        entry_price=entry_price,
        range_mode=range_mode,
        min_price=min_price,
        max_price=max_price,
        steps=steps
        )

# =========================
# BUILD RESULTS
# =========================

results = build_results_dataframe(
    prices=prices,
    price_changes=price_changes,
    leverages=leverages,
    position_type=position_type,
    margin=margin
)

# =========================
# OVERVIEW METRICS
# =========================

st.subheader("Trade Overview")

cols = st.columns(len(leverages))

for i, lev in enumerate(leverages):

    position_size = margin * lev

    cols[i].metric(
        label=f"{lev}x Position Size",
        value=f"${position_size:,.2f}"
    )

# =========================
# LIQUIDATION PRICES
# =========================

st.markdown('<div class="liq-section">', unsafe_allow_html=True)

st.subheader("Estimated Liquidation Prices")

liq_cols = st.columns(len(leverages))

for i, lev in enumerate(leverages):

    liq_price = calculate_liquidation_price(
        entry_price,
        lev,
        position_type
    )

    liq_cols[i].metric(
        label=f"🚨 {lev}x Liquidation",
        value=f"${liq_price:,.2f}"
    )


# =========================
# RESULTS TABLE
# =========================

st.subheader("PnL Table")

styled_df = results.style.format({
    col: "${:,.2f}"
    for col in results.columns
    if "PnL" in col
})

st.dataframe(
    styled_df,
    width='stretch'
)

# =========================
# CHART
# =========================

st.subheader("PnL Chart")

# fig = plot_pnl_chart(
#     results,
#     leverages,
#     position_type
# )

fig = plot_pnl_chart(
    results=results,
    leverages=leverages,
    position_type=position_type,
    entry_price=entry_price
    )

st.pyplot(fig)

# =========================
# EXAMPLE SCENARIO
# =========================

st.subheader("Example Scenario")

# NEW: USER PNL SLIDER
example_pnl_pct = st.slider(
    "Example PnL Move (%)",
    min_value=-100,
    max_value=100,
    value=10,
    step=1
)

summary_df = build_example_summary(
    leverages=leverages,
    pnl_pct=example_pnl_pct,
    position_type=position_type,
    margin=margin
)

st.table(summary_df)

# =========================
# FOOTER
# =========================

st.info("""
Notes:
- This simulator assumes linear PnL.
- Funding fees, trading fees, slippage, and liquidation fees are not included.
- This app is not meant for a finance advice. Use it for educational purposes only.
""")