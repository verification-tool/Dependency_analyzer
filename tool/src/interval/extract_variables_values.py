def extract_true_modified_false(
    connection: mysql.connector.connection.MySQLConnection, 
    action: str, 
    condition: str
) -> Tuple[List, List, List]:
    """Extract true, modified, and false parts of a SQL statement with enhanced handling."""
    true_part = []
    modified_part = []
    false_part = []
    cursor = None
    original_autocommit = connection.autocommit
    connection.autocommit = False  # Enable transactions

    try:
        # Extract table name with schema support
        table_match = re.search(
            r"(?:UPDATE\s+|FROM\s+|INTO\s+|INSERT\s+INTO\s+)([\w.]+)", 
            action, 
            re.IGNORECASE
        )
        if not table_match:
            return [], [], []
            
        full_table_name = table_match.group(1)
        table_name = full_table_name.split('.')[-1]  # Handle schema.table format
        has_condition = bool(condition.strip()) if condition else False

        # Start transaction
        cursor = connection.cursor()

        # Handle UPDATE statements
        if action.upper().startswith("UPDATE"):
            # Get original state (true part)
            true_query = (f"SELECT * FROM {full_table_name} "
                         f"{f'WHERE {condition}' if has_condition else ''}")
            true_part = execute_sql_query(connection, true_query) or []

            # Execute modification
            update_query = (f"{action} "
                           f"{f'WHERE {condition}' if has_condition else ''}")
            execute_sql_query(connection, update_query)

            # Get modified state (modified part)
            modified_part = execute_sql_query(connection, true_query) or []

            # Get false part if condition exists
            if has_condition:
                false_query = f"SELECT * FROM {full_table_name} WHERE NOT ({condition})"
                false_part = execute_sql_query(connection, false_query) or []

        # Handle DELETE statements
        elif action.upper().startswith("DELETE"):
            # Get original state (true part)
            true_query = (f"SELECT * FROM {full_table_name} "
                         f"{f'WHERE {condition}' if has_condition else ''}")
            true_part = execute_sql_query(connection, true_query) or []

            # Execute deletion
            delete_query = (f"{action} "
                           f"{f'WHERE {condition}' if has_condition else ''}")
            execute_sql_query(connection, delete_query)

            # Modified part is same as true part (deleted rows)
            modified_part = true_part.copy()

            # Get remaining rows (false part)
            false_query = f"SELECT * FROM {full_table_name}"
            false_part = execute_sql_query(connection, false_query) or []

        # Handle INSERT statements
        elif action.upper().startswith("INSERT"):
            # Get pre-insert state (false part)
            false_query = f"SELECT * FROM {full_table_name}"
            false_part = execute_sql_query(connection, false_query) or []

            # Execute insertion
            execute_sql_query(connection, action)

            # Get post-insert state
            after_query = f"SELECT * FROM {full_table_name}"
            after_insert = execute_sql_query(connection, after_query) or []

            # Calculate true part (newly inserted rows)
            true_part = [row for row in after_insert if row not in false_part]
            modified_part = true_part.copy()

        # Handle SELECT statements
        elif action.upper().startswith("SELECT"):
            # True part is the selected rows
            true_query = (f"{action} "
                         f"{f'WHERE {condition}' if has_condition else ''}")
            true_part = execute_sql_query(connection, true_query) or []

            # False part is inverse of condition if exists
            if has_condition:
                false_query = f"SELECT * FROM {full_table_name} WHERE NOT ({condition})"
                false_part = execute_sql_query(connection, false_query) or []

        connection.commit()

    except Exception as e:
        print(f"Error in extract_true_modified_false: {str(e)}")
        connection.rollback()
        # Reset collections on error
        true_part, modified_part, false_part = [], [], []
    finally:
        connection.autocommit = original_autocommit
        if cursor:
            cursor.close()

    return true_part, modified_part, false_part