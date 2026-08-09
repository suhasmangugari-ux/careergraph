import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USERNAME", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

def seed():
    if not URI or not PASSWORD:
        raise ValueError("Missing CognoDB environment variables in .env file!")

    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with driver.session() as session:
        print("🗑️ Cleaning existing data...")
        session.run("MATCH (n) DETACH DELETE n")

        print("⚡ Creating constraints...")
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Student) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (sk:Skill) REQUIRE sk.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (j:Job) REQUIRE j.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Course) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (comp:Company) REQUIRE comp.id IS UNIQUE",
        ]
        for constraint in constraints:
            try:
                session.run(constraint)
            except Exception as e:
                print(f"Constraint notice: {e}")

        # 1. Seed 10 Indian Students
        print("👥 Adding 10 Students...")
        students = [
            {"id": "STU001", "name": "Aarav Sharma", "experience_level": "Intermediate"},
            {"id": "STU002", "name": "Ananya Iyer", "experience_level": "Beginner"},
            {"id": "STU003", "name": "Rohan Verma", "experience_level": "Advanced"},
            {"id": "STU004", "name": "Priya Kulkarni", "experience_level": "Intermediate"},
            {"id": "STU005", "name": "Vikram Reddy", "experience_level": "Beginner"},
            {"id": "STU006", "name": "Sneha Patel", "experience_level": "Intermediate"},
            {"id": "STU007", "name": "Arjun Nair", "experience_level": "Advanced"},
            {"id": "STU008", "name": "Kavya Rao", "experience_level": "Beginner"},
            {"id": "STU009", "name": "Aditya Banerjee", "experience_level": "Intermediate"},
            {"id": "STU010", "name": "Meera Deshmukh", "experience_level": "Advanced"},
        ]
        session.run("""
            UNWIND $students AS s
            CREATE (:Student {id: s.id, name: s.name, experience_level: s.experience_level})
        """, students=students)

        # 2. Seed Skills
        print("💡 Adding Skills...")
        skills = [
            {"id": "SK001", "name": "Python", "category": "Programming"},
            {"id": "SK002", "name": "SQL", "category": "Data"},
            {"id": "SK003", "name": "Linear Algebra & Statistics", "category": "Math"},
            {"id": "SK004", "name": "Machine Learning", "category": "AI"},
            {"id": "SK005", "name": "Deep Learning", "category": "AI"},
            {"id": "SK006", "name": "PyTorch", "category": "Frameworks"},
            {"id": "SK007", "name": "LLMs & Transformers", "category": "GenAI"},
            {"id": "SK008", "name": "RAG Architecture", "category": "GenAI"},
            {"id": "SK009", "name": "Docker", "category": "DevOps"},
            {"id": "SK010", "name": "Kubernetes", "category": "DevOps"},
            {"id": "SK011", "name": "FastAPI", "category": "Engineering"},
            {"id": "SK012", "name": "Vector Databases", "category": "GenAI"},
        ]
        session.run("""
            UNWIND $skills AS sk
            CREATE (:Skill {id: sk.id, name: sk.name, category: sk.category})
        """, skills=skills)

        # 3. Seed Student Skills (MAPPED FOR ALL 10 STUDENTS)
        print("🔗 Mapping Skills for ALL 10 Students...")
        student_skills = [
            # STU001: Aarav Sharma
            {"student_id": "STU001", "skill_id": "SK001"},
            {"student_id": "STU001", "skill_id": "SK002"},
            {"student_id": "STU001", "skill_id": "SK003"},

            # STU002: Ananya Iyer
            {"student_id": "STU002", "skill_id": "SK001"},
            {"student_id": "STU002", "skill_id": "SK002"},

            # STU003: Rohan Verma
            {"student_id": "STU003", "skill_id": "SK001"},
            {"student_id": "STU003", "skill_id": "SK009"},
            {"student_id": "STU003", "skill_id": "SK011"},

            # STU004: Priya Kulkarni
            {"student_id": "STU004", "skill_id": "SK001"},
            {"student_id": "STU004", "skill_id": "SK002"},
            {"student_id": "STU004", "skill_id": "SK004"},

            # STU005: Vikram Reddy
            {"student_id": "STU005", "skill_id": "SK001"},

            # STU006: Sneha Patel
            {"student_id": "STU006", "skill_id": "SK001"},
            {"student_id": "STU006", "skill_id": "SK004"},
            {"student_id": "STU006", "skill_id": "SK005"},

            # STU007: Arjun Nair
            {"student_id": "STU007", "skill_id": "SK001"},
            {"student_id": "STU007", "skill_id": "SK009"},
            {"student_id": "STU007", "skill_id": "SK010"},

            # STU008: Kavya Rao
            {"student_id": "STU008", "skill_id": "SK002"},
            {"student_id": "STU008", "skill_id": "SK003"},

            # STU009: Aditya Banerjee
            {"student_id": "STU009", "skill_id": "SK001"},
            {"student_id": "STU009", "skill_id": "SK011"},

            # STU010: Meera Deshmukh
            {"student_id": "STU010", "skill_id": "SK001"},
            {"student_id": "STU010", "skill_id": "SK004"},
            {"student_id": "STU010", "skill_id": "SK005"},
            {"student_id": "STU010", "skill_id": "SK006"},
        ]
        session.run("""
            UNWIND $data AS d
            MATCH (s:Student {id: d.student_id})
            MATCH (sk:Skill {id: d.skill_id})
            CREATE (s)-[:HAS_SKILL]->(sk)
        """, data=student_skills)

        # 4. Seed Prerequisite Paths (Multi-Hop Engine)
        print("🪜 Adding Skill Prerequisite Paths...")
        prereqs = [
            ("SK001", "SK004"),  # Python -> Machine Learning
            ("SK002", "SK003"),  # SQL -> Linear Algebra & Statistics
            ("SK003", "SK004"),  # Stats -> Machine Learning
            ("SK004", "SK005"),  # Machine Learning -> Deep Learning
            ("SK005", "SK006"),  # Deep Learning -> PyTorch
            ("SK006", "SK007"),  # PyTorch -> LLMs & Transformers
            ("SK007", "SK008"),  # LLMs -> RAG Architecture
            ("SK007", "SK012"),  # LLMs -> Vector Databases
            ("SK001", "SK009"),  # Python -> Docker
            ("SK009", "SK010"),  # Docker -> Kubernetes
            ("SK001", "SK011"),  # Python -> FastAPI
        ]
        session.run("""
            UNWIND $prereqs AS p
            MATCH (a:Skill {id: p[0]})
            MATCH (b:Skill {id: p[1]})
            CREATE (a)-[:PREREQUISITE_FOR]->(b)
        """, prereqs=prereqs)

        # 5. Seed Target Job Roles
        print("💼 Adding Target Jobs...")
        jobs = [
            {"id": "JOB001", "title": "AI/ML Engineer", "level": "Senior"},
            {"id": "JOB002", "title": "Generative AI Specialist", "level": "Mid-Senior"},
            {"id": "JOB003", "title": "MLOps Engineer", "level": "Senior"},
            {"id": "JOB004", "title": "Data Scientist", "level": "Mid-Level"},
        ]
        session.run("""
            UNWIND $jobs AS j
            CREATE (:Job {id: j.id, title: j.title, level: j.level})
        """, jobs=jobs)

        # 6. Seed Job Requirements (MAPPED FOR ALL 4 JOBS)
        print("📌 Mapping Requirements for ALL 4 Jobs...")
        job_reqs = [
            # JOB001: AI/ML Engineer
            {"job_id": "JOB001", "skill_id": "SK001", "importance": 5},
            {"job_id": "JOB001", "skill_id": "SK004", "importance": 5},
            {"job_id": "JOB001", "skill_id": "SK005", "importance": 5},
            {"job_id": "JOB001", "skill_id": "SK006", "importance": 4},
            {"job_id": "JOB001", "skill_id": "SK008", "importance": 4},

            # JOB002: Generative AI Specialist
            {"job_id": "JOB002", "skill_id": "SK001", "importance": 5},
            {"job_id": "JOB002", "skill_id": "SK006", "importance": 4},
            {"job_id": "JOB002", "skill_id": "SK007", "importance": 5},
            {"job_id": "JOB002", "skill_id": "SK008", "importance": 5},
            {"job_id": "JOB002", "skill_id": "SK012", "importance": 4},

            # JOB003: MLOps Engineer
            {"job_id": "JOB003", "skill_id": "SK001", "importance": 5},
            {"job_id": "JOB003", "skill_id": "SK009", "importance": 5},
            {"job_id": "JOB003", "skill_id": "SK010", "importance": 5},
            {"job_id": "JOB003", "skill_id": "SK011", "importance": 4},

            # JOB004: Data Scientist
            {"job_id": "JOB004", "skill_id": "SK001", "importance": 5},
            {"job_id": "JOB004", "skill_id": "SK002", "importance": 5},
            {"job_id": "JOB004", "skill_id": "SK003", "importance": 5},
            {"job_id": "JOB004", "skill_id": "SK004", "importance": 4},
        ]
        session.run("""
            UNWIND $reqs AS r
            MATCH (j:Job {id: r.job_id})
            MATCH (sk:Skill {id: r.skill_id})
            CREATE (j)-[:REQUIRES {importance: r.importance}]->(sk)
        """, reqs=job_reqs)

        # 7. Seed Courses & Projects
        print("📚 Adding Courses and Projects...")
        courses = [
            {"id": "C001", "name": "Machine Learning Specialization", "provider": "Coursera", "skill_id": "SK004"},
            {"id": "C002", "name": "Deep Learning with PyTorch", "provider": "Udacity", "skill_id": "SK006"},
            {"id": "C003", "name": "Production GenAI & RAG Systems", "provider": "NPTEL / IIT Madras", "skill_id": "SK008"},
            {"id": "C004", "name": "Docker & Kubernetes Mastery", "provider": "Udemy", "skill_id": "SK010"},
            {"id": "C005", "name": "Vector Databases & Semantic Search", "provider": "Pinecone Academy", "skill_id": "SK012"},
            {"id": "C006", "name": "Building REST APIs with FastAPI", "provider": "FreeCodeCamp", "skill_id": "SK011"},
            {"id": "C007", "name": "Applied Statistics for Data Science", "provider": "edX", "skill_id": "SK003"},
            {"id": "C008", "name": "LLM Fine-Tuning & Prompting", "provider": "DeepLearning.AI", "skill_id": "SK007"},
        ]
        session.run("""
            UNWIND $courses AS c
            MATCH (sk:Skill {id: c.skill_id})
            CREATE (co:Course {id: c.id, name: c.name, provider: c.provider})-[:TAUGHT_SKILL]->(sk)
        """, courses=courses)

        projects = [
            {"id": "P001", "name": "Enterprise RAG Document Assistant", "difficulty": "Advanced", "skill_id": "SK008"},
            {"id": "P002", "name": "E-Commerce Customer Churn Predictor", "difficulty": "Intermediate", "skill_id": "SK004"},
            {"id": "P003", "name": "Kubernetes ML Model Deployment Pipeline", "difficulty": "Advanced", "skill_id": "SK010"},
            {"id": "P004", "name": "Real-Time Image Classifier API", "difficulty": "Intermediate", "skill_id": "SK006"},
            {"id": "P005", "name": "Semantic Search Engine with Vector DB", "difficulty": "Intermediate", "skill_id": "SK012"},
            {"id": "P006", "name": "Microservice Backend for Model Inferences", "difficulty": "Intermediate", "skill_id": "SK011"},
        ]
        session.run("""
            UNWIND $projects AS p
            MATCH (sk:Skill {id: p.skill_id})
            CREATE (pr:Project {id: p.id, name: p.name, difficulty: p.difficulty})-[:BUILDS]->(sk)
        """, projects=projects)

        # 8. Seed Companies
        print("🏢 Adding Hiring Companies...")
        companies = [
            {"id": "COMP001", "name": "Flipkart", "industry": "E-Commerce", "location": "Bengaluru", "job_id": "JOB001"},
            {"id": "COMP002", "name": "Reliance Jio AI Labs", "industry": "Telecom/AI", "location": "Mumbai", "job_id": "JOB002"},
            {"id": "COMP003", "name": "Swiggy", "industry": "FoodTech", "location": "Bengaluru", "job_id": "JOB003"},
            {"id": "COMP004", "name": "Microsoft India", "industry": "Technology", "location": "Hyderabad", "job_id": "JOB004"},
        ]
        session.run("""
            UNWIND $companies AS comp
            MATCH (j:Job {id: comp.job_id})
            CREATE (c:Company {id: comp.id, name: comp.name, industry: comp.industry, location: comp.location})-[:OFFERS]->(j)
        """, companies=companies)

    driver.close()
    print("✅ Database successfully seeded with ALL 10 Indian Candidates & 4 Job Roles!")

if __name__ == "__main__":
    seed()