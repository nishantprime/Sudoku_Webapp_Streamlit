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
    df = pd.DataFrame(puzzle, columns=[str(i) for i in range(9)]).replace(0, None)
    st.session_state.board = df
    st.session_state.givens = {(r, c) for r, row in enumerate(puzzle) for c, v in enumerate(row) if v != 0}

# ---------- CSS (target BOTH alpine + alpine-dark) ----------
st.markdown("""
<style>
.ag-theme-alpine-dark, .ag-theme-alpine {
  --ag-foreground-color: #eaeaea;
  --ag-background-color: #111418;
  --ag-header-background-color: #111418;
  --ag-borders: none;
  font-size: 18px;
}
.ag-theme-alpine-dark .ag-root-wrapper, .ag-theme-alpine .ag-root-wrapper {
  border-radius: 12px; box-shadow: 0 0 0 1px #2b2f36 inset;
}
.ag-theme-alpine-dark .ag-cell, .ag-theme-alpine .ag-cell {
  display:flex; align-items:center; justify-content:center; font-weight:500;
}

/* Given (prefilled) cells */
.ag-theme-alpine-dark .ag-cell.given, .ag-theme-alpine .ag-cell.given {
  color:#a9b1c6; font-weight:700; background:#141820;
}

/* Kill selection/outline noise */
.ag-theme-alpine-dark .ag-cell-focus, .ag-theme-alpine .ag-cell-focus,
.ag-theme-alpine-dark .ag-cell-range-single-cell, .ag-theme-alpine .ag-cell-range-single-cell,
.ag-theme-alpine-dark .ag-range-selected, .ag-theme-alpine .ag-range-selected {
  border:none !important; box-shadow:none !important;
}
.ag-theme-alpine-dark .ag-cell:focus-within, .ag-theme-alpine .ag-cell:focus-within { outline:none !important; }

/* 3×3 borders (cols 2 & 5; rows 2 & 5) */
.ag-theme-alpine-dark .ag-cell[col-id="2"], .ag-theme-alpine .ag-cell[col-id="2"],
.ag-theme-alpine-dark .ag-cell[col-id="5"], .ag-theme-alpine .ag-cell[col-id="5"] {
  border-right: 3px solid #4a4f58 !important;
}
.ag-theme-alpine-dark .box-bottom .ag-cell, .ag-theme-alpine .box-bottom .ag-cell {
  border-bottom: 3px solid #4a4f58 !important;
}

/* Hide header line */
.ag-theme-alpine-dark .ag-header, .ag-theme-alpine .ag-header { border-bottom:none !important; }
</style>
""", unsafe_allow_html=True)

# ---------- JS HELPERS ----------
row_class = JsCode("""
function(params){
  const r = params.node.rowIndex;
  return (r === 2 || r === 5) ? 'box-bottom' : null;
}
""")

given_cells = list(st.session_state.givens)

is_given_js = JsCode(f"""
function(params){{
  const r = params.node.rowIndex;
  const c = parseInt(params.colDef.field);
  const G = new Set({given_cells}.map(x => x[0] + ',' + x[1]));
  return !G.has(r + ',' + c);  // editable? false for givens
}}
""")

given_class_js = JsCode(f"""
function(params){{
  const r = params.node.rowIndex;
  const c = parseInt(params.colDef.field);
  const G = new Set({given_cells}.map(x => x[0] + ',' + x[1]));
  return G.has(r + ',' + c) ? 'given' : null;
}}
""")

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

# ---------- GRID OPTIONS ----------
CELL = 56  # cell size for square feel

gb = GridOptionsBuilder.from_dataframe(st.session_state.board)
gb.configure_default_column(
    editable=True,
    resizable=False,
    sortable=False,
    filter=False,
    width=CELL,
    cellClass=given_class_js,
    valueSetter=value_setter_js,
    cellEditor='agTextCellEditor',
)
gb.configure_grid_options(
    getRowClass=row_class,
    rowHeight=CELL,
    headerHeight=0,
    suppressCellSelection=True,
    suppressRowClickSelection=True,
    enableRangeSelection=False,
    undoRedoCellEditing=True,
    undoRedoCellEditingLimit=50,
    suppressMovableColumns=True,
    ensureDomOrder=True,
    animateRows=False,
    stopEditingWhenCellsLoseFocus=False,
)
for col in [str(i) for i in range(9)]:
    gb.configure_column(col, editable=is_given_js)

grid_options = gb.build()

st.caption("Enter digits 1–9. Press Enter to save a cell. Backspace to clear.")

# ---------- RENDER ----------
c1, c2, c3 = st.columns([1, 12, 1])
with c2:
    grid_response = AgGrid(
        st.session_state.board,
        gridOptions=grid_options,
        theme="alpine-dark",
        height=9*CELL + 2*3 + 24,  # rows + two thick borders + padding
        data_return_mode="AS_INPUT",
        update_mode="VALUE_CHANGED",
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
    )

st.session_state.board = grid_response["data"]

# ---------- ACTIONS ----------
colA, colB, colC = st.columns([2,2,2])

with colA:
    if st.button("Check My Solution", use_container_width=True):
        df = st.session_state.board
        def valid_block(vals):
            nums = [v for v in vals if pd.notna(v)]
            return len(nums) == len(set(nums))
        ok = True
        # rows & cols
        for i in range(9):
            ok &= valid_block(df.iloc[i].tolist())
            ok &= valid_block(df.iloc[:, i].tolist())
        # 3x3 boxes
        for r in range(0, 9, 3):
            for c in range(0, 9, 3):
                vals = df.iloc[r:r+3, c:c+3].values.flatten().tolist()
                ok &= valid_block(vals)
        st.success("Looks valid so far! (Not necessarily solved)") if ok else st.error("There are conflicts. Keep tweaking!")

with colB:
    if st.button("Solve", use_container_width=True):
        raw = st.session_state.board.fillna(0).astype(int).values.tolist()
        try:
            solved = solve(raw)
            st.session_state.board = pd.DataFrame(solved, columns=[str(i) for i in range(9)])
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Could not solve: {e}")

with colC:
    if st.button("Reset", use_container_width=True):
        puzzle = fetch_puzzle(st.session_state.diff)
        st.session_state.board = pd.DataFrame(puzzle, columns=[str(i) for i in range(9)]).replace(0, None)
        st.experimental_rerun()
