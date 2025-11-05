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


# --- 3. STYLING (FIX 2) ---
# We will use the 'balham' theme.
# YOU MUST change the CSS selectors from .ag-theme-streamlit to .ag-theme-balham
css = """
<style>
    /* Target the 'balham' theme */
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

# This JsCode is correct and unchanged
add_row_border = JsCode("""
function(params) {
    if (params.node.rowIndex === 2 || params.node.rowIndex === 5) {
        return 'ag-bottom-border';
    }
    return null;
}
""")


# --- 4. AGGRID CONFIGURATION ---
gb = GridOptionsBuilder.from_dataframe(st.session_state.board)

gb.configure_default_column(
    editable=True,
    width=45,
    height=45,
    resizable=False,
    singleClickEdit=True,
    cellEditor='agNumberCellEditor',
    cellEditorParams={'min': 1, 'max': 9, 'precision': 0},
    cellStyle={'textAlign': 'center', 'fontSize': '18px', 'lineHeight': '40px'} # Added lineHeight for vertical center
)

gb.configure_grid_options(getRowClass=add_row_border)
gridOptions = gb.build()


# --- 5. RENDER THE GRID (FIX 2) ---
st.write("Enter numbers (1-9) into the grid. Press Enter to save a cell.")

grid_response = AgGrid(
    st.session_state.board,
    gridOptions=gridOptions,
    height=425,
    width=425,
    data_return_mode='AS_INPUT',
    update_mode='VALUE_CHANGED',
    
    # --- HERE ARE THE STYLING FIXES ---
    fit_columns_on_grid_load=False, # <-- MUST be False to use custom widths
    theme='balham',                 # <-- Use a theme that allows custom styles
    # ----------------------------------
    
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False
)

# --- 6. GET DATA BACK AND STORE IT ---
st.session_state.board = grid_response['data']


# --- 7. (FOR YOU) USE THE DATA ---
if st.button("Check My Solution"):
    # Convert DataFrame back to a 2D list, filling empty cells (None) with 0
    current_board_list = st.session_state.board.fillna(0).astype(int).values.tolist()
    
    # result = solve(current_board_list) # Use your function
    # st.write(result)
    
    st.info("Check button clicked! The board is ready for validation.")
    st.write(current_board_list)
