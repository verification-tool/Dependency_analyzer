import re
import os
import numpy as np
import time
from typing import List, Tuple, Dict, Any

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

def split_action_and_condition(sql_statements: List[str]) -> List[Dict[str, str]]:
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

def process_files(input_file: str, database_file: str) -> str:
    """Main processing function."""
    try:
        start_time = time.time()
        schema = load_schema(database_file)
        statements, line_nums = extract_sql_statements(input_file)
        parsed = split_action_and_condition(statements)
        used, defined, tables = extract_used_and_defined(parsed, schema)
        matrix, total, deps, pp = create_dependency_matrix(used, defined, tables, line_nums)
        
        exec_time = round((time.time() - start_time) * 1000, 2)
        matrix_str = '\n'.join([' '.join(map(str, row)) for row in matrix])
        
        return f"""
Analysis Results:
SQL Statements Found: {len(statements)}
Dependency Matrix:
{matrix_str}

Dependency Types:
Program-Program: {pp}

Execution Time: {exec_time}ms
Dependencies Detected:
{'\n'.join(deps) if deps else 'No dependencies found'}
"""
    except Exception as e:
        return f"Analysis failed: {str(e)}"

def main(input_file_path: str, database_file_path: str) -> str:
    """Entry point with validation."""
    if not os.path.exists(input_file_path):
        return "Error: Input file not found."
    if not os.path.exists(database_file_path):
        return "Error: Database schema file not found."
    return process_files(input_file_path, database_file_path)

if __name__ == "__main__":
    input_path = input("Enter JSP file path: ")
    schema_path = input("Enter database schema path: ")
    print(main(input_path, schema_path))