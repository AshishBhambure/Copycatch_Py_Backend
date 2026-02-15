from fastapi import FastAPI, HTTPException, Query
from app.preProcessing import save_to_db, extract_and_preprocess
from app.db import documents_col
from app.Model.preProcessingModel import UploadRequest
from app.hashFunction import make_hash_funcs
from app.db import similarity_report_col
app = FastAPI()

@app.head("/")
def sayHello():
    return {"message": "Py Backedn Up and Running !!"}


@app.get("/")
def read_root():

    return {"message": "Hello, COPYCATCH! MongoDB is connected."}

@app.get("/hash-funcs/")
def get_hash_funcs():
    funcs = make_hash_funcs()
    return {"num_funcs": funcs}

@app.post("/upload/")
def upload_file(request: UploadRequest):
    try:
        # Access fields from request
        print("Inside File Upload")
        file_url = request.file_url
        submission_id = request.submission_id
        assignment_id = request.assignment_id
        minMatcgLength = request.minMatchLength
        print(" File Arrived : ",  file_url, submission_id,assignment_id)
        inserted_id = save_to_db(file_url, submission_id,assignment_id,minMatcgLength)

        print(" File Saved ")

        return {
            "message": "File processed and saved to DB",
            "id": inserted_id,
            "submission_id": submission_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    if not documents_col:
        raise HTTPException(status_code=500, detail="Database not connected")
    doc = documents_col.find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": str(doc["_id"]), "raw_text": doc["raw_text"], "processed_text": doc["processed_text"]}




@app.get("/get_similarity_report/{submission_id}")
def get_similarity_report(submission_id: str):
    """
    Fetch a similarity report by submission_id
    """
    print(f"Fetching report for submission_id: {submission_id}")

    report = similarity_report_col.find_one({"submission_id": submission_id})
    empty_response = {
        "_id": "",  # keep field present
        "assignment_id": "",  # dummy allowed
        "submission_id": submission_id,  # keep requested id
        "plagarized_with": []  # important change
    }

    if not report:
            return empty_response


    # Convert ObjectId to string for JSON serialization
    if "_id" in report:
        report["_id"] = str(report["_id"])

    return report