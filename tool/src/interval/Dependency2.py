import mysql.connector
from mysql.connector import Error
import re
from typing import List, Dict, Tuple, Optional,Any,Set
import numpy as np
import time as time
import copy
def execute_sql_file(connection: mysql.connector.MySQLConnection, file_path: str) -> None:
    """Execute all SQL statements in a given file."""
    cursor = None
    try:
        with open(file_path, 'r') as file:
            sql_script = file.read()
        
        # Split into statements, removing empty ones
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        cursor = connection.cursor()
        for stmt in statements:
            if stmt:  # Ensure not empty
                print(f"Executing: {stmt}")
                cursor.execute(stmt)
        connection.commit()
        print("Executed SQL file successfully.")
    except Error as e:
        print(f"Error executing SQL file {file_path}: {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()

def connect_to_db() -> Optional[mysql.connector.connection.MySQLConnection]:
    """Connect to the MySQL database and return the connection object."""
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Your host, e.g., localhost or an IP address
            user="root",  # Your database username
            password="your_password",  # Your database password
            database="your_database_name"  # Your database name
        )
        print("Connected to database successfully!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

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

def parse_condition_columns(condition: str) -> Set[str]:
    """Extracts column names from a SQL condition using regex."""
    SQL_KEYWORDS = {
        'and', 'or', 'not', 'in', 'like', 'between', 'is', 'null', 
        'true', 'false', 'select', 'where', 'from', 'update', 'insert', 'delete'
    }
    tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', condition.lower())
    return {token for token in tokens if token not in SQL_KEYWORDS and not token.isdigit()}

def get_modified_components(action: str) -> tuple[Set[str], Optional[str]]:
    """Extracts modified columns and table from SQL action."""
    action_upper = action.upper()
    modified_cols = set()
    modified_table = None

    if action_upper.startswith("UPDATE"):
        match = re.search(r"UPDATE\s+(\w+)\s+SET\s+(.*)", action, re.IGNORECASE)
        if match:
            modified_table = match.group(1).lower()
            set_clause = match.group(2)
            modified_cols = {m.group(1).lower() for m in re.finditer(r"(\w+)\s*=", set_clause)}

    elif action_upper.startswith("DELETE"):
        match = re.search(r"DELETE\s+FROM\s+(\w+)", action, re.IGNORECASE)
        if match:
            modified_table = match.group(1).lower()
            modified_cols = {'*'}  # DELETE modifies all columns

    elif action_upper.startswith("INSERT"):
        match = re.search(r"INSERT\s+INTO\s+(\w+)\s*(\(([^)]+)\))?", action, re.IGNORECASE)
        if match:
            modified_table = match.group(1).lower()
            if match.group(3):
                modified_cols = {col.strip().lower() for col in match.group(3).split(',')}
            else:
                modified_cols = {'*'}  # INSERT without specific columns

    return modified_cols, modified_table

def check_expression_overlap(modified_interval: Optional[tuple], true_interval: Optional[tuple]) -> bool:
    """Checks if two time intervals overlap."""
    if modified_interval is None or true_interval is None:
        return False  # No interval means no overlap
    
    mod_start, mod_end = modified_interval
    true_start, true_end = true_interval

    if mod_start is None or mod_end is None or true_start is None or true_end is None:
        return False  # Incomplete data

    return not (mod_end < true_start or true_end < mod_start)

def form_statement_dependency_matrix(
    actions: List[str],
    conditions: List[str],
    true_intervals: List[Optional[Tuple[int, int]]],
    modified_intervals: List[Optional[Tuple[int, int]]],
    matrix: np.ndarray
) -> np.ndarray:
    """
    Constructs a simplified dependency matrix for SQL statements.
    
    Args:
        actions: List of SQL statement actions.
        conditions: List of WHERE conditions for each action.
        true_intervals: Intervals representing data selected/used by each statement.
        modified_intervals: Intervals representing data modified by each statement.
        matrix: Pre-initialized numpy array to store dependencies.
        
    Returns:
        Updated dependency matrix where matrix[i, j] = 1 indicates a dependency from i to j.
    """
    N = len(actions)
    statement_tables = []     # Primary table per statement
    statement_attributes = [] # Attributes used or modified by each statement
    
    # Extract table and attributes for each statement
    for i, action in enumerate(actions):
        action_upper = action.upper()
        # Extract primary table (simplified)
        table = None
        if "FROM" in action_upper:
            match = re.search(r"FROM\s+([\w.]+)", action, re.IGNORECASE)
            table = match.group(1).lower() if match else None
        elif "UPDATE" in action_upper:
            match = re.search(r"UPDATE\s+([\w.]+)", action, re.IGNORECASE)
            table = match.group(1).lower() if match else None
        elif "INSERT" in action_upper:
            match = re.search(r"INSERT\s+INTO\s+([\w.]+)", action, re.IGNORECASE)
            table = match.group(1).lower() if match else None
        
        statement_tables.append(table)
        
        # Extract all attributes (simplified to catch most common patterns)
        attributes = set()
        # Get column names from SELECT, SET, or column lists
        col_matches = re.findall(r"(?:SELECT|SET)\s+(.*?)(?:\s+FROM|\s+WHERE|$)", action, re.IGNORECASE)
        for match in col_matches:
            cols = re.findall(r"([a-zA-Z0-9_]+)", match)
            attributes.update(col.lower() for col in cols)
        
        # Get column names from WHERE conditions
        if i < len(conditions) and conditions[i]:
            condition_cols = re.findall(r"([a-zA-Z0-9_]+)\s*(?:=|>|<|LIKE|IN|BETWEEN)", conditions[i], re.IGNORECASE)
            attributes.update(col.lower() for col in condition_cols)
        
        statement_attributes.append(attributes)
    
    # Check for dependencies
    for i in range(N):
        for j in range(i + 1, N):
            # Skip if statements operate on different tables
            if not statement_tables[i] or statement_tables[i] != statement_tables[j]:
                continue
            
            # Check if attributes overlap
            if statement_attributes[i] & statement_attributes[j]:
                # Check if intervals overlap
                if intervals_overlap(modified_intervals[i], true_intervals[j]) and intervals_overlap(true_intervals[i], true_intervals[j]) :
                    matrix[i, j] = 1
    
    return matrix

def dependency_analysis(matrix: List[List[int]], modified_intervals: List[Optional[Tuple[int, int]]], true_intervals: List[Optional[Tuple[int, int]]], results: List[Dict]) -> Tuple[List[List[int]], List, List[List[int]]]:
    """Perform dependency analysis and optimization on the given matrix."""
    print("True Intervals:", true_intervals)
    print("Modified Intervals:", modified_intervals)
    n = len(matrix)
    initial_matrix = [row.copy() for row in matrix]

    for i in range(n - 2):
        if i + 1 < len(results) and "SELECT" in results[i + 1]["action"]:
            matrix[i][i + 2] = 1

    for i in range(n - 2):
        for j in range(i + 2, n):
            if matrix[i][j] != 0:
                if i + 1 < len(results) and j < len(results):
                    if "SELECT" not in results[i]["action"] and "INSERT" not in results[j]["action"]:
                        if is_subset(modified_intervals[i], modified_intervals[i + 1]):
                            matrix[i][j] = 0
                        elif is_subset(modified_intervals[j], modified_intervals[i + 1]):
                            matrix[i][j] = 0
                        else:
                            X = subtract(true_intervals[j], intersect(true_intervals[j - 1], true_intervals[j]))
                            Y = subtract(modified_intervals[j], intersect(modified_intervals[j - 1], modified_intervals[j]))
                            if not (intersect(X, union(true_intervals[i], modified_intervals[i])) and 
                                    intersect(Y, union(true_intervals[i], modified_intervals[i]))):
                                matrix[i][j] = 0
                                print("3rd")
                            else:
                                matrix[i][j] = 1
                                print("4rth")
                                break
                    else:
                        break

    return matrix, [], initial_matrix

def load_schema(database_file: str) -> Dict[str, Dict[str, List]]:
    """Loads database schema with improved parsing of table structures."""
    schema = {}
    try:
        with open(database_file, 'r') as file:
            content = file.read()
            # Find all CREATE TABLE statements
            table_pattern = re.compile(
                r"CREATE TABLE\s+(\w+)\s*\((.*?)\);",
                re.IGNORECASE | re.DOTALL
            )
            for match in table_pattern.finditer(content):
                full_table_name = match.group(1).lower()
                table_name = full_table_name.split('.')[-1]  # Handle schema prefixes
                columns_def = match.group(2).strip()
                schema[table_name] = {'columns': [], 'foreign_keys': []}
                
                # Split columns and constraints
                elements = re.split(r',\s*(?![^()]*\))', columns_def)
                for elem in elements:
                    elem = elem.strip()
                    if not elem:
                        continue
                    
                    # Extract column name (first word)
                    col_match = re.match(r'^"?(\w+)"?', elem)
                    if col_match:
                        col_name = col_match.group(1).lower()
                        schema[table_name]['columns'].append(col_name)
                    
                    # Extract foreign key references
                    fk_match = re.search(
                        r'FOREIGN KEY\s*\(.*?\)\s*REFERENCES\s+(\w+)',
                        elem, re.IGNORECASE
                    )
                    if fk_match:
                        ref_table = fk_match.group(1).lower().split('.')[-1]
                        schema[table_name]['foreign_keys'].append(ref_table)
        return schema
    except FileNotFoundError:
        print("Error: Schema file not found.")
        return {}

def split_action_and_condition1(sql_statements: List[str]) -> List[Dict[str, str]]:
    """Splits SQL statements into action and condition parts."""
    results = []
    for stmt in sql_statements:
        stmt = re.sub(r'\s+', ' ', stmt).strip()
        where_match = re.search(r'\bWHERE\b', stmt, re.IGNORECASE)
        if where_match:
            action = stmt[:where_match.start()].strip()
            condition = stmt[where_match.end():].strip()
        else:
            action = stmt
            condition = ""
        results.append({"action": action, "condition": condition})
    return results

def extract_used_and_defined(results: List[Dict[str, Any]], schema: dict) -> Tuple[List[List[str]], List[List[str]], List[str]]:
    """Extracts variables used and defined in SQL statements."""
    used, defined, tables_affected = [], [], []
    sql_keywords = {"and", "or", "not", "in", "like", "between", "is", "null", "true", "false"}
    
    for item in results:
        action = item["action"].lower()
        condition = item["condition"].lower()
        table_name, def_cols, use_cols = None, [], []

        # Extract table name
        table_match = re.search(
            r"(?:update|insert\s+into|delete\s+from)\s+(\w+)|from\s+(\w+)", 
            action, re.IGNORECASE
        )
        table_name = (table_match.group(1) or table_match.group(2)).lower() if table_match else None
        
        # Process different SQL operations
        # In extract_used_and_defined()
        if 'select' in action:
    # Extract table name (handling FROM clause)
            table_match = re.search(
        r"(?:from|join)\s+(\w+)", 
        action, re.IGNORECASE
    )
            if table_match:
                table_name = table_match.group(1).lower()
    
    # Extract selected columns
        select_match = re.search(
        r"select\s+(.*?)\s+from", 
        action, re.IGNORECASE
    )
        if select_match:
            selected_cols = select_match.group(1).strip()
            if selected_cols == "*":
            # Use schema to expand columns
                if table_name and table_name in schema:
                 use_cols.extend(schema[table_name]["columns"])
            else:
                cols = [c.split(" as ")[0].split(".")[-1] 
                    for c in selected_cols.split(",")]
                use_cols.extend([c.strip() for c in cols if c.strip()])
    
    # Handle joins (add joined table columns if needed)
            joins = re.findall(r"join\s+(\w+)", action, re.IGNORECASE)
            tables_affected.extend([j.lower() for j in joins])
            
        elif 'insert' in action:
            insert_match = re.match(r"insert\s+into\s+(\w+)\s*(?:\((.*?)\))?", action, re.IGNORECASE)
            if insert_match:
                table = insert_match.group(1)
                cols = insert_match.group(2)
                def_cols = [c.strip().lower() for c in cols.split(',')] if cols else schema.get(table, {}).get('columns', [])
                
                # Handle values clause
                values_match = re.search(r"values\s*\((.*?)\)", action, re.IGNORECASE)
                if values_match:
                    use_cols.extend(re.findall(r"\b\w+\b", values_match.group(1)))
            
        elif 'update' in action:
            set_match = re.search(r"set\s+(.*?)(?:\s+where|$)", action, re.IGNORECASE | re.DOTALL)
            if set_match:
                assignments = re.split(r',\s*(?![^()]*\))', set_match.group(1))
                for assignment in assignments:
                    col = re.match(r"(\w+)\s*=", assignment)
                    if col:
                        def_cols.append(col.group(1).lower())
                    expr = re.sub(r"^\s*\w+\s*=\s*", "", assignment, flags=re.IGNORECASE)
                    use_cols.extend(re.findall(r"\b\w+\b", expr))
            
        elif 'delete' in action:
            use_cols = re.findall(r"\b\w+\b", condition) if condition else []
        
        # Process conditions and joins
        if condition:
            use_cols.extend(re.findall(r"\b\w+\b", condition))
        joins = re.findall(r"join\s+\w+\s+on\s+(.*?)(?:\s+where|\s*$)", action, re.IGNORECASE)
        for join in joins:
            use_cols.extend(re.findall(r"\b\w+\b", join))
        
        # Clean and dedupe
        def_cols = [c for c in def_cols if c not in sql_keywords]
        use_cols = [c for c in use_cols if c not in sql_keywords and not c.isdigit()]
        defined.append(list(dict.fromkeys(def_cols)))
        used.append(list(dict.fromkeys(use_cols)))
        tables_affected.append(table_name)
    
    return used, defined, tables_affected

def create_dependency_matrix(
    used: List[List[str]],
    defined: List[List[str]],
    tables: List[str],
    line_nums: List[int]
) -> Tuple[np.ndarray, int, List[str], int]:
    """Creates dependency matrix based on defined[i] and used[i+1] overlap only."""
    size = len(used)
    matrix = np.zeros((size, size), dtype=int)
    dependencies = []
    pp_count = 0

    for i in range(size - 1):  # Only up to second-last to check i and i+1
       for j in range(i+1,size):
        common_attrs = set(defined[i]) & set(used[j])
        if common_attrs:
            matrix[i][j] = 1
            reason = f"Statement {i+1} defines attributes {common_attrs} used by statement {j+1}"
            dependencies.append(f"Line {line_nums[i]}->{line_nums[j]} (P-P): {reason}")
            pp_count += 1

    return matrix, matrix.sum(), dependencies, pp_count

def main(input_file_path, database_file_path):
    """Main workflow."""
    output_buffer = []

    def buffer_print(text):
        output_buffer.append(str(text))

    # Step 1: Execute the database setup SQL file
    setup_connection = None
    try:
        setup_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password"
        )
        execute_sql_file(setup_connection, database_file_path)
    except Error as e:
        buffer_print(f"Error setting up database: {e}")
        return "\n".join(output_buffer)
    finally:
        if setup_connection and setup_connection.is_connected():
            setup_connection.close()

    # Step 2: Connect to the 'sem6' database
    connection = connect_to_db()
    if not connection:
        buffer_print("Failed to connect to the database.")
        return "\n".join(output_buffer)

    try:
        input_file = input_file_path
        sql_statements, line_numbers = extract_sql_statements(input_file)
        if not sql_statements:
            buffer_print("No SQL statements found in the input file.")
            return "\n".join(output_buffer)

        parsed_results = split_action_and_condition(sql_statements, connection)
        results = split_action_and_condition1(sql_statements)

        # Load schema and extract used/defined variables
        schema = load_schema(database_file_path)
        used, defined, tables = extract_used_and_defined(results, schema)

        # Step 3: Create initial dependency matrix
        matrix, _, _, pp = create_dependency_matrix(used, defined, tables, line_numbers)

        # Step 4: Save the initial matrix before semantic analysis
        initial_matrix = copy.deepcopy(matrix)

        # Step 5: Interval processing
        actions = [result['action'] for result in parsed_results]
        conditions = [result['condition'] for result in parsed_results]
        true_intervals = [result['before_interval'] for result in parsed_results]
        modified_intervals = [result['after_interval'] for result in parsed_results]

        # Step 6: Form semantic-aware dependency matrix
        matrix = form_statement_dependency_matrix(
            actions, conditions, true_intervals, modified_intervals, matrix
        )

        # Step 7: Final analysis/pruning
        updated_matrix, _, _ = dependency_analysis(
            copy.deepcopy(matrix), modified_intervals, true_intervals, parsed_results
        )

        # Step 8: Metrics and comparison
        start_time = time.time()

        initial_np = np.array(initial_matrix)
        updated_np = np.array(updated_matrix)

        # False dependencies: existed initially but removed after semantic analysis
        false_deps_matrix = np.logical_and(initial_np == 1, updated_np == 0)
        false_dependencies = int(np.sum(false_deps_matrix))

        # Dependency counts
        initial_deps = int(initial_np.sum())
        final_deps = int(updated_np.sum())

        # Get dependency pairs
        deps = [
            f"Line {line_numbers[i]} -> Line {line_numbers[j]}"
            for i in range(len(initial_matrix))
            for j in range(len(initial_matrix))
            if initial_matrix[i][j] == 1
        ]

        # False dependency pairs
        false_deps = [
            f"Line {line_numbers[i]} -> Line {line_numbers[j]}"
            for i in range(len(initial_matrix))
            for j in range(len(initial_matrix))
            if ((initial_matrix[i][j]-updated_matrix[i][j] == 1))
        ]

        execution_time = (time.time() - start_time) * 1000
        false_deps_count = max(0,initial_deps - final_deps)
        result_output = f"""
Execution Time: {execution_time:.2f} ms
Database Statements: {len(sql_statements)}
False Dependencies: {false_deps_count}

False Dependency List:
{chr(10).join(false_deps) if false_deps_count>0 else 'No false dependencies found'}
"""
        buffer_print(result_output)

    except Exception as e:
        buffer_print(f"Error during analysis: {str(e)}")
    finally:
        connection.close()

    return "\n".join(output_buffer)


if __name__ == "__main__":  
    input_file_path = input("Enter the SQL input file path: ")
    database_file_path = input("Enter the database file path: ")
    print(main(input_file_path, database_file_path))