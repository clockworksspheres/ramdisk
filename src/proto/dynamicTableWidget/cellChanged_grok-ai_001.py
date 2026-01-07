def on_cell_changed(current_row, current_col, prev_row, prev_col):
    print(f"Current: ({current_row}, {current_col}), Previous: ({prev_row}, {prev_col})")
table.currentCellChanged.connect(on_cell_changed)


