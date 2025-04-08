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