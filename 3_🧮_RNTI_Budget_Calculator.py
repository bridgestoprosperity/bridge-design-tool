from pathlib import Path
import re

import pandas as pd
import streamlit as st
from openpyxl import load_workbook

st.set_page_config(page_title="RNTI Budget Calculator", page_icon="🧮", layout="wide")
st.logo("./assets/fikalogo.png")
st.sidebar.header("RNTI Budget Calculator")

WORKBOOK_PATH = Path("./Networked Transport Infrastructure Budget Allocation Tool V2.xlsx")

FALLBACK_SOURCE_ROW_GROUPS = {
    25: [7, 8, 9, 10],
    26: [16, 17, 18, 19, 20, 21],
    27: [26, 27],
    28: [32, 33, 34, 35, 36],
    29: [41, 42],
    30: [47, 48],
    33: [54],
    34: [60, 61],
    35: [66, 67],
    36: [72],
    37: [77, 78],
    38: [83],
    39: [88],
    40: [93],
    42: [99, 100, 101, 102],
    43: [107, 108, 109],
    44: [114, 115],
    45: [120],
    46: [125],
    47: [130, 131],
    48: [136, 137],
    49: [148],
    50: [142, 143],
}


def parse_average_source_rows(formula: str | None, col_letter: str) -> list[int]:
    if not isinstance(formula, str) or "AVERAGE(" not in formula.upper():
        return []

    match = re.search(r"AVERAGE\((.*?)\)", formula, flags=re.IGNORECASE)
    if not match:
        return []

    inside = match.group(1).replace("$", "")
    refs = [part.strip() for part in inside.split(",") if part.strip()]
    rows: list[int] = []

    for ref in refs:
        if ":" in ref:
            start_ref, end_ref = ref.split(":", 1)
            start_match = re.search(rf"{col_letter}(\d+)", start_ref, flags=re.IGNORECASE)
            end_match = re.search(rf"{col_letter}(\d+)", end_ref, flags=re.IGNORECASE)
            if start_match and end_match:
                start_row = int(start_match.group(1))
                end_row = int(end_match.group(1))
                low, high = sorted((start_row, end_row))
                rows.extend(range(low, high + 1))
        else:
            single_match = re.search(rf"{col_letter}(\d+)", ref, flags=re.IGNORECASE)
            if single_match:
                rows.append(int(single_match.group(1)))

    return sorted(set(rows))


def derive_source_row_groups(ws, ws_source) -> dict[int, list[int]]:
    row_groups: dict[int, list[int]] = {}

    for row in range(24, 51):
        item_number = ws[f"A{row}"].value
        if item_number is None:
            continue

        min_formula = ws[f"D{row}"].value
        source_rows: list[int] = []

        if isinstance(min_formula, str):
            blended_match = re.search(r"!\$?C(\d+)", min_formula)
            if blended_match:
                blended_row = int(blended_match.group(1))
                source_rows = parse_average_source_rows(ws_source[f"C{blended_row}"].value, "C")
                if not source_rows:
                    source_rows = parse_average_source_rows(ws_source[f"D{blended_row}"].value, "D")

        if not source_rows:
            source_rows = FALLBACK_SOURCE_ROW_GROUPS.get(row, [])

        if source_rows:
            row_groups[row] = source_rows

    return row_groups


def derive_budget_to_source_blended_row(ws) -> dict[int, int]:
    links: dict[int, int] = {}
    for row in range(24, 51):
        item_number = ws[f"A{row}"].value
        if item_number is None:
            continue
        min_formula = ws[f"D{row}"].value
        if not isinstance(min_formula, str):
            continue
        blended_match = re.search(r"!\$?C(\d+)", min_formula)
        if blended_match:
            links[row] = int(blended_match.group(1))
    return links


def source_group_display_order(source_row_groups: dict[int, list[int]]) -> list[int]:
    return sorted(
        source_row_groups.keys(),
        key=lambda budget_row: min(source_row_groups.get(budget_row, [10**9])),
    )


@st.cache_data
def load_budget_calculator_data(file_path: str, workbook_mtime: float):
    wb = load_workbook(file_path, data_only=True)
    wb_formula = load_workbook(file_path, data_only=False)
    ws = wb["Budget Calculator"]
    ws_source = wb["Source Data - In Progress"]
    ws_source_formula = wb_formula["Source Data - In Progress"]
    source_row_groups = derive_source_row_groups(ws, ws_source)
    budget_to_source_blended_row = derive_budget_to_source_blended_row(ws)

    def source_url_from_row(source_row: int):
        cell = ws_source_formula[f"F{source_row}"]
        if cell.hyperlink is None:
            return None
        if cell.hyperlink.target:
            return str(cell.hyperlink.target)
        if cell.hyperlink.location:
            return f"#{cell.hyperlink.location}"
        return None

    def blended_costs_from_source_rows(source_rows: list[int]):
        low_values = [ws_source[f"C{r}"].value for r in source_rows]
        high_values = [ws_source[f"D{r}"].value for r in source_rows]

        min_cost = calculate_blended_average(pd.Series(low_values))
        max_cost = calculate_blended_average(pd.Series(high_values))
        mid_cost = calculate_source_mid(min_cost, max_cost)
        return min_cost, max_cost, mid_cost

    intro_title = ws["A1"].value or ""
    intro_text = ws["A2"].value or ""
    disclaimer = ws["A4"].value or ""

    defaults = {
        "project_name": ws["C9"].value or "",
        "country_region": ws["C10"].value or "",
        "total_budget_usd": float(ws["C12"].value or 0),
        "allocation_pct": float(ws["C13"].value or 0),
        "maintenance_pct": float(ws["C16"].value or 0),
    }

    section_name = ""
    items = []
    for row in range(24, 51):
        item_number = ws[f"A{row}"].value
        infra_name = ws[f"B{row}"].value

        if item_number is None and infra_name:
            section_name = str(infra_name)
            continue

        if item_number is None and not infra_name:
            continue

        source_rows = source_row_groups.get(row, [])
        min_cost, max_cost, mid_cost = blended_costs_from_source_rows(source_rows)

        items.append(
            {
                "Budget Row": row,
                "#": int(item_number),
                "Section": section_name,
                "Infrastructure Type": str(infra_name),
                "Unit": ws[f"C{row}"].value,
                "Min Unit Cost (USD)": min_cost,
                "Max Unit Cost (USD)": max_cost,
                "Mid Unit Cost (USD)": mid_cost,
                "Qty": float(ws[f"G{row}"].value or 0),
            }
        )

    components_df = pd.DataFrame(items)

    def section_title_for_source_row(row_num: int) -> str:
        if row_num < 51:
            return "ORDER 3 TERTIARY LINKS"
        if row_num < 96:
            return "SUB-TERTIARY LINKS"
        return "ANCILLARY & SAFETY INFRASTRUCTURE"

    source_records = []
    for budget_row, source_rows in source_row_groups.items():
        infrastructure_type = ws[f"B{budget_row}"].value
        first_source_row = min(source_rows) if source_rows else None
        item_title = ws_source[f"A{first_source_row - 2}"].value if first_source_row else None
        section_title = section_title_for_source_row(first_source_row) if first_source_row else ""
        for source_row in source_rows:
            source_url = source_url_from_row(source_row)
            source_records.append(
                {
                    "Budget Row": budget_row,
                    "Source Section": section_title,
                    "Source Item Title": item_title,
                    "Infrastructure Type": infrastructure_type,
                    "Source Row": source_row,
                    "Source #": ws_source[f"A{source_row}"].value,
                    "Geography / Context": ws_source[f"B{source_row}"].value,
                    "Low Est. (USD)": ws_source[f"C{source_row}"].value,
                    "High Est. (USD)": ws_source[f"D{source_row}"].value,
                    "Source Mid (USD)": ws_source[f"E{source_row}"].value,
                    "Source Name": source_url or ws_source[f"F{source_row}"].value,
                    "Full Citation": ws_source[f"G{source_row}"].value,
                    "Year": ws_source[f"H{source_row}"].value,
                }
            )

    source_df = pd.DataFrame(source_records)
    return (
        intro_title,
        intro_text,
        disclaimer,
        defaults,
        components_df,
        source_df,
        source_row_groups,
        budget_to_source_blended_row,
    )


def calc_range_text(min_unit_cost: float | None, max_unit_cost: float | None, qty: float):
    if qty == 0:
        return "-"
    if pd.isna(min_unit_cost) or pd.isna(max_unit_cost):
        return "No verifiable source yet"
    return f"${min_unit_cost * qty:,.0f} - ${max_unit_cost * qty:,.0f}"


def to_numeric_series(values: pd.Series) -> pd.Series:
    return pd.to_numeric(
        values.astype(str).str.replace(r"[\$,]", "", regex=True).str.strip(),
        errors="coerce",
    )


def build_average_formula(col_letter: str, rows: list[int]) -> str:
    def build_range_ref() -> str:
        if len(rows) == 1:
            return f"{col_letter}{rows[0]}"
        if rows == list(range(min(rows), max(rows) + 1)):
            return f"{col_letter}{min(rows)}:{col_letter}{max(rows)}"
        return ",".join([f"{col_letter}{r}" for r in rows])

    if not rows:
        return ""
    range_ref = build_range_ref()
    return f'=IFERROR(ROUND(AVERAGE({range_ref}),0),"")'


def build_mid_formula(rows: list[int]) -> str:
    if not rows:
        return ""
    c_formula = build_average_formula("C", rows).lstrip("=")
    d_formula = build_average_formula("D", rows).lstrip("=")
    return f'=IFERROR(ROUND((({c_formula})+({d_formula}))/2,0),"")'


def build_blended_summary_table(source_data: pd.DataFrame, source_row_groups: dict[int, list[int]]) -> pd.DataFrame:
    records = []
    for budget_row, source_rows in source_row_groups.items():
        subset = source_data[source_data["Budget Row"] == budget_row].copy()
        infra_name = (
            subset["Infrastructure Type"].iloc[0]
            if not subset.empty
            else None
        )

        lows = subset["Low Est. (USD)"] if not subset.empty else pd.Series(dtype=float)
        highs = subset["High Est. (USD)"] if not subset.empty else pd.Series(dtype=float)

        blended_min = calculate_blended_average(lows)
        blended_max = calculate_blended_average(highs)
        blended_mid = calculate_source_mid(blended_min, blended_max)

        records.append(
            {
                "Budget Row": budget_row,
                "Infrastructure Type": infra_name,
                "Blended Min (USD)": blended_min,
                "Blended Max (USD)": blended_max,
                "Blended Mid (USD)": blended_mid,
                "Blended Min Formula": build_average_formula("C", source_rows),
                "Blended Max Formula": build_average_formula("D", source_rows),
                "Blended Mid Formula": build_mid_formula(source_rows),
            }
        )
    return pd.DataFrame(records)


def calculate_source_mid(low_value, high_value):
    low_num = to_numeric_series(pd.Series([low_value])).iloc[0]
    high_num = to_numeric_series(pd.Series([high_value])).iloc[0]
    if pd.isna(low_num) or pd.isna(high_num):
        return pd.NA
    return float(round((low_num + high_num) / 2, 0))


def calculate_blended_average(values: pd.Series):
    numeric_values = to_numeric_series(values).dropna()
    if numeric_values.empty:
        return pd.NA
    return float(round(numeric_values.mean(), 0))


if not WORKBOOK_PATH.exists():
    st.error("Workbook file not found in the project root.")
    st.stop()

(
    intro_title,
    intro_text,
    disclaimer,
    defaults,
    components_df,
    source_df,
    source_row_groups,
    budget_to_source_blended_row,
) = load_budget_calculator_data(str(WORKBOOK_PATH), WORKBOOK_PATH.stat().st_mtime)

st.title("Networked Transport Infrastructure Budget Allocation Tool")
st.caption(intro_title)
st.write(intro_text)
st.info(disclaimer)

st.markdown("## Section 1: Transport Project Inputs")
left, right = st.columns([1, 1])

with left:
    st.text_input("Project Name / Description", value="")
    st.text_input("Country / Region", value="")
    total_budget_usd = st.number_input(
        "Total Transport Project Budget (USD)",
        min_value=0.0,
        value=defaults["total_budget_usd"],
        step=1000000.0,
    )

with right:
    allocation_pct = st.number_input(
        "% Allocated to RNTI / Rural Access",
        min_value=0.0,
        max_value=1.0,
        value=defaults["allocation_pct"],
        step=0.01,
        format="%.2f",
        help="Use decimal form (e.g., 0.07 for 7%).",
    )
    maintenance_pct = st.number_input(
        "Maintenance Reserve (%)",
        min_value=0.0,
        max_value=1.0,
        value=defaults["maintenance_pct"],
        step=0.01,
        format="%.2f",
        help="Recommended range in workbook: 5% to 15%.",
    )

rnti_budget = total_budget_usd * allocation_pct
maintenance_amount = rnti_budget * maintenance_pct
capital_budget = rnti_budget - maintenance_amount

k1, k2, k3 = st.columns(3)
k1.metric("RNTI Budget Available", f"${rnti_budget:,.0f}")
k2.metric("Maintenance Reserve Amount", f"${maintenance_amount:,.0f}")
k3.metric("Capital Budget for Infrastructure", f"${capital_budget:,.0f}")

if "rnti_source_data_df" not in st.session_state:
    st.session_state["rnti_source_data_df"] = source_df.copy()
if "rnti_blended_overrides" not in st.session_state:
    st.session_state["rnti_blended_overrides"] = {}
active_source_df = st.session_state["rnti_source_data_df"].copy()

blended_summary_df = build_blended_summary_table(active_source_df, source_row_groups)

blended_summary_df["Blended Min (USD)"] = to_numeric_series(blended_summary_df["Blended Min (USD)"])
blended_summary_df["Blended Max (USD)"] = to_numeric_series(blended_summary_df["Blended Max (USD)"])
blended_summary_df["Blended Mid (USD)"] = blended_summary_df.apply(
    lambda row: calculate_source_mid(row["Blended Min (USD)"], row["Blended Max (USD)"]),
    axis=1,
)

for budget_row, override_values in st.session_state["rnti_blended_overrides"].items():
    idx = blended_summary_df[blended_summary_df["Budget Row"] == int(budget_row)].index
    if idx.empty:
        continue
    override_low = to_numeric_series(pd.Series([override_values.get("Low Est. (USD)")])).iloc[0]
    override_high = to_numeric_series(pd.Series([override_values.get("High Est. (USD)")])).iloc[0]
    if not pd.isna(override_low):
        blended_summary_df.at[idx[0], "Blended Min (USD)"] = float(override_low)
    if not pd.isna(override_high):
        blended_summary_df.at[idx[0], "Blended Max (USD)"] = float(override_high)

blended_summary_df["Blended Mid (USD)"] = blended_summary_df.apply(
    lambda row: calculate_source_mid(row["Blended Min (USD)"], row["Blended Max (USD)"]),
    axis=1,
)

# Workbook formula-link emulation test (row 25 only):
# Budget Calculator D25/E25/F25 should mirror Source blended C12/D12/E12 logic.
if 25 in budget_to_source_blended_row:
    row_25_subset = active_source_df[active_source_df["Budget Row"] == 25]
    row_25_low = calculate_blended_average(row_25_subset["Low Est. (USD)"])
    row_25_high = calculate_blended_average(row_25_subset["High Est. (USD)"])
    row_25_mid = calculate_source_mid(row_25_low, row_25_high)
    row_25_idx = blended_summary_df[blended_summary_df["Budget Row"] == 25].index
    if not row_25_idx.empty:
        blended_summary_df.at[row_25_idx[0], "Blended Min (USD)"] = row_25_low
        blended_summary_df.at[row_25_idx[0], "Blended Max (USD)"] = row_25_high
        blended_summary_df.at[row_25_idx[0], "Blended Mid (USD)"] = row_25_mid

blended_override = {}
for _, row in blended_summary_df.iterrows():
    budget_row = int(row["Budget Row"])
    blended_override[budget_row] = (
        row["Blended Min (USD)"],
        row["Blended Max (USD)"],
        row["Blended Mid (USD)"],
    )

components_df = components_df.copy()
for idx in components_df.index:
    budget_row = int(components_df.at[idx, "Budget Row"])
    if budget_row in blended_override:
        min_cost, max_cost, mid_cost = blended_override[budget_row]
        components_df.at[idx, "Min Unit Cost (USD)"] = min_cost
        components_df.at[idx, "Max Unit Cost (USD)"] = max_cost
        components_df.at[idx, "Mid Unit Cost (USD)"] = mid_cost

st.markdown("## Section 2: Infrastructure Mix")
if 25 in budget_to_source_blended_row:
    linked_row = budget_to_source_blended_row[25]
    st.caption(
        f"Formula-link test active: Budget row 25 mirrors Source blended row {linked_row} "
        "(equivalent to D25<-C12, E25<-D12, F25<-E12 style chaining)."
    )

working_df = components_df.copy()

editor_state = st.session_state.get("rnti_infra_editor", {})
edited_rows = editor_state.get("edited_rows", {}) if isinstance(editor_state, dict) else {}
for row_idx, changes in edited_rows.items():
    if not isinstance(changes, dict) or "Qty" not in changes:
        continue
    idx = int(row_idx)
    if 0 <= idx < len(working_df):
        working_df.at[idx, "Qty"] = changes["Qty"]

working_df["Min Unit Cost (USD)"] = to_numeric_series(working_df["Min Unit Cost (USD)"])
working_df["Max Unit Cost (USD)"] = to_numeric_series(working_df["Max Unit Cost (USD)"])
working_df["Mid Unit Cost (USD)"] = to_numeric_series(working_df["Mid Unit Cost (USD)"])
working_df["Qty"] = to_numeric_series(working_df["Qty"]).fillna(0)
working_df["Total Cost Estimate (Mid)"] = working_df["Mid Unit Cost (USD)"] * working_df["Qty"]
working_df["Total Cost Estimate Range"] = working_df.apply(
    lambda row: calc_range_text(
        row["Min Unit Cost (USD)"],
        row["Max Unit Cost (USD)"],
        row["Qty"],
    ),
    axis=1,
)


editor_rows = []
for section in [s for s in working_df["Section"].dropna().unique()]:
    editor_rows.append(
        {
            "#": None,
            "Section": section,
            "Infrastructure Type": section,
            "Unit": None,
            "Mid Unit Cost (USD)": None,
            "Qty": None,
            "Min Unit Cost (USD)": None,
            "Max Unit Cost (USD)": None,
            "Total Cost Estimate (Mid)": None,
            "Total Cost Estimate Range": None,
        }
    )
    for _, row in working_df[working_df["Section"] == section].iterrows():
        editor_rows.append(
            {
                "#": row["#"],
                "Section": row["Section"],
                "Infrastructure Type": row["Infrastructure Type"],
                "Unit": row["Unit"],
                "Mid Unit Cost (USD)": row["Mid Unit Cost (USD)"],
                "Qty": row["Qty"],
                "Min Unit Cost (USD)": row["Min Unit Cost (USD)"],
                "Max Unit Cost (USD)": row["Max Unit Cost (USD)"],
                "Total Cost Estimate (Mid)": row["Total Cost Estimate (Mid)"],
                "Total Cost Estimate Range": row["Total Cost Estimate Range"],
            }
        )

editor_df = pd.DataFrame(editor_rows)

editable_df = st.data_editor(
    editor_df,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    key="rnti_infra_editor",
    column_order=[
        "Section",
        "Infrastructure Type",
        "Unit",
        "Min Unit Cost (USD)",
        "Max Unit Cost (USD)",
        "Mid Unit Cost (USD)",
        "Qty",
        "Total Cost Estimate (Mid)",
        "Total Cost Estimate Range",
    ],
    column_config={
        "Section": st.column_config.TextColumn(disabled=True),
        "Infrastructure Type": st.column_config.TextColumn(disabled=True, width="medium"),
        "Unit": st.column_config.TextColumn(disabled=True),
        "Mid Unit Cost (USD)": st.column_config.NumberColumn(disabled=True, format="$%0.0f"),
        "Qty": st.column_config.NumberColumn(min_value=0.0, step=1.0, format="%.2f"),
        "Min Unit Cost (USD)": st.column_config.NumberColumn(disabled=True, format="$%0.0f"),
        "Max Unit Cost (USD)": st.column_config.NumberColumn(disabled=True, format="$%0.0f"),
        "Total Cost Estimate (Mid)": st.column_config.NumberColumn(disabled=True, format="$%0.0f"),
        "Total Cost Estimate Range": st.column_config.TextColumn(disabled=True),
    },
)

summary_df = editable_df.copy()
summary_df = summary_df[summary_df["Unit"].notna()].copy()
summary_df["Min Unit Cost (USD)"] = to_numeric_series(summary_df["Min Unit Cost (USD)"])
summary_df["Max Unit Cost (USD)"] = to_numeric_series(summary_df["Max Unit Cost (USD)"])
summary_df["Mid Unit Cost (USD)"] = to_numeric_series(summary_df["Mid Unit Cost (USD)"])
summary_df["Qty"] = to_numeric_series(summary_df["Qty"]).fillna(0)
summary_df["Total Cost Estimate (Mid)"] = summary_df["Mid Unit Cost (USD)"] * summary_df["Qty"]
summary_df["Total Cost Estimate Range"] = summary_df.apply(
    lambda row: calc_range_text(
        row["Min Unit Cost (USD)"],
        row["Max Unit Cost (USD)"],
        row["Qty"],
    ),
    axis=1,
)

st.markdown("### Cost Inputs Snapshot")
st.caption("Quick view so Min Unit Cost is always visible.")
st.dataframe(
    summary_df[
        [
            "Infrastructure Type",
            "Qty",
            "Min Unit Cost (USD)",
            "Max Unit Cost (USD)",
            "Mid Unit Cost (USD)",
            "Total Cost Estimate (Mid)",
        ]
    ],
    hide_index=True,
    use_container_width=True,
    column_config={
        "Min Unit Cost (USD)": st.column_config.NumberColumn(format="$%0.0f"),
        "Max Unit Cost (USD)": st.column_config.NumberColumn(format="$%0.0f"),
        "Mid Unit Cost (USD)": st.column_config.NumberColumn(format="$%0.0f"),
        "Total Cost Estimate (Mid)": st.column_config.NumberColumn(format="$%0.0f"),
    },
)

st.markdown("## Section 3: Budget Summary")
total_infrastructure_cost = summary_df["Total Cost Estimate (Mid)"].fillna(0).sum()
remaining_capital_budget = capital_budget - total_infrastructure_cost
pct_capital_used = 0 if capital_budget == 0 else total_infrastructure_cost / capital_budget
total_estimated_rnti_investment = total_infrastructure_cost + maintenance_amount
pct_of_total_project = 0 if total_budget_usd == 0 else total_estimated_rnti_investment / total_budget_usd

s1, s2, s3 = st.columns(3)
s1.metric("Total Infrastructure Cost (Mid-Point Estimate)", f"${total_infrastructure_cost:,.0f}")
s2.metric("Remaining Capital Budget", f"${remaining_capital_budget:,.0f}")
s3.metric("% of Capital Budget Used", f"{pct_capital_used:.1%}")

s4, s5 = st.columns(2)
s4.metric("Maintenance Reserve", f"${maintenance_amount:,.0f}")
s5.metric("% of Total Corridor Project", f"{pct_of_total_project:.1%}")

if remaining_capital_budget < 0:
    st.error(
        f"Your selected quantities exceed capital budget by ${abs(remaining_capital_budget):,.0f}."
    )
else:
    st.success("Selected quantities are within the current capital budget.")

st.markdown("## Quick Reference: Example Allocation Scenarios")
quick_ref = pd.DataFrame(
    {
        "% Allocation": ["1%", "2%", "5%", "10%"],
        "Budget = $100M": [1_000_000, 2_000_000, 5_000_000, 10_000_000],
        "Budget = $200M": [2_000_000, 4_000_000, 10_000_000, 20_000_000],
        "Budget = $400M": [4_000_000, 8_000_000, 20_000_000, 40_000_000],
        "Budget = $1B": [10_000_000, 20_000_000, 50_000_000, 100_000_000],
    }
)

st.dataframe(
    quick_ref,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Budget = $100M": st.column_config.NumberColumn(format="$%0.0f"),
        "Budget = $200M": st.column_config.NumberColumn(format="$%0.0f"),
        "Budget = $400M": st.column_config.NumberColumn(format="$%0.0f"),
        "Budget = $1B": st.column_config.NumberColumn(format="$%0.0f"),
    },
)

with st.expander("Section 4: Source Data and Formula Inputs", expanded=False):
    st.markdown("### RNTI COST SOURCE DATA — Verifiable Sources with Integrated Blended Averages")

    grouped_source_frames = []
    new_blended_overrides = {}
    last_section = None
    for budget_row in source_group_display_order(source_row_groups):
        group_df = st.session_state["rnti_source_data_df"][
            st.session_state["rnti_source_data_df"]["Budget Row"] == budget_row
        ].copy()
        if group_df.empty:
            continue

        source_section = group_df["Source Section"].iloc[0]
        source_item_title = group_df["Source Item Title"].iloc[0]

        if source_section != last_section:
            st.markdown(f"#### {source_section}")
            last_section = source_section

        st.markdown(f"**{source_item_title}**")
        group_df["Source Mid (USD)"] = group_df.apply(
            lambda row: calculate_source_mid(row["Low Est. (USD)"], row["High Est. (USD)"]),
            axis=1,
        )

        blended_min = calculate_blended_average(group_df["Low Est. (USD)"])
        blended_max = calculate_blended_average(group_df["High Est. (USD)"])
        blended_mid = calculate_source_mid(blended_min, blended_max)

        edited_group_df = st.data_editor(
            group_df[
                [
                    "Geography / Context",
                    "Low Est. (USD)",
                    "High Est. (USD)",
                    "Source Mid (USD)",
                    "Source Name",
                    "Full Citation",
                    "Year",
                    "Budget Row",
                    "Source Row",
                    "Infrastructure Type",
                    "Source Section",
                    "Source Item Title",
                ]
            ],
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key=f"rnti_source_data_editor_{budget_row}",
            column_config={
                "Geography / Context": st.column_config.TextColumn(disabled=True, width="large"),
                "Low Est. (USD)": st.column_config.NumberColumn(format="$%0.0f"),
                "High Est. (USD)": st.column_config.NumberColumn(format="$%0.0f"),
                "Source Mid (USD)": st.column_config.NumberColumn(disabled=True, format="$%0.0f"),
                "Source Name": st.column_config.LinkColumn(disabled=True, width="medium"),
                "Full Citation": st.column_config.TextColumn(disabled=True, width="large"),
                "Year": st.column_config.NumberColumn(disabled=True, format="%d"),
                "Budget Row": st.column_config.NumberColumn(disabled=True, format="%d"),
                "Source Row": st.column_config.NumberColumn(disabled=True, format="%d"),
                "Infrastructure Type": st.column_config.TextColumn(disabled=True),
                "Source Section": st.column_config.TextColumn(disabled=True),
                "Source Item Title": st.column_config.TextColumn(disabled=True),
            },
            column_order=[
                "Geography / Context",
                "Low Est. (USD)",
                "High Est. (USD)",
                "Source Mid (USD)",
                "Source Name",
                "Full Citation",
                "Year",
            ],
        )

        edited_group_df = edited_group_df.reset_index(drop=True)

        edited_group_df["Low Est. (USD)"] = to_numeric_series(
            edited_group_df["Low Est. (USD)"]
        )
        edited_group_df["High Est. (USD)"] = to_numeric_series(
            edited_group_df["High Est. (USD)"]
        )
        edited_group_df["Source Mid (USD)"] = edited_group_df.apply(
            lambda row: calculate_source_mid(row["Low Est. (USD)"], row["High Est. (USD)"]),
            axis=1,
        )

        blended_low = calculate_blended_average(edited_group_df["Low Est. (USD)"])
        blended_high = calculate_blended_average(edited_group_df["High Est. (USD)"])
        blended_mid = calculate_source_mid(blended_low, blended_high)

        existing_override = st.session_state["rnti_blended_overrides"].get(int(budget_row), {})
        display_blended_low = to_numeric_series(pd.Series([existing_override.get("Low Est. (USD)")])).iloc[0]
        display_blended_high = to_numeric_series(pd.Series([existing_override.get("High Est. (USD)")])).iloc[0]
        if pd.isna(display_blended_low):
            display_blended_low = blended_low
        if pd.isna(display_blended_high):
            display_blended_high = blended_high
        display_blended_mid = calculate_source_mid(display_blended_low, display_blended_high)

        blended_editor_df = pd.DataFrame(
            [
                {
                    "Geography / Context": "BLENDED AVERAGE (Min / Max / Mid)",
                    "Low Est. (USD)": display_blended_low,
                    "High Est. (USD)": display_blended_high,
                    "Source Mid (USD)": display_blended_mid,
                    "Source Name": None,
                    "Full Citation": None,
                    "Year": None,
                }
            ]
        )

        edited_blended_df = st.data_editor(
            blended_editor_df,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key=f"rnti_blended_editor_{budget_row}",
            column_order=[
                "Geography / Context",
                "Low Est. (USD)",
                "High Est. (USD)",
                "Source Mid (USD)",
                "Source Name",
                "Full Citation",
                "Year",
            ],
            column_config={
                "Geography / Context": st.column_config.TextColumn(disabled=True, width="large"),
                "Low Est. (USD)": st.column_config.NumberColumn(format="$%0.0f"),
                "High Est. (USD)": st.column_config.NumberColumn(format="$%0.0f"),
                "Source Mid (USD)": st.column_config.NumberColumn(disabled=True, format="$%0.0f"),
                "Source Name": st.column_config.LinkColumn(disabled=True, width="medium"),
                "Full Citation": st.column_config.TextColumn(disabled=True, width="large"),
                "Year": st.column_config.NumberColumn(disabled=True, format="%d"),
            },
        )

        edited_blended_low = to_numeric_series(pd.Series([edited_blended_df.at[0, "Low Est. (USD)"]])).iloc[0]
        edited_blended_high = to_numeric_series(pd.Series([edited_blended_df.at[0, "High Est. (USD)"]])).iloc[0]
        if pd.isna(edited_blended_low):
            edited_blended_low = blended_low
        if pd.isna(edited_blended_high):
            edited_blended_high = blended_high
        new_blended_overrides[int(budget_row)] = {
            "Low Est. (USD)": edited_blended_low,
            "High Est. (USD)": edited_blended_high,
        }

        grouped_source_frames.append(edited_group_df)

    editable_source_df = pd.concat(grouped_source_frames, ignore_index=True)
    editable_source_df["Low Est. (USD)"] = to_numeric_series(editable_source_df["Low Est. (USD)"])
    editable_source_df["High Est. (USD)"] = to_numeric_series(editable_source_df["High Est. (USD)"])
    editable_source_df["Source Mid (USD)"] = editable_source_df.apply(
        lambda row: calculate_source_mid(row["Low Est. (USD)"], row["High Est. (USD)"]),
        axis=1,
    )

    source_changed = not editable_source_df.equals(st.session_state["rnti_source_data_df"])
    overrides_changed = new_blended_overrides != st.session_state["rnti_blended_overrides"]

    if source_changed:
        st.session_state["rnti_source_data_df"] = editable_source_df.copy()
    if overrides_changed:
        st.session_state["rnti_blended_overrides"] = new_blended_overrides

    if source_changed or overrides_changed:
        st.rerun()

with st.expander("Methodology and caveats"):
    st.markdown(
        """
- Unit costs are blended approximations from verifiable sources in the workbook.
- Items with no verifiable source are intentionally left blank.
- Actual costs vary by country, terrain, labor, materials, and design specification.
- This is a conversation/planning tool, not a final engineering cost estimate.
- Maintenance is represented as a reserve percentage, not full lifecycle costing.
"""
    )
