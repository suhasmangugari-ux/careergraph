from fastapi import FastAPI, HTTPException
from backend.db import db

app = FastAPI(title="CareerGraph API")

@app.on_event("startup")
def startup():
    db.connect()

@app.on_event("shutdown")
def shutdown():
    db.close()

@app.get("/api/health")
def health():
    try:
        db.driver.verify_connectivity()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {str(e)}")

@app.get("/api/students")
def get_students():
    with db.driver.session() as session:
        result = session.run("MATCH (s:Student) RETURN s.id AS id, s.name AS name")
        return [record.data() for record in result]

@app.get("/api/jobs")
def get_jobs():
    with db.driver.session() as session:
        result = session.run("MATCH (j:Job) RETURN j.id AS id, j.title AS title")
        return [record.data() for record in result]

@app.get("/api/career-overview")
def get_career_overview(student_id: str, job_id: str):
    with db.driver.session() as session:
        # Current Skills
        res_current = session.run("""
            MATCH (s:Student {id: $student_id})-[:HAS_SKILL]->(sk:Skill)
            RETURN sk.id AS id, sk.name AS name
        """, student_id=student_id)
        current_skills = [r.data() for r in res_current]

        # Job Required Skills
        res_req = session.run("""
            MATCH (j:Job {id: $job_id})-[r:REQUIRES]->(sk:Skill)
            RETURN sk.id AS id, sk.name AS name, r.importance AS importance
        """, job_id=job_id)
        required_skills = [r.data() for r in res_req]

        current_ids = {s["id"] for s in current_skills}
        required_ids = {s["id"] for s in required_skills}
        
        missing_skills = [s for s in required_skills if s["id"] not in current_ids]
        
        readiness = round((len(required_ids - (required_ids - current_ids)) / len(required_ids)) * 100) if required_ids else 0

        return {
            "readiness": readiness,
            "current_skills": current_skills,
            "missing_skills": missing_skills
        }

@app.get("/api/multi-hop-path")
def get_multi_hop_path(student_id: str, job_id: str):
    """MULTI-HOP TRAVERSAL: Connects current student skills to missing job skills via prerequisite paths."""
    with db.driver.session() as session:
        result = session.run("""
            MATCH (s:Student {id: $student_id})-[:HAS_SKILL]->(start:Skill)
            MATCH (j:Job {id: $job_id})-[:REQUIRES]->(target:Skill)
            WHERE NOT (s)-[:HAS_SKILL]->(target)
            
            // Find path from current skill (start) through prerequisites to target required skill
            MATCH p = shortestPath((start)-[:PREREQUISITE_FOR*1..6]->(target))
            
            RETURN 
                [node IN nodes(p) | {id: node.id, name: node.name}] AS path_nodes,
                j.title AS job_title
        """, student_id=student_id, job_id=job_id)
        
        paths = []
        for record in result:
            paths.append(record.data())
        return {"paths": paths}
    
@app.get("/api/recommendations")
def get_recommendations(job_id: str):
    with db.driver.session() as session:
        # Courses for missing skills
        res_courses = session.run("""
            MATCH (j:Job {id: $job_id})-[:REQUIRES]->(sk:Skill)<-[:TAUGHT_SKILL]-(c:Course)
            RETURN sk.name AS skill, c.name AS course, c.provider AS provider
        """, job_id=job_id)
        
        # Projects for missing skills
        res_projects = session.run("""
            MATCH (j:Job {id: $job_id})-[:REQUIRES]->(sk:Skill)<-[:BUILDS]-(p:Project)
            RETURN sk.name AS skill, p.name AS project, p.difficulty AS difficulty
        """, job_id=job_id)

        return {
            "courses": [r.data() for r in res_courses],
            "projects": [r.data() for r in res_projects]
        }