import sys
from flask import Flask, request, jsonify
import numpy as np
import psycopg2
import faiss
from sentence_transformers import SentenceTransformer
sys.path.append('/Users/sk/link')
from db.db_utils import get_profiles_from_indices, insert_alumni_profile, insert_vector

app = Flask(__name__)

model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384
faiss_index = faiss.IndexFlatL2(dimension)

def load_vectors():
    conn = psycopg2.connect(
        dbname="alumni",
        user="satvik",
        password="12345",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT AlumniID, Vector FROM FaissMapping;")
    data = cursor.fetchall()
    profile_ids = []
    vectors = []

    for row in data:
        profile_ids.append(row[0])
        vector = np.frombuffer(row[1], dtype='float32')
        #print(f"AlumniID: {row[0]}, Vector Shape: {vector.shape}")
        
        vectors.append(vector)

    if vectors:
        try:
            faiss_index.add(np.array(vectors))
        except ValueError as e:
            print("Error adding vectors to FAISS index:", e)
    
    cursor.close()
    conn.close()
    return profile_ids

profile_ids = load_vectors()


@app.route('/add-profile', methods=['POST'])
def add_profile():
    data = request.get_json()
    required_fields = ['FullName', 'CurrentRole', 'Company', 'University', 'HighSchool', 'LinkedInURL']
    print("got to add profile")
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    result = insert_alumni_profile(
        data['FullName'],
        data['CurrentRole'],
        data['Company'],
        data['University'],
        data['HighSchool'],
        data['LinkedInURL']
    )

    if result['status'] == 'success':
        alumni_id = result['alumni_id']
        profile_text = f"{data['FullName']} at {data['Company']}, graduated from {data['University']}"
        vector_result = insert_vector(alumni_id, profile_text)

        if vector_result['status'] == 'success':
            return jsonify({"status": "success", "message": "Profile and vector added successfully"}), 201
        else:
            return jsonify(vector_result), 500
    else:
        return jsonify(result), 500
    
    
@app.route('/search', methods=['POST'])
def search_profiles():
    data = request.get_json()
    query = data.get('query')
    k = data.get('k', 5) 

    if not query:
        return jsonify({"status": "error", "message": "Missing query"}), 400

    query_embedding = model.encode(query).astype("float32").reshape(1, -1)
    distances, indices = faiss_index.search(query_embedding, k)
    print("these are the indices", indices)
    if len(indices[0]) == 0:
        return jsonify({"status": "success", "results": []})

    result_ids = [profile_ids[i] for i in indices[0] if i < len(profile_ids)]
    print("there are the result_ids", result_ids)
    detailed_results = get_profiles_from_indices(result_ids)

    response = [
        {
            "AlumniID": r[0],
            "FullName": r[1],
            "CurrentRole": r[2],
            "Company": r[3],
            "University": r[4],
            "HighSchool": r[5],
            "LinkedInURL": r[6],
            "Distance": float(distances[0][i])
        }
        for i, r in enumerate(detailed_results)
    ]

    return jsonify({"status": "success", "results": response})

if __name__ == '__main__':
    app.run(debug=True)