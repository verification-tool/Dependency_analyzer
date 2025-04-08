import numpy as np
import math
from typing import List, Dict, Tuple, Optional , Set,Any
from scipy.optimize import linprog
import mysql.connector
from mysql.connector import Error
import re
from scipy.spatial import ConvexHull
import time as time
import copy

def connect_to_db() -> Optional[mysql.connector.MySQLConnection]:
    """Connect to the MySQL database and return the connection object."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_mysql_password",
            database="your_db_name"
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
                modified_cols = set(get_table_columns(connection, table_match.group(1))[0] ) # Get column names only

        # Extract condition columns
        if condition:
            condition_cols.update(re.findall(r"\b([a-zA-Z_]\w*)\b", condition))
            
    except Exception as e:
        print(f"Error extracting columns: {e}")
    
    return modified_cols, condition_cols

def is_numeric_type(data_type: str) -> bool:
    """Check if SQL data type is numeric"""
    return any(t in data_type.lower() for t in ['int', 'float', 'double', 'decimal', 'real'])

def rows_to_inequalities(rows, numeric_col_indices: List[int]) -> Tuple[Tuple[List[List[float]], List[float]], List[int]]:
    """Convert database rows to polyhedron inequalities using schema-based numeric columns"""
    if not rows:
        return ([], []), []
    
    points = []
    for row in rows:
        try:
            point = []
            for idx in numeric_col_indices:
                value = row[idx]
                if value is None:
                    raise ValueError(f"NULL value in numeric column at index {idx}")
                point.append(float(value))
            if all(not math.isnan(v) for v in point):
                points.append(point)
        except (TypeError, ValueError, IndexError) as e:
            continue  # Silently skip invalid rows
    
    if not points:
        return ([], []), numeric_col_indices
    
    A, b = _points_to_inequalities(points)
    return (A, b), numeric_col_indices

def parse_condition_to_inequalities(
    condition: str, 
    columns: List[str]
) -> Tuple[List[List[float]], List[float]]:
    inequalities = []
    constants = []
    
    and_conditions = re.split(r'\s+AND\s+', condition, flags=re.IGNORECASE)
    
    for cond in and_conditions:
        cond = re.sub(r'\s+', ' ', cond.strip())  # Normalize whitespace
        
        # Split into left-hand side (LHS) and right-hand side (RHS)
        match = re.match(
            r"\(*(.+?)\)*\s*(=|<=?|>=?|!=)\s*([\d\.]+)", 
            cond, 
            re.IGNORECASE
        )
        if not match:
            continue
            
        lhs, op, rhs = match.groups()
        rhs_val = float(rhs)
        
        # Parse LHS into coefficients (e.g., "cost + 0.2*duration" → {"cost": 1.0, "duration": 0.2})
        terms = re.findall(r'([+-]?[\d\.]*\*?[a-zA-Z_]\w*|\b[a-zA-Z_]\w*\b)', lhs)
        coeffs = {}
        for term in terms:
            term = term.replace(' ', '')
            if '*' in term:
                coeff_part, col_part = term.split('*', 1)
                coeff = float(coeff_part) if coeff_part not in ['+', '-', ''] else 1.0
                if col_part not in columns:
                    continue
                coeffs[col_part] = coeffs.get(col_part, 0.0) + coeff
            else:
                col = term.lstrip('+-')
                if col not in columns:
                    continue
                sign = -1.0 if term.startswith('-') else 1.0
                coeffs[col] = coeffs.get(col, 0.0) + sign * 1.0
        
        if not coeffs:
            continue  # No valid columns in expression
            
        # Convert coefficients to a row in A
        row = [0.0] * len(columns)
        for col, coeff in coeffs.items():
            try:
                idx = columns.index(col)
                row[idx] = coeff
            except ValueError:
                continue
        
        # Handle operators
        if op == ">":
            row = [-x for x in row]
            constants.append(-rhs_val)
        elif op == ">=":
            row = [-x for x in row]
            constants.append(-rhs_val + 1e-9)
        elif op == "<":
            constants.append(rhs_val)
        elif op == "<=":
            constants.append(rhs_val + 1e-9)
        elif op == "=":
            constants.append(rhs_val + 1e-6)
            inequalities.append(row.copy())
            row = [-x for x in row]
            constants.append(-rhs_val + 1e-6)
        
        inequalities.append(row)
    
    return inequalities, constants

def _points_to_inequalities(points: List[List[float]]) -> Tuple[List[List[float]], List[float]]:
    """Handle small datasets with bounding boxes."""
    if len(points) < 1:
        return [], []
    
    # Use bounding box if <= 3 dimensions or few points
    if len(points[0]) <= 3 or len(points) <= len(points[0]) + 1:
        return _bounding_box_inequalities(points)
    
    try:
        hull = ConvexHull(np.array(points))
        return hull.equations[:, :-1].tolist(), (-hull.equations[:, -1]).tolist()
    except:
        return _bounding_box_inequalities(points)

def _bounding_box_inequalities(points: List[List[float]]) -> Tuple[List[List[float]], List[float]]:
    """Create bounding box constraints"""
    pts = np.array(points)
    A = []
    b = []
    
    for dim in range(pts.shape[1]):
        # Lower bound: -x <= -min
        A.append([-1.0 if i == dim else 0.0 for i in range(pts.shape[1])])
        b.append(-np.min(pts[:, dim]))
        
        # Upper bound: x <= max
        A.append([1.0 if i == dim else 0.0 for i in range(pts.shape[1])])
        b.append(np.max(pts[:, dim]))
    
    return A, b

def project_to_columns(
    A: List[List[float]], 
    b: List[float], 
    original_columns: List[str], 
    target_columns: Set[str]
) -> Tuple[List[List[float]], List[float]]:
    """Project polyhedron (A, b) onto the subset of target_columns."""
    projected_A = []
    projected_b = []
    
    # Get column indices and order for projection
    target_indices = [i for i, col in enumerate(original_columns) if col in target_columns]
    projected_columns = [col for col in original_columns if col in target_columns]
    
    for a_row, b_val in zip(A, b):
        non_zero = [i for i, coeff in enumerate(a_row) if coeff != 0]
        if len(non_zero) != 1:
            continue  # Skip multi-column inequalities (axis-aligned only)
        col_idx = non_zero[0]
        if original_columns[col_idx] in target_columns:
            proj_row = [0.0] * len(projected_columns)
            proj_row[projected_columns.index(original_columns[col_idx])] = a_row[col_idx]
            projected_A.append(proj_row)
            projected_b.append(b_val)
    
    return projected_A, projected_b

def project_polyhedron(
    A: List[List[float]], 
    b: List[float],
    original_cols: List[str], 
    target_cols: Set[str]
) -> Tuple[List[List[float]], List[float]]:
    """Projects polyhedron onto target columns using Fourier-Motzkin elimination."""
    if not A or not original_cols:
        return [], []
    
    # Keep track of active column indices
    active_indices = list(range(len(original_cols)))

    # Eliminate variables not in target_cols
    for col in original_cols:
        if col not in target_cols:
            elim_idx = active_indices.index(original_cols.index(col))
            A, b = fourier_motzkin_eliminate(A, b, elim_idx)
            active_indices.pop(elim_idx)  # Remove the eliminated index
    
    # Retain only target columns
    proj_A = [[row[i] for i in active_indices] for row in A]
    return proj_A, b

def fourier_motzkin_eliminate(A: List[List[float]], b: List[float], elim_idx: int) -> Tuple[List[List[float]], List[float]]:
    """Eliminates a variable using Fourier-Motzkin elimination."""
    pos, neg, other = [], [], []

    # Classify constraints based on elimination variable
    for a_row, b_val in zip(A, b):
        coeff = a_row[elim_idx]
        if math.isclose(coeff, 0, abs_tol=1e-9):
            other.append((a_row, b_val))
        elif coeff > 0:
            pos.append((a_row, b_val, coeff))
        else:
            neg.append((a_row, b_val, coeff))
    
    new_A, new_b = [], []

    # Constraints without the eliminated variable
    new_A.extend([row[:elim_idx] + row[elim_idx+1:] for row, _ in other])
    new_b.extend(b_val for _, b_val in other)

    # Generate new constraints from positive-negative pairs
    for p_row, p_rhs, p_coeff in pos:
        for n_row, n_rhs, n_coeff in neg:
            combined = [
                p_coeff * n_val - n_coeff * p_val 
                for p_val, n_val in zip(p_row[:elim_idx] + p_row[elim_idx+1:], 
                                        n_row[:elim_idx] + n_row[elim_idx+1:])
            ]
            new_rhs = p_coeff * n_rhs - n_coeff * p_rhs
            if any(not math.isclose(c, 0, abs_tol=1e-9) for c in combined):
                new_A.append(combined)
                new_b.append(new_rhs)

    return new_A, new_b if new_A else ([], []) 

def check_poly_intersection(
    A1: List[List[float]], 
    b1: List[float], 
    A2: List[List[float]], 
    b2: List[float]
) -> bool:
    """
    Check if two polyhedra defined by A*x <= b have a non-empty intersection.
    
    Parameters:
    - A1, b1: First polyhedron
    - A2, b2: Second polyhedron
    
    Returns:
    - True if polyhedra intersect, False otherwise
    """
    A1 = np.atleast_2d(A1) if A1 else np.empty((0, 0))
    A2 = np.atleast_2d(A2) if A2 else np.empty((0, 0))
    
    if A1.size == 0 and A2.size == 0:
        return True  # Both are unconstrained
    if A1.shape[1] != A2.shape[1]:
        print(f"Dimension mismatch: {A1.shape[1]} vs {A2.shape[1]}")
        return True
    
    # Combine constraints
    try:
        A_combined = np.vstack([np.array(A1), np.array(A2)])
        b_combined = np.concatenate([np.array(b1), np.array(b2)])
    except Exception as e:
        print(f"Error combining constraints: {str(e)}")
        return True  # Be conservative on errors
    
    # Set up linear programming problem to check feasibility
    n_vars = A_combined.shape[1]
    
    try:
        # Create any objective (doesn't matter for feasibility check)
        c = np.zeros(n_vars)
        
        # Use a linear programming solver to check feasibility
        from scipy.optimize import linprog
        result = linprog(c, A_ub=A_combined, b_ub=b_combined, method='highs')
        
        # If the optimization succeeded, the polyhedra intersect
        return result.success
    except Exception as e:
        print(f"Error checking intersection: {str(e)}")
        # If there's an error, assume they might intersect to be safe
        return True

def rows_to_inequalities(rows) -> Tuple[Tuple[List[List[float]], List[float]], List[str]]:
    """Convert database rows to polyhedron inequalities with numeric validation."""
    if not rows:
        return ([], []), []
    
    # Identify numeric columns dynamically
    numeric_cols = []
    sample_row = rows[0] if rows else []
    for idx, value in enumerate(sample_row):
        try:
            float(value)
            numeric_cols.append(idx)
        except:
            continue
    if not numeric_cols:
        return ([], []), []
    
    points = []
    for row in rows:
        try:
            if isinstance(row, dict):
                point = [float(row[col]) for col in numeric_cols]
            else:
                point = [float(row[idx]) for idx in numeric_cols]
            if all(not math.isnan(v) for v in point):
                points.append(point)
        except (TypeError, ValueError, IndexError) as e:
            print(f"Error processing row: {str(e)}")
            continue
    
    if not points:
        return ([], []), numeric_cols
    
    A, b = _points_to_inequalities(points)
    return (A, b), numeric_cols

def build_poly_dependency_matrix(results, dependency_matrix):
    """Build dependency matrix supporting multi-column conditions, with expression and fallback awareness."""
    N = len(results)
    
    for i in range(N):
        op_i = results[i]
        A_i, b_i = op_i.get('data_modified_poly', ([], []))
        data_cols_i = op_i.get('data_modified_cols', [])
        modified_cols_i = op_i.get('modified_cols', set())

        for j in range(i + 1, N):
            # Only check pairs where initial_matrix suggests a dependency
            if dependency_matrix[i, j] != 1:
                continue
                
            op_j = results[j]
            A_j, b_j = op_j.get('cond_true_poly', ([], []))
            cond_true_cols_j = op_j.get('cond_true_cols', [])
            condition_cols_j = op_j.get('condition_cols', set())

            # Require common columns, but proceed conservatively if projection fails
            common_cols = modified_cols_i & condition_cols_j
            if not common_cols:
                dependency_matrix[i, j] = 0  # No common columns, no dependency
                continue

            try:
                # Project polyhedra onto common columns
                proj_A_i, proj_b_i = project_polyhedron(A_i, b_i, data_cols_i, common_cols)
                proj_A_j, proj_b_j = project_polyhedron(A_j, b_j, cond_true_cols_j, common_cols)

                # Check polyhedron validity
                if not _valid_poly(proj_A_i, proj_b_i) or not _valid_poly(proj_A_j, proj_b_j):
                    # If invalid, conservatively assume dependency to avoid missing it
                    dependency_matrix[i, j] = 1
                    print(f"Kept {i}->{j}: Invalid polyhedron, assuming dependency")
                    continue

                # Check for intersection
                intersect_A, intersect_b = intersection_inequalities(proj_A_i, proj_b_i, proj_A_j, proj_b_j)
                if intersect_A is not None:
                    dependency_matrix[i, j] = 1
                    print(f"Set {i}->{j} to 1: Polyhedra intersect")
                else:
                    # Fallback to boundary intersection
                    if check_boundary_intersection(proj_A_i, proj_b_i, proj_A_j, proj_b_j):
                        dependency_matrix[i, j] = 1
                        print(f"Set {i}->{j} to 1: Boundary intersection detected")
                    else:
                        dependency_matrix[i, j] = 0
                        print(f"Set {i}->{j} to 0: No intersection or boundary overlap")

            except (ValueError, IndexError) as e:
                # Conservatively keep dependency on projection errors
                dependency_matrix[i, j] = 1
                print(f"Kept {i}->{j}: Projection error ({e}), assuming dependency")

    return dependency_matrix

def _valid_poly(A: List[List[float]], b: List[float]) -> bool:
    """Check if polyhedron is non-empty/feasible."""
    if not A:
        return True  # Universal set is valid
    try:
        result = linprog(
            c=np.zeros(len(A[0])),
            A_ub=np.array(A),
            b_ub=np.array(b),
            method='highs'
        )
        return result.success
    except Exception:
        return False
    
def check_boundary_intersection(A1: List[List[float]], b1: List[float],
                                A2: List[List[float]], b2: List[float]) -> bool:
    """Check polyhedron boundary intersection with numerical stability."""
    if not A1 or not A2 or len(A1[0]) != len(A2[0]):
        return False
    
    try:
        # Normalize constraints
        A_combined = np.vstack([A1, A2]).astype(np.float64)
        b_combined = np.hstack([b1, b2]).astype(np.float64)
        
        # Scale to unit norm
        norms = np.linalg.norm(A_combined, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        A_norm = A_combined / norms
        b_norm = b_combined / norms.flatten()
        
        # Solve with improved tolerance
        result = linprog(
            c=np.zeros(A_combined.shape[1]),
            A_ub=A_norm,
            b_ub=b_norm,
            method='highs',
            options={'tol': 1e-8, 'presolve': True}
        )
        
        if result.success:
            residuals = A_norm @ result.x - b_norm
            return np.any(np.abs(residuals)) < 1e-6
        return False
    except Exception as e:
        print(f"Boundary check failed: {e}")
        return False

def split_action_and_condition(sql_statements: List[str], connection: mysql.connector.connection.MySQLConnection) -> List[Dict]:
    """Enhanced with condition-based polyhedra"""
    results = []
    
    for statement in sql_statements:
        where_match = re.search(r"where\s+(.*)", statement, re.IGNORECASE)
        action = statement[:where_match.start()].strip() if where_match else statement.strip()
        condition = where_match.group(1).strip().rstrip(';').strip() if where_match else None

        # Extract table name
        table_match = re.search(r"(?:UPDATE|FROM|INTO)\s+([\w.]+)", action, re.IGNORECASE)
        table_name = table_match.group(1) if table_match else None
        
        # Get table columns and numeric indices
        columns = get_table_columns(connection, table_name) if table_name else []
        numeric_col_indices = [idx for idx, (name, dtype) in enumerate(columns) if is_numeric_type(dtype)]
        


        # Get operation columns
        modified_cols, condition_cols = get_operation_columns(connection, action, condition)
        # Parse condition to inequalities
        cond_inequalities = parse_condition_to_inequalities(condition, columns) if condition and columns else ([], [])
        
        # Extract data parts
        true_part, modified_part, false_part = extract_true_modified_false(connection, action, condition)
        
        # Compute polyhedra
        (data_true_A, data_true_b), data_true_cols = rows_to_inequalities(true_part) or (([], []), [])
        (data_modified_A, data_modified_b), data_modified_cols = rows_to_inequalities(modified_part) or (([], []), [])
        
        results.append({
            "action": action,
            "condition": condition,
            "true_part": true_part,
            "modified_part": modified_part,
            "false_part": false_part,
            "data_true_poly": (data_true_A, data_true_b),
            "data_modified_poly": (data_modified_A, data_modified_b),
            "cond_true_poly": cond_inequalities,
            "columns": columns,
            "modified_cols": modified_cols,
            "condition_cols": condition_cols,
            "data_true_cols": data_true_cols,
            "data_modified_cols": data_modified_cols
        })
    
    return results

def extract_true_modified_false(
    connection: mysql.connector.connection.MySQLConnection, action: str, condition: str
) -> Tuple[List, List, List]:
    """Extract true, modified, and false parts of a SQL statement, handling cases with no condition."""
    true_part = []
    modified_part = []
    false_part = []

    # Extract the table name from the action
    table_match = re.search(r"(?:UPDATE|FROM|INSERT INTO)\s+([\w.]+)", action, re.IGNORECASE)
    if not table_match:
        return true_part, modified_part, false_part
    table_name = table_match.group(1)

    # Check if condition exists (non-empty after trimming)
    has_condition = condition.strip() != "" if condition else False

    # Handle UPDATE statements
    if action.upper().startswith("UPDATE"):
        # True part: All rows or rows matching condition
        true_query = (
            f"SELECT * FROM {table_name} WHERE {condition}"
            if has_condition
            else f"SELECT * FROM {table_name}"
        )
        true_part = execute_sql_query(connection, true_query) or []

        # Apply the update with or without condition
        update_query = f"{action} WHERE {condition}" if has_condition else action
        execute_sql_query(connection, update_query) or []

        # Modified part: Same query as true_query but after update
        modified_part = execute_sql_query(connection, true_query) or []

        # False part: Rows not matching condition (empty if no condition)
        if has_condition:
            false_query = f"SELECT * FROM {table_name} WHERE NOT ({condition})"
            false_part = execute_sql_query(connection, false_query) or []

    # Handle DELETE statements
    elif action.upper().startswith("DELETE"):
        # True part: All rows or rows matching condition
        true_query = (
            f"SELECT * FROM {table_name} WHERE {condition}"
            if has_condition
            else f"SELECT * FROM {table_name}"
        )
        true_part = execute_sql_query(connection, true_query) or []

        # Apply delete with or without condition
        delete_query = f"{action} WHERE {condition}" if has_condition else action
        execute_sql_query(connection, delete_query)

        # Modified part: Deleted rows (same as true_part)
        modified_part = true_part

        # False part: Rows not matching condition (empty if no condition)
        if has_condition:
            false_query = f"SELECT * FROM {table_name} WHERE NOT ({condition})"
            false_part = execute_sql_query(connection, false_query) or []
    
    # Handle INSERT statements
    elif action.upper().startswith("INSERT"):
        # False_part: Existing rows before INSERT
        false_query = f"SELECT * FROM {table_name}"
        false_part = execute_sql_query(connection, false_query) or []

        # Execute the INSERT
        execute_sql_query(connection, action)

        # True_part: Fetch the newly inserted row(s)
        cursor = connection.cursor()
        cursor.execute(action)  # Re-executing to get lastrowid (alternative: fetch all and diff)
        last_id = cursor.lastrowid
        if last_id is not None:
            true_query = f"SELECT * FROM {table_name} WHERE id = {last_id}"
            true_part = execute_sql_query(connection, true_query) or []
        else:
            # Fallback: Select all rows and compare with false_part to find new rows
            after_query = f"SELECT * FROM {table_name}"
            after_insert = execute_sql_query(connection, after_query) or []
            true_part = [row for row in after_insert if row not in false_part]
        modified_part = true_part.copy()

    # Handle SELECT statements
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

def polyhedron_subset(A1: List[List[float]], b1: List[float], 
                      A2: List[List[float]], b2: List[float]) -> bool:
    """
    Check if polyhedron defined by A1x ≤ b1 is a subset of polyhedron defined by A2x ≤ b2.
    Uses linear programming to verify this condition.
    
    Returns:
        bool: True if the first polyhedron is a subset of the second, False otherwise.
    """
    if not A1 or not A2 or len(A1[0]) != len(A2[0]):
        return False
    
    
    # Convert inputs to numpy arrays for easier manipulation
    A1 = np.array(A1)
    b1 = np.array(b1)
    A2 = np.array(A2)
    b2 = np.array(b2)
    
    n_vars = A1.shape[1]  # Number of variables (dimensions)
    
    # For each constraint in the second polyhedron, check if it's satisfied by all points in the first
    for i in range(len(A2)):
        # Objective: maximize A2[i] · x subject to A1x ≤ b1
        c = -A2[i]  # Negative because linprog minimizes
        
        # Solve the linear program
        result = linprog(c, A_ub=A1, b_ub=b1, bounds=None, method='highs')
        
        # If optimization succeeded and the maximum value exceeds b2[i], the subset condition fails
        if result.success and -result.fun > b2[i]:
            return False
    
    return True

def intersection_inequalities(
    A1: List[List[float]], 
    b1: List[float], 
    A2: List[List[float]], 
    b2: List[float]
) -> Tuple[Optional[List[List[float]]], Optional[List[float]]]:
    """Compute intersection of two polyhedra, handling unconstrained cases."""
    # Handle unconstrained (empty) polyhedra
    if not A1 and not b1:
        if not A2 and not b2:
            return [], []  # Both unconstrained: entire space
        return A2, b2  # A1 unconstrained: intersection is A2
    if not A2 and not b2:
        return A1, b1  # A2 unconstrained: intersection is A1
    
    # Validate dimensions
    if not A1 or not A2 or len(A1[0]) != len(A2[0]):
        return None, None
    
    # Merge constraints
    A_combined = A1 + A2
    b_combined = b1 + b2
    
    # Check feasibility
    result = linprog(
        c=np.zeros(len(A_combined[0])),
        A_ub=A_combined,
        b_ub=b_combined,
        method='highs'
    )
    return (A_combined, b_combined) if result.success else (None, None)

def union_convex_hull(A1: List[List[float]], b1: List[float], 
                      A2: List[List[float]], b2: List[float]) -> Tuple[List[List[float]], List[float]]:
    if (not A1 and not A2) or (A1 == [] and A2 == []):
        return None, None
    # Convert polyhedra to vertex representation
    vertices1, rays1 = inequalities_to_vertices(A1, b1)
    vertices2, rays2 = inequalities_to_vertices(A2, b2)
    
    if vertices1 is None or vertices2 is None:
        # One of the polyhedra might be empty
        if vertices1 is None and vertices2 is None:
            return None, None
        elif vertices1 is None:
            return A2, b2
        else:
            return A1, b1
    
    # Combine vertices and rays
    combined_vertices = vertices1 + vertices2
    combined_rays = rays1 + rays2
    
    # Remove duplicates
    combined_vertices = [list(v) for v in set(tuple(v) for v in combined_vertices)]
    combined_rays = [list(r) for r in set(tuple(r) for r in combined_rays)]
    
    # Convert back to inequality representation
    A_hull, b_hull = vertices_to_inequalities(combined_vertices, combined_rays)
    
    return (A_hull, b_hull) if A_hull else (None, None)

def compute_A_intersection_B_complement(
    A1: List[List[float]], 
    b1: List[float],
    A2: List[List[float]], 
    b2: List[float], 
    epsilon: float = 1e-5
) -> Tuple[Optional[List[List[float]]], Optional[List[float]]]:
    """Compute A ∩ ¬B."""
    if not A1 or not A2 or A1 == [] or A2 == []:
        return None, None # If either polyhedron is missing, return None

    # Convert to numpy arrays
    A1 = np.array(A1)
    b1 = np.array(b1)
    A2 = np.array(A2)
    b2 = np.array(b2)

    n_vars = A1.shape[1]  # Number of variables

    # Introducing an auxiliary variable z
    A_extended = np.hstack([A2, -np.ones((A2.shape[0], 1))])  # A2 x - z <= b2
    b_extended = b2 + epsilon  # Ensuring strict violation

    # Adding constraints from A1x ≤ b1
    A1_extended = np.hstack([A1, np.zeros((A1.shape[0], 1))])
    A_combined = np.vstack([A1_extended, A_extended])
    b_combined = np.hstack([b1, b_extended])

    # Objective function: maximize z
    c = np.zeros(n_vars + 1)
    c[-1] = -1  # Maximize z (negated for minimization)

    # Solve linear program
    result = linprog(c, A_ub=A_combined, b_ub=b_combined, bounds=None, method='highs')

    if result.success and result.x[-1] > 0:
        return A_combined[:, :-1].tolist(), b_combined.tolist()
    else:
        return None, None

def inequalities_to_vertices(A: List[List[float]], b: List[float]) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Convert a polyhedron from inequality representation (Ax ≤ b) to vertex representation.
    Uses the Chernikova algorithm implemented in the Dependency class.
    
    Returns:
        Tuple[List[List[float]], List[List[float]]]: Vertices and rays of the polyhedron.
        Returns (None, None) if the polyhedron is empty.
    """
    if not A or len(A) == 0:
        return None, None
    
    # Prepare input matrix for Chernikova algorithm
    # The format should be [A | b]
    n_vars = len(A[0])
    m = []
    
    for i in range(len(A)):
        row = A[i] + [b[i]]  # Append b[i] to each row of A
        m.append(row)
    
    # Create an instance of Dependency and call the cre method
    
    result = cre(m)
    
    if result == 0:
        # The polyhedron is empty
        return None, None
    
    # Extract vertices and rays from the result
    # This part depends on the specific implementation of the Chernikova algorithm
    # and needs to be adapted to the actual output format
    
    # For demonstration, we'll return some placeholder values
    # In a real implementation, you would parse the output of the Chernikova algorithm
    vertices = [[0] * n_vars]  # Origin as a default vertex
    rays = []  # No rays for a bounded polyhedron
    
    return vertices, rays

def vertices_to_inequalities(vertices: List[List[float]], rays: List[List[float]]) -> Tuple[List[List[float]], List[float]]:
    """
    Convert a polyhedron from vertex representation to inequality representation.
    
    Returns:
        Tuple[List[List[float]], List[float]]: Inequalities (A, b) representing the polyhedron.
    """
    if not vertices:
        return None, None
    
    # This is a complex operation that typically requires a convex hull algorithm
    # For simplicity, we'll implement a basic version that works for simple cases
    
    n_vars = len(vertices[0])
    
    # For demonstration, we'll create a bounding box as a simple approximation
    A = []
    b = []
    
    # Find min and max along each dimension
    for i in range(n_vars):
        min_val = min(v[i] for v in vertices)
        max_val = max(v[i] for v in vertices)
        
        # Add constraints x_i ≥ min_val and x_i ≤ max_val
        constraint_min = [0] * n_vars
        constraint_min[i] = -1
        A.append(constraint_min)
        b.append(-min_val)
        
        constraint_max = [0] * n_vars
        constraint_max[i] = 1
        A.append(constraint_max)
        b.append(max_val)
    
    # Handle rays (if any)
    for ray in rays:
        # For each ray, add a constraint ensuring the ray direction is bounded
        A.append(ray)
        b.append(0)  # The ray starts from some vertex and goes to infinity
    
    return A, b

def cre(m):
        m = check_m(m)
        
        # Print the matrix
        for h1 in range(len(m)):
            for h2 in range(len(m[0])):
                print(m[h1][h2], "   ", end="")
            print()
        
        k, k1, k5, pm = 0, 0, 0, 0
        j, f, l, ax, k2 = 0, 0, 0, 0, 0
        g, tot1 = 0, 0
        
        att = len(m[0]) - 1
        
        v = [0] * att
        v1 = [0] * att
        n = [0] * att
        
        att1 = int(math.pow(2, att))
        
        # Initialize p array for vertices
        p = [[0 for _ in range(att)] for _ in range(att1 * att1)]
        
        px = [0] * att
        
        # Initialize r array for rays
        r = [[0 for _ in range(att)] for _ in range(2 * att)]
        
        # Set up rays array
        for h1 in range(len(r[0])):
            r[2 * h1][h1] = 1
            r[2 * h1 + 1][h1] = -1
        
        # Algorithm
        for h in range(att):
            p[0][h] = 0
        
        for i in range(len(m)):  # Loop for linear equations
            g = 0
            f1, f2 = 0, 0
            
            z = 0
            while z < len(p):  # Loop for vertices computation
                f = z
                l = 0
                
                # First if of Chernikova algorithm for vertices computation
                k = 0
                for j in range(len(m[i]) - 1):
                    k += p[f][j] * m[i][j]
                    v[j] = p[f][j]
                
                if k >= m[i][j]:
                    for t in range(len(v)):
                        p[f][t] = v[t]
                    l += 1
                
                # Second if of Chernikova algorithm for vertices computation
                for x in range(len(r)):
                    k1, k2 = 0, 0
                    for w in range(len(r[x])):
                        k1 += m[i][w] * r[x][w]
                        k2 += p[f][w] * m[i][w]
                        n[w] = r[x][w]
                    
                    if (k2 > m[i][j] and k1 < 0) or (k2 < m[i][j] and k1 > 0):
                        c = int((m[i][j] - k2) / k1)
                        g += 1
                        
                        if l > 0:
                            for x1 in range(len(p) - 1, f, -1):
                                for w1 in range(len(p[x1])):
                                    p[x1][w1] = p[x1 - 1][w1]
                            z += 1
                        
                        for e in range(len(n)):
                            v[e] = v[e] + (c * n[e])
                        
                        for t in range(len(v)):
                            p[f][t] = v[t]
                
                k = 0
                
                f1 = z + 1
                if f1 < len(p):
                    for f3 in range(len(p[f1])):
                        f2 += p[f1][f3]
                
                if f2 == 0:
                    break
                else:
                    f2 = 0
                
                z += 1
            
            # Chernikova algorithm for vertices computation (continued)
            s1, s5, s6 = 0, 0, 0
            f4, f6, f8, tot, kx, ky = 0, 0, 0, 0, 0, 0
            
            v2 = [0.0] * att
            v3 = [0.0] * att
            v4 = [0.0] * att
            v5 = [0.0] * att
            v6 = [0.0] * att
            v7 = [0.0] * att
            
            for s in range(len(p[1])):
                s1 += p[1][s]
            
            if s1 != 0:
                s2 = 0
                while s2 < len(p) - 1:
                    f4 = s2 + 1
                    if f4 < len(p):
                        for f5 in range(len(p[f4])):
                            f6 += p[f4][f5]
                    
                    if f6 == 0:
                        break
                    else:
                        f6 = 0
                    
                    for s4 in range(len(p[s2])):
                        v2[s4] = p[s2][s4]
                        s5 += m[i][s4] * p[s2][s4]
                    
                    s3 = s2 + 1
                    while s3 < len(p):
                        for s7 in range(len(p[s3])):
                            v3[s7] = p[s3][s7]
                            s6 += m[i][s7] * p[s3][s7]
                        
                        if s5 > m[i][s7] and s6 < m[i][s7]:
                            sum_val = (m[i][s7] - s6) / float(s5 - s6)
                            
                            for s8 in range(len(v2)):
                                v2[s8] = v2[s8] * sum_val
                            
                            sum1 = (m[i][s7] - s5) / float(s5 - s6)
                            
                            for s8 in range(len(v3)):
                                v3[s8] = v3[s8] * sum1
                            
                            for s8 in range(len(v3)):
                                v4[s8] = v2[s8] - v3[s8]
                            
                            for x1 in range(len(p) - 1, s2, -1):
                                for w1 in range(len(p[x1])):
                                    p[x1][w1] = p[x1 - 1][w1]
                            
                            for t in range(len(v4)):
                                p[s2][t] = int(v4[t])
                            
                            s2 += 1
                            s3 += 1
                        
                        elif s5 < m[i][s7] and s6 > m[i][s7]:
                            sum_val = (m[i][s7] - s5) / float(s6 - s5)
                            
                            for s8 in range(len(v2)):
                                v2[s8] = v2[s8] * sum_val
                            
                            sum1 = (m[i][s7] - s6) / float(s6 - s5)
                            
                            for s8 in range(len(v3)):
                                v3[s8] = v3[s8] * sum1
                            
                            for s8 in range(len(v3)):
                                v4[s8] = v2[s8] - v3[s8]
                            
                            for x1 in range(len(p) - 1, s2, -1):
                                for w1 in range(len(p[x1])):
                                    p[x1][w1] = p[x1 - 1][w1]
                            
                            for t in range(len(v4)):
                                p[s2][t] = int(v4[t])
                            
                            s2 += 1
                            s3 += 1
                        
                        s6 = 0
                        f7 = s3 + 1
                        if f7 < len(p):
                            for f5 in range(len(p[f7])):
                                f8 += p[f7][f5]
                        
                        if f8 == 0:
                            break
                        else:
                            f8 = 0
                        
                        s3 += 1
                    
                    s5 = 0
                    s2 += 1
            
            # Rays computation
            for z1 in range(len(r)):
                k5 = 0
                for j1 in range(len(r[z1])):
                    k5 += r[z1][j1] * m[i][j1]
                    v1[j1] = r[z1][j1]
                
                if not (k5 >= 0):
                    for t in range(len(v1)):
                        r[z1][t] = 0
                
                k5 = 0
            
            tot1 = 0
        
        # Emptiness checking
        kz = 0
        vx = [0] * att
        
        for ix in range(len(m)):
            for zx in range(len(p)):
                kz = 0
                for jx in range(len(m[ix]) - 1):
                    kz += p[zx][jx] * m[ix][jx]
                    vx[jx] = p[zx][jx]
                
                if kz < m[ix][jx]:
                    for t in range(len(vx)):
                        p[zx][t] = 0
                
                kz = 0
        
        xx = 0
        for i in range(len(p)):
            for b in range(len(p[i])):
                if p[i][b] != 0:
                    xx = 1
                    break
        
        return xx
    
def check_m(m):
    if not m:
        return []
        
    att = len(m[0]) - 1
    m1 = [[0 for _ in range(len(m[0]))] for _ in range(len(m))]
    
    order = []
    ini_order = []
    
    for i in range(att):
        # Lower bound constraint check
        found_lower = False
        for p in range(len(m)):
            if p >= len(m):
                continue
            if m[p][i] == 1:
                valid = True
                for q in range(len(m[0])-1):
                    if q != i and m[p][q] != 0:
                        valid = False
                        break
                if valid:
                    order.append(p)
                    found_lower = True
                    break
        if not found_lower:
            pass  # No lower bound found
            
        # Upper bound constraint check
        found_upper = False
        for p in range(len(m)):
            if p >= len(m):
                continue
            if m[p][i] == -1:
                valid = True
                for q in range(len(m[0])-1):
                    if q != i and m[p][q] != 0:
                        valid = False
                        break
                if valid:
                    order.append(p)
                    found_upper = True
                    break
        if not found_upper:
            pass  # No upper bound found
    
    # Handle remaining constraints
    ini_order = [i for i in range(len(m)) if i not in order]
    for i in range(len(ini_order)):
        if len(order) < len(m):
            order.append(ini_order[i])
    
    # Create ordered matrix
    for i in range(len(order)):
        m1[i] = m[order[i]].copy()
    
    return m1

def dependency_analysis(
    matrix: List[List[int]], 
    results: List[Dict]
) -> Tuple[List[List[int]], List, List[List[int]]]:
    """Perform dependency analysis using polyhedra."""
    print("\nPolyhedra-based Dependency Analysis")
    n = len(matrix)
    initial_matrix = [row.copy() for row in matrix]

    for i in range(n - 2):
        for j in range(i + 2, n):
            if matrix[i][j] != 0 and i + 1 < len(results) and j < len(results):
                mod_i_A, mod_i_b = results[i].get("data_modified_poly", ([], []))
                mod_i1_A, mod_i1_b = results[i+1].get("data_modified_poly", ([], []))
                mod_j_A, mod_j_b = results[j].get("data_modified_poly", ([], []))
                true_i_A, true_i_b = results[i].get("cond_true_poly", ([], []))

                # Dimension validation
                if len(mod_i_A) > 0 and len(mod_i_b) > 0:
                    if len(mod_i_A[0]) != len(mod_i1_A[0]) if len(mod_i1_A) > 0 else False:
                        continue

                # 1st condition: mod_i ⊆ mod_i1
                if polyhedron_subset(mod_i_A, mod_i_b, mod_i1_A, mod_i1_b):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (1st condition)")
                    continue
                
                # 2nd condition: mod_j ⊆ mod_i1
                if polyhedron_subset(mod_j_A, mod_j_b, mod_i1_A, mod_i1_b):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (2nd condition)")
                    continue

                # 3rd condition logic with error handling
                try:
                    true_j_A, true_j_b = results[j].get("cond_true_poly", ([], []))
                    true_j1_A, true_j1_b = results[j-1].get("cond_true_poly", ([], []))
                    mod_j1_A, mod_j1_b = results[j-1].get("data_modified_poly", ([], []))
                except (KeyError, IndexError):
                    continue

                # Safe intersection checks with fallback to (None, None)
                A_int_j, b_int_j = intersection_inequalities(true_j1_A, true_j1_b, true_j_A, true_j_b) or (None, None)
                A_X, b_X = (compute_A_intersection_B_complement(A_int_j, b_int_j, true_j_A, true_j_b) 
                            if (A_int_j is not None and b_int_j is not None) 
                            else (None, None))
                
                A_int_modj, b_int_modj = intersection_inequalities(mod_j1_A, mod_j1_b, mod_j_A, mod_j_b) or (None, None)
                A_Y, b_Y = (compute_A_intersection_B_complement(A_int_modj, b_int_modj, mod_j_A, mod_j_b) 
                            if (A_int_modj is not None and b_int_modj is not None) 
                            else (None, None))

                # Safe convex hull with fallback
                A_combined, b_combined = union_convex_hull(true_i_A, true_i_b, mod_i_A, mod_i_b) or (None, None)

                # Final intersection checks with null guards
                has_intersection_X = (
                    check_poly_intersection(A_X, b_X, A_combined, b_combined) 
                    if (A_X is not None and b_X is not None and A_combined is not None) 
                    else False
                )
                has_intersection_Y = (
                    check_poly_intersection(A_Y, b_Y, A_combined, b_combined) 
                    if (A_Y is not None and b_Y is not None and A_combined is not None) 
                    else False
                )

                if not (intersection_inequalities(A_X, b_X, A_combined, b_combined) and intersection_inequalities(A_Y, b_Y, A_combined, b_combined)):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (3rd condition)")
                else:
                    matrix[i][j] = 1
                    print(f"Kept {i}->{j} (4th condition)")

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
    """Main function to demonstrate SQL analysis workflow."""
    output_buffer = []

    def buffer_print(text):
        output_buffer.append(str(text))

    # Initialize database connection
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

        # Step 3: Parse and analyze statements
        start_time = time.time()
        results = split_action_and_condition(sql_statements, conn)
        parsed = split_action_and_condition1(sql_statements)

        # Step 4: Schema-based analysis
        schema = load_schema(database_file_path)
        used, defined, tables = extract_used_and_defined(parsed, schema)

        # Step 5: Initial dependency matrix (syntactic)
        initial_matrix, _, _, pp = create_dependency_matrix(
            used, defined, tables, line_numbers
        )
        initial_matrix_copy = copy.deepcopy(initial_matrix)

        # Step 6: Polyhedral refinement
        matrix1 = build_poly_dependency_matrix(results, initial_matrix)
        updated_matrix, _, _ = dependency_analysis(copy.deepcopy(matrix1), results)


        # Step 8: Metrics and false dependency detection
        initial_np = np.array(initial_matrix_copy)
        updated_np = np.array(updated_matrix)
        false_deps_matrix = np.logical_and(initial_np == 1, updated_np == 0)
        false_dependencies = int(np.sum(false_deps_matrix))

        execution_time = (time.time() - start_time) * 1000  # ms
        initial_dep_count = int(initial_np.sum())
        final_dep_count = int(updated_np.sum())

        # Get dependency and false dependency pairs
        deps = [
            f"Line {line_numbers[i]} -> Line {line_numbers[j]}"
            for i in range(len(initial_matrix_copy))
            for j in range(len(initial_matrix_copy))
            if initial_matrix_copy[i][j] == 1
        ]

        false_deps = [
            f"Line {line_numbers[i]} -> Line {line_numbers[j]}"
            for i in range(len(initial_matrix_copy))
            for j in range(len(initial_matrix_copy))
            if initial_matrix_copy[i][j] == 1 and updated_matrix[i][j] == 0
        ]

        # Step 9: Final report
        result_output = f"""

Execution Time: {execution_time:.2f} ms
Database Statements: {len(sql_statements)}
False Dependencies: {false_dependencies}

False Dependency List:
{chr(10).join(false_deps) if false_deps else 'No false dependencies found'}
"""
        buffer_print(result_output)

    except Exception as e:
        buffer_print(f"Error during analysis: {str(e)}")
    finally:
        conn.close()

    return "\n".join(output_buffer)


if __name__ == "__main__":  
    input_file_path = input("Enter the SQL input file path: ")
    database_file_path = input("Enter the database setup file path: ")
    main(input_file_path, database_file_path)