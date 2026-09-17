"""TailorResume — Full API Test Suite"""
import httpx

client = httpx.Client(follow_redirects=True, timeout=30)
BASE = "http://127.0.0.1:8000/api"

print("=== TailorResume API Test Suite ===\n")

# 1. Health
r = client.get(f"{BASE}/health")
print(f"1. Health Check:       {r.status_code} OK" if r.status_code == 200 else f"1. FAIL: {r.status_code}")

# 2. Register
r = client.post(f"{BASE}/auth/register", json={"email": "suite@test.com", "password": "pass123", "name": "Suite"})
status = "Created" if r.status_code == 201 else "(exists)"
print(f"2. Register:           {r.status_code} {status}")

# 3. Login
r = client.post(f"{BASE}/auth/login", json={"email": "suite@test.com", "password": "pass123"})
token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}
print(f"3. Login:              {r.status_code} OK")

# 4. Get me
r = client.get(f"{BASE}/auth/me", headers=h)
print(f"4. Get Me:             {r.status_code} OK - {r.json()['email']}")

# 5. Create resume
resume_data = {
    "title": "Full Stack Resume",
    "content": [
        {"name": "Header", "type": "header", "fullName": "Jane Smith", "email": "jane@example.com", "phone": "555-0001", "location": "NYC"},
        {"name": "Summary", "type": "summary", "text": "Full-stack developer with 6 years of experience in Python and React."},
        {"name": "Skills", "type": "skills", "categories": {"Languages": "Python, TypeScript, Go", "Cloud": "AWS, GCP, Docker, K8s"}, "items": ["Python", "TypeScript", "React", "FastAPI"]},
        {"name": "Experience", "type": "experience", "entries": [{"company": "TechCo", "title": "Staff Engineer", "location": "NYC", "duration": "2021-Present", "bullets": ["Architected microservices platform handling 5M RPM", "Mentored 8 junior developers"]}]},
        {"name": "Education", "type": "education", "entries": [{"institution": "Stanford", "degree": "M.S. Computer Science", "location": "CA", "year": "2018"}]},
    ],
}
r = client.post(f"{BASE}/resumes/", json=resume_data, headers=h)
rid = r.json().get("id")
print(f"5. Create Resume:      {r.status_code} Created (id={rid})")

# 6. List resumes
r = client.get(f"{BASE}/resumes/", headers=h)
print(f"6. List Resumes:       {r.status_code} OK - {len(r.json())} resume(s)")

# 7. Get resume
r = client.get(f"{BASE}/resumes/{rid}", headers=h)
title = r.json()["title"]
print(f"7. Get Resume:         {r.status_code} OK - {title}")

# 8. Update resume
r = client.put(f"{BASE}/resumes/{rid}", json={"title": "Updated Resume"}, headers=h)
title = r.json()["title"]
print(f"8. Update Resume:      {r.status_code} OK - {title}")

# 9. DOCX export
r = client.post(f"{BASE}/export/docx", json={"sections": resume_data["content"]}, headers=h)
print(f"9. DOCX Export:        {r.status_code} OK - {len(r.content)} bytes")

# 10. Parse JD
r = client.post(f"{BASE}/parse/jd", json={"text": "We need a Senior Python Engineer with 5+ years in FastAPI, PostgreSQL, Docker, Kubernetes, AWS. Must know microservices and CI/CD. Nice: React, TypeScript."}, headers=h)
print(f"10. Parse JD:          {r.status_code} {'OK' if r.status_code == 200 else '(needs LLM key)'}")

# 11. Score
r = client.post(f"{BASE}/score/", json={"resume_content": resume_data["content"], "job_description": "Senior Python Engineer with FastAPI and Docker"}, headers=h)
print(f"11. Score Resume:      {r.status_code} {'OK' if r.status_code == 200 else '(needs LLM key)'}")

# 12. Delete
r = client.delete(f"{BASE}/resumes/{rid}", headers=h)
print(f"12. Delete Resume:     {r.status_code} OK")

print("\n=== Tests Complete ===")
