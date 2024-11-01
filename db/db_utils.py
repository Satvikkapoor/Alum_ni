import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer

DB_NAME = "alumni"
DB_USER = "satvik"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_db_connection():
    """Establish a database connection and return the connection and cursor."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    return conn, cursor

def close_db_connection(conn, cursor):
    """Close the database connection and cursor."""
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def insert_alumni_profile(full_name, current_role, company, university, high_school, linkedin_url):
    """Insert an alumni profile into the database and return the alumni ID."""
    conn, cursor = get_db_connection()
    try:
        cursor.execute("""
            INSERT INTO AlumniProfiles (FullName, CurrentRole, Company, University, HighSchool, LinkedInURL)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING AlumniID;
        """, (full_name, current_role, company, university, high_school, linkedin_url))
        alumni_id = cursor.fetchone()[0]
        conn.commit()
        return {"status": "success", "alumni_id": alumni_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        close_db_connection(conn, cursor)

def insert_vector(alumni_id, profile_text):
    """Generate a vector embedding and insert it into the FaissMapping table."""
    conn, cursor = get_db_connection()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    try:
        # Generate the vector embedding
        vector = model.encode(profile_text).astype('float32')
        
        # Insert the vector into the FaissMapping table
        cursor.execute("""
            INSERT INTO FaissMapping (AlumniID, Vector)
            VALUES (%s, %s);
        """, (alumni_id, psycopg2.Binary(vector.tobytes())))
        
        conn.commit()
        return {"status": "success", "message": "Vector inserted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        close_db_connection(conn, cursor)
        
def get_profiles_from_indices(result_ids):
    """Fetch detailed alumni information based on result IDs."""
    conn, cursor = get_db_connection()
    try:
        cursor.execute(
            "SELECT AlumniID, FullName, CurrentRole, Company, University, HighSchool, LinkedInURL "
            "FROM AlumniProfiles WHERE AlumniID IN %s;", 
            (tuple(result_ids),)
        )
        results = cursor.fetchall()
        return results
    except Exception as e:
        print("Error fetching profiles:", e)
        return []
    finally:
        close_db_connection(conn, cursor)
