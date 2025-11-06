import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from functions import solve, fetch_puzzle

st.set_page_config(layout="centered")
st.title("Streamlit Sudoku with `AgGrid`")

difficulty = st.selectbox("Select Difficulty :", ("easy", "medium", "hard"), key="difficulty_select")

# ---------- SESSION STATE ----------
if (
    "board" not in st.session_state
    or "givens" not in st.session_state
    or st.session_state.get("diff") != difficulty
):
    puzzle = fetch_puzzle(difficulty)
    st.session_state.diff = difficulty
    # store board as None for blanks (for nice display)
    df = pd.DataFrame(puzzle, columns=[str(i) for i in range(9)]).replace(0, None)
    st.session_state.board = df
    # coordinates of fixed cells (row,col) where puzzle had numbers
    st.session_state.givens = {(r, c) for r, row in enumerate(puzzle) for c, v in enumerate(row) if v != 0}

# ---------- CSS (alpine-dark) ----------
st.markdown("""
<style>
.ag-theme-alpine-dark {
  --ag-foreground-color: #eaeaea;
  --ag-background-color: #111418;
  --ag-header-background-color: #111418;
  --ag-borders: none;
  font-size: 18px;
}
.ag-theme-alpine-dark .ag-root-wrapper { border-radius: 12px; box-shadow: 0 0 0 1px #2b2f36 inset; }
.ag-theme-alpine-dark .ag-cell {
  display:flex; align-items:center; justify-content:center;
  font-weight: 500;
}
.ag-theme-alpine-dark .ag-cell.given { color:#a9b1c6; font-weight:700; background: #141820; }
.ag-theme-alpine-dark .ag-cell.editing { background:#1a1f27 !important; }
.ag-theme-alpine-dark .ag-cell:focus-within { outline: 2px solid #3a81ff55 !important; }

 /* 3×3 borders */
.ag-theme-alpine-dark .ag-cell[col-id="2"],
.ag-theme-alpine-dark .ag-cell[col-id="5"] { border-right: 3px solid #4a4f58 !important; }
.ag-theme-alpine-dark .ag-row.ag-block-bottom .ag-cell { border-bottom: 3px solid #4a4f58 !important; }

 /* hide header line */
.ag-theme-alpine-dark .ag-header { border-bottom: none !important; }
</style>
""", unsafe_allow_html=True)

# JS: mark 3×3 horizontal borders
row_class = JsCode("""
function(params){
  const r = params.node.rowIndex;
  return (r === 2 || r === 5) ? 'ag-block-bottom' : null;
}
""")

# JS: prevent editing on givens
given_cells = list(st.session_state.givens)  # list of [row,col]
is_given_js = JsCode(f"""
function(params){{
  const r = params.node.rowIndex;
  const c = parseInt(params.colDef.field);
  const givens = new Set({given_cells}.map(x => x[0] + ',' + x[1]));
  return givens.has(r + ',' + c) ? false : true;  // editable?
}}
""")

# JS: add "given" class for styling
given_class_js = JsCode(f"""
function(params){{
  const r = params.node.rowIndex;
  const c = parseInt(params.colDef.field);
  const givens = new Set({given_cells}.map(x => x[0] + ',' + x[1]));
  return givens.has(r + ',' + c) ? 'given' : null;
}}
""")

# JS: coerce value to digits 1–9 or blank
value_setter_js = JsCode("""
function(params){
  let v = params.newValue;
  if (v === null || v === undefined) { params.data[params.colDef.field] = null; return true; }
  if (typeof v === 'string') v = v.trim();
  if (v === '') { params.data[params.colDef.field] = null; return true; }
  const n = Number(v);
  if (Number.isInteger(n) && n >= 1 && n <= 9) { params.data[params.colDef.field] = n; return true; }
  return false;  // reject invalid edits
}
""")

# ---------- Grid options ----------
gb = GridOptionsBuilder.from_dataframe(st.session_state.board)

# Default column config
gb.configure_default_column(
    editable=True,
    resizable=False,
    sortable=False,
    filter=False,
    width=48,                      # square-ish cells
    cellClass=given_class_js,
    valueSetter=value_setter_js,
    cellEditor='agTextCellEditor', # we validate ourselves
)

# Per-grid options
gb.configure_grid_options(
    getRowClass=row_class,
    rowHeight=48,
    headerHeight=0,
    suppressCellSelection=True,        # no blue selection rectangle
    suppressRowClickSelection=True,
    undoRedoCellEditing=True,
    undoRedoCellEditingLimit=50,
    enableRangeSelection=False,
    suppressMovableColumns=True,
    suppressMenuHide=True,
    ensureDomOrder=True,
    animateRows=False,
    stopEditingWhenCellsLoseFocus=False
)

# Make givens readonly via editable callback
for col in [str(i) for i in range(9)]:
    gb.configure_column(col, editable=is_given_js)

grid_options = gb.build()

st.caption("Enter digits 1–9. Press Enter to save a cell. Backspace to clear.")

# Center the grid nicely
c1, c2, c3 = st.columns([1,12,1])
with c2:
    grid_response = AgGrid(
        st.session_state.board,
        gridOptions=grid_options,
        height=9*48 + 6*3 + 12,           # rows + thick borders + padding
        theme="alpine-dark",
        data_return_mode="AS_INPUT",
        update_mode="VALUE_CHANGED",
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=False
    )

st.session_state.board = grid_response["data"]
