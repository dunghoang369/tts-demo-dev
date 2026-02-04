from api.index import init_firebase

db = init_firebase()

auth_collection = db.collection("authentication")

# Get all documents from the collection
docs = auth_collection.stream()

# Iterate and print each document
for doc in docs:
    print(f"Document ID: {doc.id}")
    print(f"Data: {doc.to_dict()}")
    print("---")

query = (
    auth_collection.where("email", "==", "premium@namisense.ai")
    .where("is_active", "==", True)
    .limit(1)
)

docs = query.stream()
for doc in docs:
    print(doc.to_dict())

doc_ref = auth_collection.document("premium")
doc = doc_ref.get()
user_data = doc.to_dict()
print(user_data)
import pdb

pdb.set_trace()
