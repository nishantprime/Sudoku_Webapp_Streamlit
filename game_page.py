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


# --- 2. SESSION STATE LOGIC (This part is correct) ---
if 'board' not in st.session_state or 'puzzle_fetched_for_difficulty' not in st.session_state or st.session_state.puzzle_fetched_for_difficulty != difficulty:
    initial_puzzle = fetch_puzzle(difficulty)
    # --- MOCK FUNCTION (in case fetch_puzzle isn't imported) ---
    # if 'fetch_puzzle' not in globals():
    #     st.session_state.puzzle_fetched_for_difficulty = difficulty
    #     initial_puzzle = [
    #         [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0],
    #         [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6],
    #         [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9]
    #     ]
    # else:
    #     initial_puzzle = fetch_puzzle(difficulty)
    # -------------------------------------------------------------
        
    st.session_state.board = pd.DataFrame(
        initial_puzzle,
        columns=[str(i) for i in range(9)],
        dtype=object
    ).replace(0, None)

# --- 3. STYLING (FIX: NEW THEME AND CSS) ---
css = """
<style>
    /* Target the 'alpine-dark' theme */
    .ag-theme-alpine-dark .ag-cell[col-id="2"],
    .ag-theme-alpine-dark .ag-cell[col-id="5"] {
        border-right: 3px solid #666 !important; /* Made border a bit lighter */
    }

    .ag-theme-alpine-dark .ag-row.ag-bottom-border .ag-cell {
        border-bottom: 3px solid #666 !important;
    }
    
    /* Remove the header's bottom border */
    .ag-theme-alpine-dark .ag-header {
        border-bottom: none !important;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# This JsCode is correct
add_row_border = JsCode("""
function(params) {
    if (params.node.rowIndex === 2 || params.node.rowIndex === 5) {
        return 'ag-bottom-border';
    }
    return null;
}
""")


# --- 4. AGGRID CONFIGURATION (FIX: HIDE HEADER) ---
gb = GridOptionsBuilder.from_dataframe(st.session_state.board)

gb.configure_default_column(
    editable=True,
    width=45,
    resizable=False,
    singleClickEdit=True,
    cellEditor='agNumberCellEditor',
    cellEditorParams={'min': 1, 'max': 9, 'precision': 0},
    cellStyle={'textAlign': 'center', 'fontSize': '18px'}
)

# Apply the row-border-adding function AND set rowHeight
gb.configure_grid_options(
    getRowClass=add_row_border,
    rowHeight=45,
    headerHeight=0  # <-- FIX: THIS HIDES THE "0, 1, 2..." HEADER
)
gridOptions = gb.build()


# --- 5. RENDER THE GRID (FIX: NEW THEME AND HEIGHT) ---
st.write("Enter numbers (1-9) into the grid. Press Enter to save a cell.")

grid_response = AgGrid(
    st.session_state.board,
    gridOptions=gridOptions,
    
    # --- FIXES ---
    height=415,  # (9 rows * 45px) + (2 borders * 3px) + 4px padding
    width=415,   # (9 cols * 45px) + (2 borders * 3px) + 4px padding
    theme='alpine-dark',            # <-- FIX: CHANGED THEME
    # -------------

    data_return_mode='AS_INPUT',
    update_mode='VALUE_CHANGED',
    fit_columns_on_grid_load=False, # Correct
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
