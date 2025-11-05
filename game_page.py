import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from functions import solve, fetch_puzzle

st.set_page_config(layout="centered")
st.title("Streamlit Sudoku with `AgGrid`")

# ----------------------------------------------------------------------
# 1. DEFINE YOUR INITIAL PUZZLE HERE
#
# Replace this with your 2D list. 
# Use 0 or None to represent empty cells.
# ----------------------------------------------------------------------
initial_puzzle = fetch_puzzle()

# --- 2. SESSION STATE INITIALIZATION ---
if 'board' not in st.session_state:
    # Convert your 2D list to a Pandas DataFrame
    # We use string columns ('0', '1', '2'...) for easier CSS targeting
    st.session_state.board = pd.DataFrame(
        initial_puzzle,
        columns=[str(i) for i in range(9)],
        dtype=object  # Use object type to allow for 0, None, or ints
    ).replace(0, None) # Use None for empty cells, agGrid handles this well


# --- 3. STYLING (The 3x3 Grid) ---

# Inject custom CSS for the 3x3 thick borders
css = """
<style>
    /* Add a thicker border to the right of columns '2' and '5' */
    .ag-theme-streamlit .ag-cell[col-id="2"],
    .ag-theme-streamlit .ag-cell[col-id="5"] {
        border-right: 3px solid #888 !important;
    }

    /* Add a thicker border to the bottom of rows 2 and 5 */
    /* We use a JsCode function to add a class 'ag-bottom-border' to these rows */
    .ag-theme-streamlit .ag-row.ag-bottom-border .ag-cell {
        border-bottom: 3px solid #888 !important;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Use JsCode to add a class to rows 2 and 5
# This function is passed to AgGrid and runs in the browser
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

# Configure all columns
gb.configure_default_column(
    editable=True,
    width=45,
    height=45,
    resizable=False,
    singleClickEdit=True,
    # Restrict input to numbers 1-9 (and None/clear)
    cellEditor='agNumberCellEditor',
    cellEditorParams={'min': 1, 'max': 9, 'precision': 0},
    # Center-align the text in cells
    cellStyle={'textAlign': 'center', 'fontSize': '18px'}
)

# Apply the row-border-adding function
gb.configure_grid_options(getRowClass=add_row_border)

gridOptions = gb.build()


# --- 5. RENDER THE GRID ---
st.write("Enter numbers (1-9) into the grid. Press Enter to save a cell.")

grid_response = AgGrid(
    st.session_state.board,
    gridOptions=gridOptions,
    height=425,  # 9 rows * 45px + 2*3px border + padding
    width=425,   # 9 cols * 45px + 2*3px border + padding
    data_return_mode='AS_INPUT',      # Returns a DataFrame
    
    # --- THIS IS THE CORRECTED LINE ---
    update_mode='VALUE_CHANGED',      # Triggers on each edit
    # ----------------------------------
    
    fit_columns_on_grid_load=True,    # Fit columns to width
    allow_unsafe_jscode=True,         # Required for getRowClass
    enable_enterprise_modules=False,
    theme='streamlit'                 # Use Streamlit's native theme
)

# --- 6. GET DATA BACK AND STORE IT ---
# The grid_response['data'] contains the new state of the DataFrame
# We overwrite the session_state to save the user's edit
st.session_state.board = grid_response['data']


# --- 7. (FOR YOU) USE THE DATA ---
st.divider()
st.subheader("Current Board State (for your logic)")

# You can now access the current board for your validation functions
current_board_df = st.session_state.board

# Convert DataFrame back to a 2D list, filling empty cells (None) with 0
# This gives you the format you're used to
current_board_list = current_board_df.fillna(0).astype(int).values.tolist()

st.write("This is the current board as a Pandas DataFrame:")
st.dataframe(current_board_df)

st.write("And as a 2D Python list (with 0 for empty):")
st.write(current_board_list)

# You would now pass 'current_board_list' to your checking/solving functions
if st.button("Check My Solution"):
    # result = your_validation_function(current_board_list)
    # st.write(result)
    st.info("Check button clicked! Use the `current_board_list` variable for your logic.")
