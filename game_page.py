import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from functions import solve, fetch_puzzle # Your imports are fine

st.set_page_config(layout="centered")
st.title("Streamlit Sudoku with `AgGrid`")

difficulty = st.selectbox(
    "Select Difficulty :",
    ("easy", "medium", "hard"),
    key='difficulty_select' # Add a key for reliable state checking
)


# --- 2. SESSION STATE LOGIC (FIX 1) ---
# We must re-initialize the board IF
# 1. The board doesn't exist yet ('board' not in st.session_state)
# 2. The difficulty setting has been changed
if 'board' not in st.session_state or 'puzzle_fetched_for_difficulty' not in st.session_state or st.session_state.puzzle_fetched_for_difficulty != difficulty:
    initial_puzzle = fetch_puzzle(difficulty)
    st.session_state.board = pd.DataFrame(
        initial_puzzle,
        columns=[str(i) for i in range(9)],
        dtype=object
    ).replace(0, None)

# --- 3. STYLING (This part is correct) ---
css = """
<style>
    .ag-theme-balham .ag-cell[col-id="2"],
    .ag-theme-balham .ag-cell[col-id="5"] {
        border-right: 3px solid #888 !important;
    }

    .ag-theme-balham .ag-row.ag-bottom-border .ag-cell {
        border-bottom: 3px solid #888 !important;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

add_row_border = JsCode("""
function(params) {
    if (params.node.rowIndex === 2 || params.node.rowIndex === 5) {
        return 'ag-bottom-border';
    }
    return null;
}
""")


# --- 4. AGGRID CONFIGURATION (THIS IS THE FIX) ---
gb = GridOptionsBuilder.from_dataframe(st.session_state.board)

gb.configure_default_column(
    editable=True,
    width=45,
    # height=45,  <-- REMOVED. This was the error.
    resizable=False,
    singleClickEdit=True,
    cellEditor='agNumberCellEditor',
    cellEditorParams={'min': 1, 'max': 9, 'precision': 0},
    cellStyle={'textAlign': 'center', 'fontSize': '18px'} # Removed lineHeight
)

# Apply the row-border-adding function AND set rowHeight
gb.configure_grid_options(
    getRowClass=add_row_border,
    rowHeight=45  # <-- THIS IS THE FIX. It makes the rows 45px tall.
)
gridOptions = gb.build()


# --- 5. RENDER THE GRID (This part is correct) ---
st.write("Enter numbers (1-9) into the grid. Press Enter to save a cell.")

grid_response = AgGrid(
    st.session_state.board,
    gridOptions=gridOptions,
    height=425,  # 9 rows * 45px + 2*3px borders + padding
    width=425,   # 9 cols * 45px + 2*3px borders + padding
    data_return_mode='AS_INPUT',
    update_mode='VALUE_CHANGED',
    fit_columns_on_grid_load=False, # Correct
    theme='balham',                 # Correct
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False
)

# --- 6. GET DATA BACK (This part is correct) ---
st.session_state.board = grid_response['data']

# --- 7. (FOR YOU) USE THE DATA (This part is correct) ---
if st.button("Check My Solution"):
    current_board_list = st.session_state.board.fillna(0).astype(int).values.tolist()
    st.info("Check button clicked! The board is ready for validation.")
    st.write(current_board_list)
