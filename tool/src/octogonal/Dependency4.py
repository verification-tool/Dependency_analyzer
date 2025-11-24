import numpy as np
import math
from typing import List, Dict, Tuple, Optional, Set, Any
import mysql.connector
from mysql.connector import Error
import re
import time
import copy
import pandas as pd

def connect_to_db() -> Optional[mysql.connector.MySQLConnection]:
    """Connect to the MySQL database and return the connection object."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="sem6"
        )
        print("Connected to database successfully!")
        return connection
    except Error as err:
        print(f"Error: {err}")
        return None

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
                    # Extract table name from INSERT query
                    insert_match = re.search(r"insert\s+into\s+(\w+)", query, re.IGNORECASE)
                    table_name = insert_match.group(1) if insert_match else None
                    if table_name and last_id is not None:
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
                # Improved table name extraction
                table_name = None
                
                if query.lower().startswith("delete"):
                    # Handle DELETE FROM syntax
                    delete_match = re.search(r"delete\s+from\s+(\w+)", query, re.IGNORECASE)
                    if delete_match:
                        table_name = delete_match.group(1)
                    else:  # Handle DELETE without FROM (non-standard)
                        table_name = query.split()[1] if len(query.split()) > 1 else None
                else:  # UPDATE
                    table_name = query.split()[1] if len(query.split()) > 1 else None
                
                if table_name:
                    where_clause_start = query.lower().find("where")
                    if where_clause_start != -1:  # Has WHERE clause
                        select_query = f"SELECT * FROM {table_name} " + query[where_clause_start:]
                    else:  # No WHERE clause
                        select_query = f"SELECT * FROM {table_name}"
                    
                    print("Fetching affected rows with:", select_query)
                    cursor.execute(select_query)
                    result = cursor.fetchall()
                    print("Query Result (Affected Rows):", result)
                    return result
                else:
                    print("Could not determine table name for affected rows fetch")
            
            print("Query executed successfully.")
            return None
    
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        return None
    
    finally:
        if cursor:
            cursor.close()

def get_table_columns(connection: mysql.connector.MySQLConnection, table: str) -> List[Tuple[str, str]]:
    """Get column names and types for a table"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table}")
        return [(row[0], row[1]) for row in cursor.fetchall()]
    except Error as e:
        print(f"Column fetch error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()

def get_operation_columns(
    connection: mysql.connector.MySQLConnection, 
    action: str, 
    condition: str
) -> Tuple[Set[str], Set[str]]:
    """Extract columns modified by an operation and columns used in conditions."""
    modified_cols = set()
    condition_cols = set()
    
    action_upper = action.upper()
    
    try:
        # Handle UPDATE statements
        if action_upper.startswith("UPDATE"):
            set_match = re.search(r"SET\s+(.*?)(\s+WHERE|$)", action, re.IGNORECASE)
            if set_match:
                assignments = [a.strip() for a in set_match.group(1).split(',')]
                for assign in assignments:
                    col = assign.split('=')[0].strip()
                    modified_cols.add(col)

        # Handle INSERT statements
        elif action_upper.startswith("INSERT"):
            insert_match = re.search(r"INSERT\s+INTO\s+\w+\s*\((.*?)\)", action, re.IGNORECASE)
            if insert_match:
                modified_cols.update([col.strip() for col in insert_match.group(1).split(',')])

        # Handle DELETE statements
        elif action_upper.startswith("DELETE"):
            table_match = re.search(r"FROM\s+(\w+)", action, re.IGNORECASE)
            if table_match:
                table_cols = get_table_columns(connection, table_match.group(1))
                modified_cols = set([col[0] for col in table_cols])  # Get column names only

        # Extract condition columns
        if condition:
            condition_cols.update(re.findall(r"\b([a-zA-Z_]\w*)\b", condition))
            
    except Exception as e:
        print(f"Error extracting columns: {e}")
    
    return modified_cols, condition_cols

def is_numeric_type(data_type: str) -> bool:
    """Check if SQL data type is numeric."""
    return any(t in data_type.lower() for t in ['int', 'float', 'double', 'decimal', 'real'])

def is_numeric(val):
    """Check if a value is numeric."""
    try:
        float(val)
        return True
    except:
        return False

def rows_to_octagon_constraints(rows, col_names: List[str]) -> Tuple[List[Tuple[str, int, str, int, float]], List[str]]:
    """Convert numeric data rows directly into Octagon domain constraints."""
    if not rows:
        return [], []
    
    sample_row = rows[0]
    if isinstance(sample_row, dict):
        numeric_col_names = [k for k, v in sample_row.items() if is_numeric(v)]
    else:
        numeric_col_names = [col_names[i] for i in range(min(len(sample_row), len(col_names))) 
                           if is_numeric(sample_row[i])]

    if not numeric_col_names:
        return [], []
    
    # Extract numeric points from rows
    points = []
    for row in rows:
        try:
            if isinstance(row, dict):
                point = [float(row[col]) for col in numeric_col_names if col in row]
            else:
                point = []
                for i, col in enumerate(numeric_col_names):
                    col_idx = col_names.index(col) if col in col_names else i
                    if col_idx < len(row):
                        point.append(float(row[col_idx]))
                    
            if len(point) == len(numeric_col_names) and all(not math.isnan(v) for v in point):
                points.append(point)
        except (ValueError, TypeError, IndexError):
            continue

    if not points:
        return [], numeric_col_names

    constraints = []
    num_vars = len(numeric_col_names)
    
    # Generate octagon constraints directly from data points
    print(f"Generating octagon constraints from {len(points)} points with {num_vars} variables")
    
    # Single variable constraints
    for i in range(num_vars):
        values = [p[i] for p in points]
        min_val = min(values)
        max_val = max(values)
        
        # x_i <= max_val (constraint: +x_i +x_i <= 2*max_val)
        constraints.append((numeric_col_names[i], +1, numeric_col_names[i], +1, 2 * max_val))
        
        # x_i >= min_val (constraint: -x_i -x_i <= -2*min_val)
        constraints.append((numeric_col_names[i], -1, numeric_col_names[i], -1, -2 * min_val))
    
    # Two variable constraints
    for i in range(num_vars):
        for j in range(num_vars):
            if i != j:
                # x_i + x_j <= max(data)
                vsum = [p[i] + p[j] for p in points]
                constraints.append((numeric_col_names[i], +1, numeric_col_names[j], +1, max(vsum)))
                
                # x_i - x_j <= max(data)
                vdiff = [p[i] - p[j] for p in points]
                constraints.append((numeric_col_names[i], +1, numeric_col_names[j], -1, max(vdiff)))
                
                # -x_i + x_j <= max(data)
                vdiff_rev = [-p[i] + p[j] for p in points]
                constraints.append((numeric_col_names[i], -1, numeric_col_names[j], +1, max(vdiff_rev)))
                
                # -x_i - x_j <= max(data)
                vsum_neg = [-p[i] - p[j] for p in points]
                constraints.append((numeric_col_names[i], -1, numeric_col_names[j], -1, max(vsum_neg)))

    return constraints, numeric_col_names

def initialize_cdbm(variable_count: int) -> Tuple[np.ndarray, List[str]]:
    """Initialize a CDBM matrix for a given number of variables."""
    var_names = []
    for i in range(1, variable_count + 1):
        var_names.extend([f"x{i}+", f"x{i}-"])
    
    n = len(var_names)
    cdbm = np.full((n, n), np.inf)
    np.fill_diagonal(cdbm, 0.0)
    return cdbm, var_names

def build_octagon_from_constraints(constraints: List[Tuple[str, int, str, int, float]], variables: List[str]) -> List[List[float]]:
    """Build octagon DBM directly from octagon constraints."""
    if not constraints or not variables:
        return []
    
    variable_count = len(variables)
    cdbm, var_names = initialize_cdbm(variable_count)
    var_map = {name: idx for idx, name in enumerate(var_names)}
    
    # Convert octagon constraints to CDBM format
    for constraint in constraints:
        var1, sign1, var2, sign2, value = constraint
        
        # Map variable names to indices
        var1_idx = None
        var2_idx = None
        for i, var in enumerate(variables):
            if var == var1:
                var1_idx = i + 1  # 1-indexed for x1, x2, etc.
            if var == var2:
                var2_idx = i + 1
        
        if var1_idx is None or var2_idx is None:
            continue
            
        # Convert to CDBM constraints based on octagon constraint type
        if sign1 == 1 and sign2 == 1:  # x + y <= c
            # x+ - y- <= c and y+ - x- <= c
            cdbm_var1_pos = f"x{var1_idx}+"
            cdbm_var1_neg = f"x{var1_idx}-"
            cdbm_var2_pos = f"x{var2_idx}+"
            cdbm_var2_neg = f"x{var2_idx}-"
            
            if cdbm_var2_neg in var_map and cdbm_var1_pos in var_map:
                i = var_map[cdbm_var2_neg]
                j = var_map[cdbm_var1_pos]
                cdbm[i][j] = min(cdbm[i][j], value)
            
            if var1_idx != var2_idx:  # Avoid self-constraints
                if cdbm_var1_neg in var_map and cdbm_var2_pos in var_map:
                    i = var_map[cdbm_var1_neg]
                    j = var_map[cdbm_var2_pos]
                    cdbm[i][j] = min(cdbm[i][j], value)
                
        elif sign1 == 1 and sign2 == -1:  # x - y <= c
            cdbm_var1_pos = f"x{var1_idx}+"
            cdbm_var1_neg = f"x{var1_idx}-"
            cdbm_var2_pos = f"x{var2_idx}+"
            cdbm_var2_neg = f"x{var2_idx}-"
            
            if cdbm_var2_pos in var_map and cdbm_var1_pos in var_map:
                i = var_map[cdbm_var2_pos]
                j = var_map[cdbm_var1_pos]
                cdbm[i][j] = min(cdbm[i][j], value)
            
            if var1_idx != var2_idx:
                if cdbm_var1_neg in var_map and cdbm_var2_neg in var_map:
                    i = var_map[cdbm_var1_neg]
                    j = var_map[cdbm_var2_neg]
                    cdbm[i][j] = min(cdbm[i][j], value)
                
        elif sign1 == -1 and sign2 == 1:  # -x + y <= c
            cdbm_var1_pos = f"x{var1_idx}+"
            cdbm_var1_neg = f"x{var1_idx}-"
            cdbm_var2_pos = f"x{var2_idx}+"
            cdbm_var2_neg = f"x{var2_idx}-"
            
            if cdbm_var1_pos in var_map and cdbm_var2_pos in var_map:
                i = var_map[cdbm_var1_pos]
                j = var_map[cdbm_var2_pos]
                cdbm[i][j] = min(cdbm[i][j], value)
            
            if var1_idx != var2_idx:
                if cdbm_var2_neg in var_map and cdbm_var1_neg in var_map:
                    i = var_map[cdbm_var2_neg]
                    j = var_map[cdbm_var1_neg]
                    cdbm[i][j] = min(cdbm[i][j], value)
                
        elif sign1 == -1 and sign2 == -1:  # -x - y <= c
            cdbm_var1_pos = f"x{var1_idx}+"
            cdbm_var1_neg = f"x{var1_idx}-"
            cdbm_var2_pos = f"x{var2_idx}+"
            cdbm_var2_neg = f"x{var2_idx}-"
            
            if cdbm_var1_pos in var_map and cdbm_var2_neg in var_map:
                i = var_map[cdbm_var1_pos]
                j = var_map[cdbm_var2_neg]
                cdbm[i][j] = min(cdbm[i][j], value)
            
            if var1_idx != var2_idx:
                if cdbm_var2_pos in var_map and cdbm_var1_neg in var_map:
                    i = var_map[cdbm_var2_pos]
                    j = var_map[cdbm_var1_neg]
                    cdbm[i][j] = min(cdbm[i][j], value)
    
    # Apply Floyd-Warshall closure
    closed_dbm = dbm_closure(cdbm.tolist())
    return closed_dbm

def dbm_closure(dbm: List[List[float]]) -> List[List[float]]:
    """Apply Floyd-Warshall algorithm for DBM closure."""
    n = len(dbm)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dbm[i][k] + dbm[k][j] < dbm[i][j]:
                    dbm[i][j] = dbm[i][k] + dbm[k][j]
    return dbm

def parse_condition_to_octagon_constraints(
    condition: str,
    columns: List[str]
) -> Tuple[List[Tuple[str, int, str, int, float]], List[str]]:
    """Convert condition string directly into octagon constraints."""
    constraints = []
    numeric_columns = []

    if not condition:
        return [], []

    and_conditions = re.split(r'\s+AND\s+', condition, flags=re.IGNORECASE)

    for cond in and_conditions:
        cond = re.sub(r'\s+', ' ', cond.strip())
        match = re.match(r"\(*(.+?)\)*\s*(=|<=?|>=?|!=)\s*([\d\.]+)", cond, re.IGNORECASE)
        if not match:
            continue
        
        lhs, op, rhs = match.groups()
        rhs_val = float(rhs)

        # Parse left-hand side for variables and coefficients
        terms = re.findall(r'[+-]?\s*\d*\.?\d*\s*\*?\s*[a-zA-Z_]\w*', lhs)
        var_coeffs = {}

        for term in terms:
            term = term.replace(' ', '')
            if '*' in term:
                coeff_str, var = term.split('*')
                coeff = float(coeff_str) if coeff_str not in ('', '+', '-') else float(f"{coeff_str}1")
            else:
                var = term.lstrip('+-')
                coeff_str = term[:len(term)-len(var)]
                coeff = -1.0 if coeff_str.startswith('-') else 1.0

            if var in columns:
                var_coeffs[var] = var_coeffs.get(var, 0) + coeff
                if var not in numeric_columns:
                    numeric_columns.append(var)

        # Convert to octagon constraints based on the number of variables
        vars_with_coeffs = [(var, coeff) for var, coeff in var_coeffs.items() if abs(coeff) > 1e-8]
        
        if len(vars_with_coeffs) == 1:  # Single variable constraint
            var, coeff = vars_with_coeffs[0]
            if op in ("<", "<="):
                if coeff > 0:  # ax <= b -> x <= b/a
                    bound = rhs_val / coeff
                    constraints.append((var, 1, var, 1, 2 * bound))
                else:  # -ax <= b -> x >= -b/a
                    bound = -rhs_val / coeff
                    constraints.append((var, -1, var, -1, -2 * bound))
            elif op in (">", ">="):
                if coeff > 0:  # ax >= b -> x >= b/a
                    bound = rhs_val / coeff
                    constraints.append((var, -1, var, -1, -2 * bound))
                else:  # -ax >= b -> x <= -b/a
                    bound = -rhs_val / coeff
                    constraints.append((var, 1, var, 1, 2 * bound))
                    
        elif len(vars_with_coeffs) == 2:  # Two variable constraint
            (var1, coeff1), (var2, coeff2) = vars_with_coeffs
            if op in ("<", "<="):
                # Convert ax + by <= c to octagon form
                if coeff1 == 1 and coeff2 == 1:  # x + y <= c
                    constraints.append((var1, 1, var2, 1, rhs_val))
                elif coeff1 == 1 and coeff2 == -1:  # x - y <= c
                    constraints.append((var1, 1, var2, -1, rhs_val))
                elif coeff1 == -1 and coeff2 == 1:  # -x + y <= c
                    constraints.append((var1, -1, var2, 1, rhs_val))
                elif coeff1 == -1 and coeff2 == -1:  # -x - y <= c
                    constraints.append((var1, -1, var2, -1, rhs_val))
            elif op in (">", ">="):
                # Convert ax + by >= c to octagon form by negating
                if coeff1 == 1 and coeff2 == 1:  # x + y >= c -> -x - y <= -c
                    constraints.append((var1, -1, var2, -1, -rhs_val))
                elif coeff1 == 1 and coeff2 == -1:  # x - y >= c -> -x + y <= -c
                    constraints.append((var1, -1, var2, 1, -rhs_val))
                elif coeff1 == -1 and coeff2 == 1:  # -x + y >= c -> x - y <= -c
                    constraints.append((var1, 1, var2, -1, -rhs_val))
                elif coeff1 == -1 and coeff2 == -1:  # -x - y >= c -> x + y <= -c
                    constraints.append((var1, 1, var2, 1, -rhs_val))

    return constraints, numeric_columns

def split_action_and_condition(sql_statements: List[str], connection: mysql.connector.MySQLConnection) -> List[Dict]:
    """Analyze SQL statements using octagon domain directly."""
    results = []
    
    for statement in sql_statements:
        where_match = re.search(r"\bwhere\b\s+(.*)", statement, re.IGNORECASE)
        action = statement[:where_match.start()].strip() if where_match else statement.strip()
        condition = where_match.group(1).strip().rstrip(';') if where_match else None
        
        # Extract table name and get column information
        table_match = re.search(r"\b(?:UPDATE|FROM|INTO)\s+([\w.]+)", action, re.IGNORECASE)
        table_name = table_match.group(1) if table_match else None
        columns = get_table_columns(connection, table_name) if table_name else []
        numeric_col_names = [name for name, dtype in columns if is_numeric_type(dtype)]
        
        # Get modified and condition columns
        modified_cols, condition_cols = get_operation_columns(connection, action, condition)
        
        # Parse condition to octagon constraints
        cond_constraints, cond_vars = parse_condition_to_octagon_constraints(condition, numeric_col_names) if condition else ([], [])
        cond_oct = build_octagon_from_constraints(cond_constraints, cond_vars) if cond_constraints else None
        
        # Extract data and build octagons
        true_part, modified_part, false_part = extract_true_modified_false(connection, action, condition)
        
        true_constraints, true_vars = rows_to_octagon_constraints(true_part, numeric_col_names)
        true_oct = build_octagon_from_constraints(true_constraints, true_vars) if true_constraints else None
        
        mod_constraints, mod_vars = rows_to_octagon_constraints(modified_part, numeric_col_names)
        mod_oct = build_octagon_from_constraints(mod_constraints, mod_vars) if mod_constraints else None
        
        results.append({
            "action": action,
            "condition": condition,
            "true_octagon": true_oct,
            "modified_octagon": mod_oct,
            "condition_octagon": cond_oct,
            "modified_part": modified_part,
            "true_part": true_part,
            "numeric_columns": numeric_col_names
        })
    
    return results

def extract_true_modified_false(
    connection: mysql.connector.MySQLConnection, action: str, condition: str
) -> Tuple[List, List, List]:
    """Extract true, modified, and false parts of a SQL statement."""
    true_part = []
    modified_part = []
    false_part = []

    table_match = re.search(r"(?:UPDATE|FROM|INSERT INTO)\s+([\w.]+)", action, re.IGNORECASE)
    if not table_match:
        return true_part, modified_part, false_part
    table_name = table_match.group(1)

    has_condition = condition and condition.strip() != ""

    if action.upper().startswith("UPDATE"):
        true_query = (
            f"SELECT * FROM {table_name} WHERE {condition}"
            if has_condition
            else f"SELECT * FROM {table_name}"
        )
        true_part = execute_sql_query(connection, true_query) or []

        update_query = f"{action} WHERE {condition}" if has_condition else action
        execute_sql_query(connection, update_query)

        modified_part = execute_sql_query(connection, true_query) or []

        if has_condition:
            false_query = f"SELECT * FROM {table_name} WHERE NOT ({condition})"
            false_part = execute_sql_query(connection, false_query) or []
    
    elif action.upper().startswith("INSERT"):
        false_query = f"SELECT * FROM {table_name}"
        false_part = execute_sql_query(connection, false_query) or []

        cursor = connection.cursor()
        cursor.execute(action)
        last_id = cursor.lastrowid
        connection.commit()

        if last_id is not None:
            true_query = f"SELECT * FROM {table_name} WHERE id = {last_id}"
            true_part = execute_sql_query(connection, true_query) or []
        else:
            after_query = f"SELECT * FROM {table_name}"
            after_insert = execute_sql_query(connection, after_query) or []
            true_part = [row for row in after_insert if row not in false_part]
        modified_part = true_part.copy()

    elif action.upper().startswith("SELECT"):
        if has_condition:
            true_query = f"SELECT * FROM {table_name} WHERE {condition}"
            false_query = f"SELECT * FROM {table_name} WHERE NOT ({condition})"
        else:
            true_query = f"SELECT * FROM {table_name}"
            false_query = None

        true_part = execute_sql_query(connection, true_query) or []
        false_part = execute_sql_query(connection, false_query) or [] if false_query else []

    return true_part, modified_part, false_part

def check_consecutive_dependencies(matrix, results):
    """Check dependencies between consecutive statements using octagon analysis."""
    n = len(results)
    
    if isinstance(matrix, np.ndarray):
        refined_matrix = matrix.copy().tolist()
    else:
        refined_matrix = [list(row) if not isinstance(row, list) else row[:] for row in matrix]
    
    print("\n=== Consecutive Dependency Check (Column-Aware) ===")
    
    for i in range(n-1):
        j = i + 1
        
        print(f"\nS{i+1} -> S{j+1}: ", end="")
        
        # Get the actual columns modified and used
        action_i = results[i].get("action", "")
        condition_j = results[j].get("condition", "")
        action_j = results[j].get("action", "")
        
        # Extract modified columns from S_i
        modified_cols_i = set()
        if "SET" in action_i.upper():
            set_match = re.search(r"SET\s+(.*?)(?:\s+WHERE|$)", action_i, re.IGNORECASE)
            if set_match:
                assignments = set_match.group(1).split(',')
                for assign in assignments:
                    col = assign.split('=')[0].strip().lower()
                    modified_cols_i.add(col)
        
        # Extract columns used by S_j (in condition and SET RHS)
        used_cols_j = set()
        
        # From condition
        if condition_j:
            used_cols_j.update(re.findall(r'\b([a-zA-Z_]\w*)\b', condition_j.lower()))
        
        # From SET clause RHS
        if "SET" in action_j.upper():
            set_match = re.search(r"SET\s+(.*?)(?:\s+WHERE|$)", action_j, re.IGNORECASE)
            if set_match:
                assignments = set_match.group(1).split(',')
                for assign in assignments:
                    if '=' in assign:
                        lhs, rhs = assign.split('=', 1)
                        # Only take columns from RHS (what's being read)
                        used_cols_j.update(re.findall(r'\b([a-zA-Z_]\w*)\b', rhs.lower()))
                        # Remove the LHS column (what's being written)
                        used_cols_j.discard(lhs.strip().lower())
        
        # Remove SQL keywords
        sql_keywords = {'and', 'or', 'not', 'in', 'like', 'between', 'is', 'null', 'true', 'false', 'where', 'set'}
        modified_cols_i -= sql_keywords
        used_cols_j -= sql_keywords
        
        print(f"Modified by S{i+1}: {modified_cols_i}, Used by S{j+1}: {used_cols_j}")
        
        # Check for COLUMN overlap (syntactic dependency)
        column_overlap = modified_cols_i & used_cols_j
        
        if refined_matrix[i][j] == 0:
            # Try to add dependency only if there's column overlap
            if column_overlap:
                print(f"Column overlap {column_overlap} - checking octagon...")
                
                mod_i = results[i].get("modified_octagon")
                cond_j = results[j].get("condition_octagon")
                mod_j = results[j].get("modified_octagon")
                
                should_add = False
                if mod_i and cond_j and octagon_intersects(mod_i, cond_j):
                    should_add = True
                    print(f"Octagon intersection confirmed - ADDED")
                elif mod_i and mod_j and octagon_intersects(mod_i, mod_j):
                    should_add = True
                    print(f"Octagon intersection confirmed - ADDED")
                
                if should_add:
                    refined_matrix[i][j] = 1
                else:
                    print(f"No octagon intersection - NOT ADDED")
            else:
                print(f"No column overlap - NOT ADDED")
        
        else:
            # Verify existing dependency
            if column_overlap:
                print(f"Column overlap {column_overlap} - KEPT")
            else:
                print(f"No column overlap - REMOVED (false positive)")
                refined_matrix[i][j] = 0
    
    print(f"\nRefined matrix after consecutive check: {refined_matrix}")
    return refined_matrix

def dependency_analysis_octagon(
    matrix: List[List[int]], 
    results: List[Dict]
) -> Tuple[List[List[int]], List, List[List[int]]]:
    """Refine dependency matrix using octagon-based analysis."""
    print("\nOctagon-based Dependency Analysis")
    n = len(matrix)
    initial_matrix = [row.copy() for row in matrix]

    for i in range(n - 2):
        for j in range(i + 2, n):
            if matrix[i][j] != 0 and i + 1 < len(results) and j < len(results):
                mod_i = results[i].get("modified_octagon", None)
                mod_i1 = results[i+1].get("modified_octagon", None)
                mod_j = results[j].get("modified_octagon", None)
                true_i = results[i].get("condition_octagon", None)

                if mod_i is None or mod_i1 is None or mod_j is None:
                    continue

                # Condition 1: If mod_i ⊆ mod_{i+1}, remove dependency
                if octagon_subset(mod_i, mod_i1):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (octagon subset condition 1)")
                    continue

                # Condition 2: If mod_j ⊆ mod_{i+1}, remove dependency  
                if octagon_subset(mod_j, mod_i1):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (octagon subset condition 2)")
                    continue

                # More complex conditions for multi-step dependencies
                if j > i + 1:
                    mod_j1 = results[j-1].get("modified_octagon", None)
                    true_j = results[j].get("condition_octagon", None)
                    true_j1 = results[j-1].get("condition_octagon", None)

                    if all(x is not None for x in [mod_j1, true_j, true_j1, true_i]):
                        # Check if octagon constraints eliminate dependency
                        X = intersection_complement_oct(true_j1, true_j)
                        Y = intersection_complement_oct(mod_j1, mod_j)
                        combined = convex_hull_oct(true_i, mod_i)

                        if not octagon_intersects(X, combined) and not octagon_intersects(Y, combined):
                            matrix[i][j] = 0
                            print(f"Removed {i}->{j} (octagon intersection condition)")
                        else:
                            matrix[i][j] = 1
                            print(f"Kept {i}->{j} (octagon dependency confirmed)")

    return matrix, [], initial_matrix

def octagon_subset(dbm1: List[List[float]], dbm2: List[List[float]]) -> bool:
    """Check if octagon dbm1 is a subset of octagon dbm2."""
    if not dbm1 or not dbm2 or len(dbm1) != len(dbm2):
        return False
        
    # Apply closure to both DBMs
    closed_dbm1 = dbm_closure([row[:] for row in dbm1])
    closed_dbm2 = dbm_closure([row[:] for row in dbm2])
    
    # dbm1 ⊆ dbm2 iff for all constraints (i,j): dbm1[i][j] >= dbm2[i][j]
    # (tighter constraints in dbm1 mean smaller feasible region)
    for i in range(len(closed_dbm1)):
        for j in range(len(closed_dbm1)):
            if closed_dbm1[i][j] > closed_dbm2[i][j]:
                return False
    return True

def octagon_intersects(dbm1: List[List[float]], dbm2: List[List[float]]) -> bool:
    """Check if the intersection of two octagons is feasible."""
    if not dbm1 or not dbm2 or len(dbm1) != len(dbm2):
        return False
        
    n = len(dbm1)
    # Intersection: take minimum of corresponding constraints
    merged = [[min(dbm1[i][j], dbm2[i][j]) for j in range(n)] for i in range(n)]
    merged = dbm_closure(merged)
    
    # Check for inconsistency (negative cycle)
    for i in range(n):
        if merged[i][i] < 0:
            return False
    return True

def convex_hull_oct(dbm1: List[List[float]], dbm2: List[List[float]]) -> List[List[float]]:
    """Compute the convex hull of two octagons."""
    if not dbm1 or not dbm2 or len(dbm1) != len(dbm2):
        return dbm1 or dbm2 or []
        
    n = len(dbm1)
    # Convex hull: take maximum of corresponding constraints (weaker bounds)
    hull = [[max(dbm1[i][j], dbm2[i][j]) for j in range(n)] for i in range(n)]
    return dbm_closure(hull)

def intersection_complement_oct(dbm_A: List[List[float]], dbm_B: List[List[float]]) -> List[List[float]]:
    """Approximate the intersection of octagon A and the complement of octagon B."""
    if not dbm_A or not dbm_B or len(dbm_A) != len(dbm_B):
        return dbm_A or []
        
    n = len(dbm_A)
    # Rough approximation: use constraints from A but weaken those that are also in B
    approx = [[dbm_A[i][j] for j in range(n)] for i in range(n)]
    
    for i in range(n):
        for j in range(n):
            if dbm_B[i][j] < float('inf'):
                # If B has a constraint, weaken it in the result
                approx[i][j] = max(approx[i][j], dbm_B[i][j] + 1.0)
    
    return dbm_closure(approx)

def bellman_ford_octagon(dbm: List[List[float]]) -> bool:
    """Check if an octagon DBM is consistent using Bellman-Ford algorithm."""
    if not dbm:
        return True
        
    n = len(dbm)
    distance = [float('inf')] * n
    distance[0] = 0  # Start from first node
    
    # Relax edges n-1 times
    for _ in range(n - 1):
        updated = False
        for u in range(n):
            for v in range(n):
                if dbm[u][v] != float('inf') and distance[u] != float('inf'):
                    new_dist = distance[u] + dbm[u][v]
                    if new_dist < distance[v]:
                        distance[v] = new_dist
                        updated = True
        if not updated:
            break
    
    # Check for negative cycles
    for u in range(n):
        for v in range(n):
            if dbm[u][v] != float('inf') and distance[u] != float('inf'):
                if distance[u] + dbm[u][v] < distance[v]:
                    return False  # Negative cycle detected
    
    return True  # No negative cycle

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

def main(input_file_path: str, database_file_path: str) -> str:
   
    output_buffer = []

    def buffer_print(text):
        output_buffer.append(str(text))

    conn = connect_to_db()
    if not conn:
        buffer_print("Failed to connect to the database.")
        return "\n".join(output_buffer)

    try:
        # Step 1: Setup database
        execute_sql_file(conn, database_file_path)

        # Step 2: Extract SQL statements
        sql_statements, line_numbers = extract_sql_statements(input_file_path)
        buffer_print(f"Extracted {len(sql_statements)} SQL statements")

        if not sql_statements:
            buffer_print("No SQL statements found.")
            return "\n".join(output_buffer)

        # Step 3: Parse and analyze
        start_time = time.time()
        results = split_action_and_condition(sql_statements, conn)
        
        parsed = split_action_and_condition1(sql_statements)

        # Step 4: Load schema and extract used/defined
        schema = load_schema(database_file_path)
        
        used, defined, tables = extract_used_and_defined(parsed, schema)
        
        # Step 5: Build initial dependency matrix (syntactic)
        initial_matrix, _, _, pp = create_dependency_matrix(used, defined, tables, line_numbers)
        original_initial_matrix = copy.deepcopy(initial_matrix)
        
        # Step 6: Refine dependencies using Octagon
        working_matrix = copy.deepcopy(initial_matrix)
        matrix1 = check_consecutive_dependencies(working_matrix, results)
        updated_matrix, _, _ = dependency_analysis_octagon(copy.deepcopy(matrix1), results)

        # Step 7: Metrics
        initial_np = np.array(original_initial_matrix)
        updated_np = np.array(updated_matrix)

        false_deps_matrix = np.logical_and(initial_np == 1, updated_np == 0)
        false_dependencies = int(np.sum(false_deps_matrix))

        execution_time = (time.time() - start_time) * 1000  # ms
        initial_dep_count = int(initial_np.sum())
        final_dep_count = int(updated_np.sum())

        # Step 8: Dependency and false dependency list
        deps = [
            f"Line {line_numbers[i]} -> Line {line_numbers[j]}"
            for i in range(len(original_initial_matrix))
            for j in range(len(original_initial_matrix))
            if original_initial_matrix[i][j] == 1
        ]

        false_deps = [
            f"Line {line_numbers[i]} -> Line {line_numbers[j]}"
            for i in range(len(original_initial_matrix))
            for j in range(len(original_initial_matrix))
            if original_initial_matrix[i][j] == 1 and updated_matrix[i][j] == 0
        ]

        # Step 9: Final Report
        result_output = f"""
### Dependency Analysis Results (Octagon Domain)
Initial Dependencies: {initial_dep_count}
False Dependencies: {false_dependencies}

Execution Time: {execution_time:.2f} ms
Database Statements: {len(sql_statements)}


False Dependency List:
{chr(10).join(false_deps) if false_deps else 'No false dependencies found'}
"""
        buffer_print(result_output)

    except Exception as e:
        buffer_print(f"Error during analysis: {str(e)}")

    finally:
        conn.close()

    return "\n".join(output_buffer)

# Ensure this is guarded to run as script
if __name__ == "__main__":
    input_file_path = input("Enter the SQL input file path: ")
    database_file_path = input("Enter the database setup file path: ")
    print(main(input_file_path, database_file_path))

