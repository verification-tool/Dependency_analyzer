import mysql.connector
from mysql.connector import Error
import re
from typing import List, Dict, Tuple, Optional,Any,Set
import numpy as np
import time as time
import copy
def connect_to_db() -> Optional[mysql.connector.connection.MySQLConnection]:
    """Connect to the MySQL database and return the connection object."""
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Your host, e.g., localhost or an IP address
            user="root",  # Your database username
            password="your_mysql_password",
            database="your_db_name"

        )
        print("Connected to database successfully!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None