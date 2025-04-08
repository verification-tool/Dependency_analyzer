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