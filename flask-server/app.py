import sys
import certifi
import faiss
import numpy as np
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import Binary
from sentence_transformers import SentenceTransformer
sys.path.append('/Users/sk/link')
from db.utils import insert_alumni_profile, insert_vector, get_profiles_from_indices



app = Flask(__name__)

MONGO_URI = "mongodb+srv://ksatvik:S9050756696k@cluster0.z3sbo.mongodb.net/myDatabase?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['alum_ni']  
alumni_profiles = db['alumniProfiles']
faiss_mapping = db['faissMapping']

model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384
faiss_index = faiss.IndexFlatL2(dimension)

def load_vectors():
    """Load vectors and their associated IDs from MongoDB and add them to FAISS index."""
    data = faiss_mapping.find({}, {'alumniId': 1, 'vector': 1})
    profile_ids = []
    vectors = []

    for record in data:
        profile_ids.append(record['alumniId'])
        vector = np.frombuffer(record['vector'], dtype='float32')
        vectors.append(vector)

    if vectors:
        try:
            faiss_index.add(np.array(vectors))
        except ValueError as e:
            print("Error adding vectors to FAISS index:", e)

    return profile_ids

profile_ids = load_vectors()

def normalize_field(field):
    """Normalize a string field by stripping extra spaces and applying title case."""
    if field:
        return field.strip().title()
    return ""


@app.route('/add-profile', methods=['POST'])
def add_profile():
    data = request.get_json()
    required_fields = ['FullName', 'CurrentRole', 'Company', 'University', 'HighSchool', 'LinkedInURL']
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    normalized_data = {field: normalize_field(data.get(field, "")) for field in required_fields}

    result = insert_alumni_profile(
        normalized_data['FullName'],
        normalized_data['CurrentRole'],
        normalized_data['Company'],
        normalized_data['University'],
        normalized_data['HighSchool'],
        data['LinkedInURL']
    )

    if result['status'] == 'success':
        alumni_id = result['alumni_id']
        profile_text = (
        f"{normalized_data['FullName']} work as {normalized_data['CurrentRole']} at {normalized_data['Company']}, "
        f"graduated from {normalized_data['University']} and attended {normalized_data['HighSchool']}.")
        
        # Use the MongoDB function to insert a vector
        vector_result = insert_vector(alumni_id, profile_text)

        if vector_result['status'] == 'success':
            return jsonify({"status": "success", "message": "Profile and vector added successfully"}), 201
        else:
            return jsonify(vector_result), 50
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
    print("here are the indices", indices)
    print("distances", distances)

    if len(indices[0]) == 0:
        return jsonify({"status": "success", "results": []})

    result_ids = [profile_ids[i] for i in indices[0] if i < len(profile_ids)]
    print("this is the result ids", result_ids)
    detailed_results = get_profiles_from_indices(result_ids)

    response = [
        {
            "AlumniID": str(r['_id']), 
            "FullName": r.get('fullName', 'N/A'),
            "CurrentRole": r.get('currentRole', 'N/A'),
            "Company": r.get('company', 'N/A'),
            "University": r.get('university', 'N/A'),
            "HighSchool": r.get('highSchool', 'N/A'),
            "LinkedInURL": r.get('linkedInURL', 'N/A'),
            "Distance": float(distances[0][i])
        }
        for i, r in enumerate(detailed_results)
    ]

    return jsonify({"status": "success", "results": response})

if __name__ == '__main__':
    app.run(debug=True)