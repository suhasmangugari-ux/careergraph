# CareerGraph: AI Skill Path Explorer

It can be hard to keep track of the many technology career paths. Having an idea of what skills to learn is challenging enough, but knowing what order to learn them in, and what skills should be taught first and which ones second, and so on, and what skills should come before others and which skills will follow, is even harder.

**CareerGraph** Solves this by creating individual and step-by-step skill sequences. Rather than providing a set of skills that are missing, it creates a visual graph that is interactive, allowing students to view and follow required pathways to different skills that will lead them to the skills required for a specific job role.

---

## 💡 Key Features

* **Real-Time Career Readiness Score**: Quickly assess your students' ability to work in a particular role within a desired career path based on your current skills.

* **Clear Skill Gap Analysis**: The most important missing skill areas are identified and prioritized by the importance for the role.
* **Interactive Multi-Hop Skill Traversal**: Explore a visual map showing prerequisite skill pathways.
* 🟢 **Green Nodes**: Skills you already master.
* 🟠 **Orange Nodes**: Target skills and missing prerequisites you need to bridge the gap.


* **Curated Learning Pathways**: Get course and practical recommendations that are customized to your needs to learn the necessary skills in the fastest possible time.
---

## 🚀 Live Demo

You can try the live application here:

* **Frontend Dashboard**: [https://careergraphfrontend-production.up.railway.app](https://careergraphfrontend-production.up.railway.app)
* **API Documentation**: [https://careergraph-production.up.railway.app/docs](https://careergraph-production.up.railway.app/docs)
---

## How It Works (High-Level)

1. **Select Profile & Target Role**: Pick a student profile and choose a target career path (e.g., Data Scientist, Backend Engineer).
2. **Graph Traversal**: The backend searches through a graph database to identify multi-hop prerequisite pathways connecting your current skills to the target role requirements.
3. **Interactive Path Visualization**: The Streamlit interface renders an interactive graph powered by Pyvis, letting you click, drag, and inspect your learning trajectory.
4. **Actionable Recommendations**: Get targeted course and project suggestions designed specifically for your missing skills.

---

## Running Locally

### 1. Clone & Setup

```bash
git clone https://github.com/suhasmangugari-ux/careergraph.git
cd careergraph
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

```

### 2. Start Backend

```bash
uvicorn backend.app:app --reload

```

### 3. Start Frontend

```bash
streamlit run frontend/ui.py

```
