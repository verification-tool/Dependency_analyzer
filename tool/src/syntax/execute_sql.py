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