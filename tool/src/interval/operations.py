def parse_condition_to_interval(condition: str) -> Optional[Tuple[int, int]]:
    """Parse a SQL condition to an interval."""
    match = re.findall(r"(\w+)\s*([<>]=?)\s*(\d+)", condition)
    if not match:
        return None
    min_value, max_value = None, None
    for attr, operator, value in match:
        value = int(value)
        if operator in (">", ">="):
            min_value = value + (1 if operator == ">" else 0)
        elif operator in ("<", "<="):
            max_value = value - (1 if operator == "<" else 0)   
    return min_value, max_value

def is_subset(interval_a: Optional[Tuple[int, int]], interval_b: Optional[Tuple[int, int]]) -> bool:
    """Check if interval_a is a subset of interval_b."""
    if interval_a is None or interval_b is None:
        return False  # Non-existent intervals can't be subsets
    a_min, a_max = interval_a
    b_min, b_max = interval_b
    return a_min >= b_min and a_max <= b_max

def intervals_overlap(interval1: Optional[Tuple[int, int]], interval2: Optional[Tuple[int, int]]) -> bool:
    """Check if two intervals overlap."""
    if not interval1 or not interval2 or len(interval1) != 2 or len(interval2) != 2:
        return False
    return interval1[0] < interval2[1] and interval2[0] < interval1[1]

def extract_sql_statements(input_file: str) -> Tuple[List[str], List[int]]:
    """Extracts SQL statements from executeUpdate and openrs, handling parameterized calls."""
    sql_statements = []
    line_numbers = []
    
    # Enhanced pattern to handle object.method() calls and parameters
    method_pattern = re.compile(
        r'(executeUpdate|openrs)\s*\(\s*.*?["\'](.*?)["\']\s*\)',
        re.IGNORECASE
    )
    sql_keyword_pattern = re.compile(r'^\s*(INSERT|SELECT|UPDATE|DELETE)\b', re.IGNORECASE)

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        inside_sql = False
        sql_buffer = []
        sql_start_line = 0
        quote_char = None

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Detect method calls with SQL strings, ignoring case and object prefixes
            method_match = method_pattern.search(line)
            if method_match:
                sql_candidate = method_match.group(2).strip()
                if sql_keyword_pattern.match(sql_candidate):
                    sql_statements.append(sql_candidate)
                    line_numbers.append(line_num)
                continue

            # Handle multi-line SQL statements more flexibly
            if not inside_sql and ('executeupdate(' in line.lower() or 'openrs(' in line.lower()):
                # Check for quote to start capturing
                if '"' in line or "'" in line:
                    inside_sql = True
                    sql_start_line = line_num
                    quote_char = '"' if '"' in line else "'"
                    parts = line.split(quote_char, 1)
                    if len(parts) > 1:
                        sql_buffer.append(parts[1])
                    continue
            
            if inside_sql:
                # Check for closing quote and parenthesis
                end_quote_pos = line.find(quote_char + ')')
                if end_quote_pos != -1:
                    sql_buffer.append(line[:end_quote_pos])
                    inside_sql = False
                    full_sql = ' '.join(sql_buffer).strip()
                    if sql_keyword_pattern.match(full_sql):
                        sql_statements.append(full_sql)
                        line_numbers.append(sql_start_line)
                    sql_buffer = []
                else:
                    sql_buffer.append(line)
        
        return sql_statements, line_numbers
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return [], []

def execute_sql_query(connection: mysql.connector.connection.MySQLConnection, query: str) -> Optional[List[Tuple]]:
    """Execute the given SQL query and fetch results for all operations (SELECT, INSERT, UPDATE, DELETE)."""
    print("Query:", query)
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        # Handle SELECT queries
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
            print("Query Result:", result)
            return result
        
        # Handle DML (INSERT, UPDATE, DELETE) queries
        else:
            connection.commit()
            print(f"Rows Affected: {cursor.rowcount}")
            
            # Fetch rows after INSERT
            if query.strip().lower().startswith("insert"):
                last_id = cursor.lastrowid
                if 'into' in query.lower():  # If the table has an auto-incremented column
                    # Fetch the newly inserted row
                    table_name = query.lower().split("into")[1].split("(")[0].strip()
                    select_query = f"SELECT * FROM {table_name} WHERE id = {last_id}"
                    print("Fetching inserted row with:", select_query)
                    cursor.execute(select_query)
                    result = cursor.fetchall()
                    print("Query Result (Inserted Row):", result)
                    return result
                else:
                    print("Last Inserted ID not available. Skipping row fetch.")
            
            # Fetch rows after UPDATE or DELETE
            elif query.strip().lower().startswith(("update", "delete")):
                where_clause_start = query.lower().find("where")
                if where_clause_start != -1:  # Check if there is a WHERE clause
                    table_name = query.split(" ")[1]  # Extract table name
                    select_query = f"SELECT * FROM {table_name} " + query[where_clause_start:]
                    
                    print("Fetching updated rows with:", select_query)
                    cursor.execute(select_query)
                    result = cursor.fetchall()
                    print("Query Result (Affected Rows):", result)
                    return result
                else:
                    print("No WHERE clause found to fetch specific rows.")
            
            print("Query executed successfully.")
            return None
    
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        return None
    
    finally:
        if cursor:
            cursor.close()

def execute_sql_statements(sql_statements: List[str]) -> None:
    """Execute extracted SQL statements on the database."""
    connection = connect_to_db()
    if connection:
        try:
            for statement in sql_statements:
                print(f"Executing SQL: {statement}")
                execute_sql_query(connection, statement)
        finally:
            connection.close()

def find_min_max_attribute_before_after(
    connection: mysql.connector.connection.MySQLConnection, table_name: str, attribute: str, statement: str
) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    """Find the min and max values of an attribute in a table before and after a SQL statement."""
    try:
        print("attribute:",attribute)
        before_query = f"SELECT MIN({attribute}), MAX({attribute}) FROM {table_name};"
        before_result = execute_sql_query(connection, before_query)
        before_interval = (before_result[0][0], before_result[0][1]) if before_result else None

        execute_sql_query(connection, statement)

        after_query = f"SELECT MIN({attribute}), MAX({attribute}) FROM {table_name};"
        after_result = execute_sql_query(connection, after_query)
        after_interval = (after_result[0][0], after_result[0][1]) if after_result else None

        return before_interval, after_interval
    except Exception as e:
        print(f"Error finding min and max before/after {statement}: {e}")
        return None, None

def split_action_and_condition(sql_statements: List[str], connection: mysql.connector.connection.MySQLConnection) -> List[Dict]:
    """Split SQL statements into action, condition, and extract parts."""
    results = []
    for statement in sql_statements:
        # Handle case sensitivity in 'WHERE' keyword
        where_pattern = re.compile(r'\bWHERE\b', re.IGNORECASE)
        where_match = where_pattern.search(statement)
        
        # Split into action and condition
        if where_match:
            action = statement[:where_match.start()].strip()
            condition = statement[where_match.end():].strip().rstrip(';').strip()
        else:
            action = statement.strip()
            condition = None
        
        # Extract true/modified/false parts
        true_part, modified_part, false_part = extract_true_modified_false(connection, action, condition)
        
        # Calculate intervals based on the data
        before_interval, after_interval = form_intervals(true_part, modified_part)
        
        # Append results with all required information
        results.append({
            "action": action,
            "condition": condition,
            "before_interval": before_interval,
            "after_interval": after_interval,
            "true_part": true_part,
            "modified_part": modified_part,
            "false_part": false_part,
        })
    
    return results

def intersect(interval_a: Optional[Tuple[int, int]], interval_b: Optional[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """Find the intersection of two intervals, handling None inputs properly."""
    # Return None if either interval is None
    if interval_a is None or interval_b is None:
        return None
    
    # Ensure inputs are in the correct format
    if isinstance(interval_a, tuple): 
        interval_a = [interval_a]
    if isinstance(interval_b, tuple): 
        interval_b = [interval_b]
    
    # Handle empty lists
    if not interval_a or not interval_b:
        return None
    
    overlaps = []
    for a in interval_a:
        for b in interval_b:
            # Only process valid tuples with 2 elements
            if a and b and len(a) == 2 and len(b) == 2:
                # Check if intervals overlap
                if a[0] < b[1] and b[0] < a[1]:
                    overlap = (max(a[0], b[0]), min(a[1], b[1]))
                    overlaps.append(overlap)
    
    return overlaps if overlaps else None

def union(interval1: Optional[Tuple[int, int]], interval2: Optional[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """Find the union of two intervals, returning merged or separate intervals."""
    # Handle None cases correctly
    if interval1 is None and interval2 is None:
        return None
    if interval1 is None:
        return [interval2] if isinstance(interval2, tuple) else interval2
    if interval2 is None:
        return [interval1] if isinstance(interval1, tuple) else interval1
    
    # Ensure both are valid tuples with 2 elements
    if not isinstance(interval1, tuple) or not isinstance(interval2, tuple) or len(interval1) != 2 or len(interval2) != 2:
        # Return the valid one if only one is valid
        if isinstance(interval1, tuple) and len(interval1) == 2:
            return [interval1]
        if isinstance(interval2, tuple) and len(interval2) == 2:
            return [interval2]
        return None
    
    # Check if intervals overlap or are adjacent
    if (interval1[0] <= interval2[1] and interval2[0] <= interval1[1]) or interval1[1] == interval2[0] or interval2[1] == interval1[0]:
        return [(min(interval1[0], interval2[0]), max(interval1[1], interval2[1]))]  # Merge overlapping/adjacent intervals
    
    return [interval1, interval2]  # Return separate intervals if disjoint

def subtract(interval1: Optional[Tuple[int, int]], interval2: Optional[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """Subtract interval2 from interval1, returning the remaining interval(s)."""
    # Handle None cases correctly
    if interval1 is None:
        return None
    if interval2 is None:
        return [interval1] if isinstance(interval1, tuple) and len(interval1) == 2 else None
    
    # Ensure both are valid tuples with 2 elements
    if not isinstance(interval1, tuple) or not isinstance(interval2, tuple) or len(interval1) != 2 or len(interval2) != 2:
        # Return interval1 if it's valid and interval2 is not
        if isinstance(interval1, tuple) and len(interval1) == 2:
            return [interval1]
        return None
    
    # Check if intervals overlap
    if not (interval1[0] < interval2[1] and interval2[0] < interval1[1]):
        return [interval1]  # No overlap, return interval1 unchanged

    # Calculate the remaining parts
    result = []
    if interval1[0] < interval2[0]:  # Left part remains
        result.append((interval1[0], min(interval1[1], interval2[0])))
    
    if interval1[1] > interval2[1]:  # Right part remains
        result.append((max(interval1[0], interval2[1]), interval1[1]))

    return result if result else None  # Return None if interval1 is fully subtracted

def form_intervals(true_part: List[Tuple], modified_part: List[Tuple]) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    """Compute intervals for a single statement's true and modified parts, considering all numeric values."""
    def compute_interval(rows: List[Tuple]) -> Optional[Tuple[int, int]]:
        numeric_values = []
        
        # Extract all numeric values from the rows
        for row in rows:
            for value in row:
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_values.append(value)
        
        # Return interval if we found any numeric values
        if numeric_values:
            return (int(min(numeric_values)), int(max(numeric_values)))
        return None
    
    # Calculate intervals for both parts
    true_interval = compute_interval(true_part)
    modified_interval = compute_interval(modified_part)
    
    return true_interval, modified_interval