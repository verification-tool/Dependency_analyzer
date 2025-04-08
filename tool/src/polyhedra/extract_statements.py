import re
import os
import numpy as np
import time
from typing import List, Tuple, Dict, Any

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