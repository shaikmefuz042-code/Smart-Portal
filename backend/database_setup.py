from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_portal"]
faculty_col = db["faculty"]
students_col = db["students"]

# Clear previous data
faculty_col.delete_many({})
students_col.delete_many({})

# ----------------- Faculty Data -----------------
faculty_col.insert_one({
    "name": "Murali Krishna",
    "id": "50001",            # should match 'id' field in app.py
    "password": "VIG2341"
})

# ----------------- Students Data -----------------
students_col.insert_many([
    {
        "name": "Shaik Mehfuz",
        "roll_no": "231fa20020",
        "password": "mehfuz@09",
        "Department": "ACSE",
        "Branch": "CSBS",
        "year": "3rd Year",
        "cgpa": 8.5,
        "phone": "6387453406",
        "email": "231fa20020@gmail.com"
    },
    {
        "name": "M Ram Charan",
        "roll_no": "231fa20023",
        "password": "charanz@23",
        "Department": "ACSE",
        "Branch": "CSBS",
        "year": "3rd Year",
        "cgpa": 8.2,
        "phone": "6387453406",
        "email": "231fa200233@gmail.com"
    },
    {
        "name": "D Bhavesh Reddy",
        "roll_no": "231fa20031",
        "password": "bhavesh@31",
        "Department": "ACSE",
        "Branch": "CSBS",
        "year": "3rd Year",
        "cgpa": 9.3,
        "phone": "6387453406",
        "email": "231fa200231@gmail.com"
    }
])

print("✅ Database setup complete: 1 faculty and 3 students added")
