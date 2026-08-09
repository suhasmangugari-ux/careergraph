import os
import streamlit as st
import requests
from pyvis.network import Network
import streamlit.components.v1 as components

# API_URL = "http://127.0.0.1:8000/api"
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = f"{BASE_URL}/api"
st.set_page_config(page_title="CareerGraph", layout="wide")

st.title("CareerGraph: AI Skill Path Explorer")

# Check Backend Health
try:
    health = requests.get(f"{API_URL}/health", timeout=3).json()
except Exception as e:
    st.error(f" Backend or CognoDB is unreachable. Error details: {e}")
    st.info(" Make sure FastAPI is running in terminal: `uvicorn backend.app:app --reload`")
    st.stop()

# Load Dropdowns
students = requests.get(f"{API_URL}/students").json()
jobs = requests.get(f"{API_URL}/jobs").json()

col1, col2 = st.columns(2)
with col1:
    selected_student_name = st.selectbox("Select Student", [s["name"] for s in students])
    student_id = next(s["id"] for s in students if s["name"] == selected_student_name)

with col2:
    selected_job_title = st.selectbox("Select Target Job Role", [j["title"] for j in jobs])
    job_id = next(j["id"] for j in jobs if j["title"] == selected_job_title)

st.markdown("---")

# Fetch Career Overview
overview = requests.get(f"{API_URL}/career-overview", params={"student_id": student_id, "job_id": job_id}).json()

# Extract Student's Current Skill IDs set for exact matching
current_skill_ids = {s["id"] for s in overview["current_skills"]}

# Dashboard Summary
st.subheader("📊 Career Readiness Overview")
st.progress(overview["readiness"] / 100)
st.write(f"**Readiness Score:** `{overview['readiness']}%`")

c_left, c_right = st.columns(2)
with c_left:
    st.markdown("### ✅ Current Skills")
    for sk in overview["current_skills"]:
        st.success(f"• {sk['name']}")

with c_right:
    st.markdown("### 🎯 Missing Skills Needed")
    for sk in overview["missing_skills"]:
        st.warning(f"• {sk['name']} (Importance: {sk['importance']}/5)")

st.markdown("---")

# Graph Visualization (Multi-Hop Traversal)
st.subheader("🕸️ Graph Traversal: Your Skill Progression Path")
st.caption("Visualizing multi-hop Cypher traversal paths from your current skills to target requirements.")

# Color Legend
st.markdown("""
<div style="display: flex; gap: 20px; margin-bottom: 10px;">
    <span><span style="color:#4CAF50; font-size:18px;">🟢</span> <b>Current Skill</b></span>
    <span><span style="color:#FF9800; font-size:18px;">🟠</span> <b>Required / Path Skill</b></span>
</div>
""", unsafe_allow_html=True)

path_data = requests.get(f"{API_URL}/multi-hop-path", params={"student_id": student_id, "job_id": job_id}).json()

if path_data["paths"]:
    net = Network(height="400px", width="100%", directed=True, bgcolor="#111111", font_color="white")
    
    # Add Nodes and Edges from multi-hop query
    added_nodes = set()
    for path_item in path_data["paths"]:
        nodes = path_item["path_nodes"]
        for i in range(len(nodes)):
            node = nodes[i]
            if node["id"] not in added_nodes:
                # ✅ FIX: Color green if node ID is in student's current skills set
                color = "#4CAF50" if node["id"] in current_skill_ids else "#FF9800"
                net.add_node(node["id"], label=node["name"], color=color)
                added_nodes.add(node["id"])
            if i > 0:
                prev_node = nodes[i - 1]
                net.add_edge(prev_node["id"], node["id"], title="PREREQUISITE_FOR")
                
    net.save_graph("temp_graph.html")
    with open("temp_graph.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=430)
else:
    st.info("No prerequisite multi-hop paths found for selected role.")

st.markdown("---")

# Recommendations
st.subheader("📚 Recommended Learning Resources")
recs = requests.get(f"{API_URL}/recommendations", params={"job_id": job_id}).json()

rec_col1, rec_col2 = st.columns(2)
with rec_col1:
    st.markdown("#### Recommended Courses")
    for c in recs["courses"]:
        st.write(f"📖 **{c['course']}** ({c['provider']}) → *Teaches {c['skill']}*")

with rec_col2:
    st.markdown("#### Recommended Projects")
    for p in recs["projects"]:
        st.write(f"🛠️ **{p['project']}** [{p['difficulty']}] → *Builds {p['skill']}*")