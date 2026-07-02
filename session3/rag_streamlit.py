"""
=============================================================================
  Session 3: RAG Demo - Streamlit Interactive Version
  University of Hertfordshire AI Workshop
  Time: 14:00 - 14:30
=============================================================================

  This is the interactive Streamlit version of the RAG demo.  It provides
  a side-by-side comparison of LLM answers WITH and WITHOUT retrieved
  context, powerfully demonstrating why RAG matters.

  Retrieval is handled by scikit-learn's TF-IDF vectorizer (no API needed
  for the search step).  Generation uses the local LLM service via
  llm_client.py.

  Run with:
      streamlit run rag_streamlit.py
=============================================================================
"""

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import llm_client


# ===========================================================================
# Knowledge Base -- same robotics documents as the console demo
# ===========================================================================

KNOWLEDGE_BASE = [
    (
        "Robot arms, also called manipulators, are the most common type of "
        "industrial robot. A typical robot arm has 6 degrees of freedom (DOF) "
        "allowing it to reach any position and orientation within its workspace. "
        "Key joints include revolute (rotational) and prismatic (linear) types. "
        "Popular models include the Universal Robots UR5e (collaborative) and "
        "the FANUC M-20iA (industrial). Payload capacity, reach, and "
        "repeatability are the primary specifications when choosing an arm."
    ),
    (
        "Sensors are essential for robot perception. Common types include: "
        "proximity sensors (detect nearby objects), force/torque sensors "
        "(measure contact forces for delicate tasks), LiDAR (laser-based "
        "distance scanning for mapping), cameras (RGB and depth for computer "
        "vision), encoders (track joint positions), and IMUs (inertial "
        "measurement units for orientation). Sensor fusion -- combining data "
        "from multiple sensor types -- is key to robust perception."
    ),
    (
        "Autonomous navigation allows mobile robots to move through environments "
        "without human control. The key components are: (1) Localisation -- "
        "knowing where the robot is, often using SLAM (Simultaneous Localisation "
        "and Mapping); (2) Path planning -- computing a collision-free route "
        "using algorithms like A*, RRT, or Dijkstra; (3) Obstacle avoidance -- "
        "reacting to unexpected objects using LiDAR or depth cameras in real "
        "time. The ROS Navigation Stack (Nav2) provides ready-made packages "
        "for all three components."
    ),
    (
        "Computer vision enables robots to understand their surroundings from "
        "camera data. Core tasks include: object detection (finding objects in "
        "images using models like YOLO or SSD), object recognition (identifying "
        "what an object is), pose estimation (determining an object's 3D "
        "position and orientation), and semantic segmentation (labelling every "
        "pixel in an image). Deep learning, especially convolutional neural "
        "networks (CNNs), has revolutionised computer vision performance in "
        "robotics applications."
    ),
    (
        "ROS (Robot Operating System) is an open-source middleware framework "
        "for building robot software. Despite its name, it is not an operating "
        "system but a collection of tools, libraries, and conventions. ROS uses "
        "a publisher-subscriber model for communication between nodes (processes). "
        "Key concepts include: topics (named message channels), services "
        "(request-reply calls), actions (long-running tasks with feedback), and "
        "the parameter server. ROS 2 (the latest version) adds real-time "
        "support, improved security, and multi-robot capabilities."
    ),
    (
        "Robot safety in industrial settings is governed by standards such as "
        "ISO 10218 (industrial robots) and ISO/TS 15066 (collaborative robots). "
        "Key safety measures include: emergency stop (e-stop) buttons, safety-rated "
        "monitored speed and force limits, safety light curtains and laser "
        "scanners that detect humans entering the work zone, physical fencing "
        "for high-speed robots, and risk assessments before deployment. "
        "Collaborative robots (cobots) are designed to work alongside humans "
        "safely by limiting force and speed on contact."
    ),
    (
        "Grippers are end-effectors that allow robots to grasp and manipulate "
        "objects. The main types are: (1) Mechanical grippers -- two or three "
        "finger designs that physically clamp objects, good for rigid parts; "
        "(2) Vacuum grippers -- use suction cups and negative pressure, ideal "
        "for flat surfaces like boxes or sheets; (3) Magnetic grippers -- for "
        "ferrous metal parts; (4) Soft grippers -- made of flexible materials "
        "that conform to object shapes, great for delicate items like food. "
        "Gripper selection depends on object shape, weight, material, and the "
        "required cycle time."
    ),
    (
        "Conveyor systems are used in manufacturing and logistics to transport "
        "parts between workstations. Common types include belt conveyors, roller "
        "conveyors, and chain conveyors. When integrated with robots, conveyors "
        "enable high-throughput pick-and-place operations. Conveyor tracking -- "
        "where the robot synchronises its motion with a moving belt -- requires "
        "an encoder on the conveyor and precise timing. Vision-guided conveyor "
        "picking uses a camera to detect objects on the belt and calculate pick "
        "points in real time, enabling flexible handling of varied products."
    ),
]

DOC_LABELS = [
    "Robot Arms",
    "Sensors",
    "Autonomous Navigation",
    "Computer Vision",
    "ROS (Robot Operating System)",
    "Safety Standards",
    "Gripper Types",
    "Conveyor Systems",
]


# ===========================================================================
# Helper Functions
# ===========================================================================

@st.cache_resource
def build_tfidf_index():
    """
    Build the TF-IDF index over the knowledge base.

    Cached by Streamlit so it only runs once per session -- the vectorizer
    and matrix are reused for every query.  Unlike neural embeddings this
    requires zero API calls and runs instantly.
    """
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(KNOWLEDGE_BASE)
    return vectorizer, tfidf_matrix


def retrieve_top_k(query, vectorizer, tfidf_matrix, top_k=3):
    """
    Find the top-K most similar documents to the query using TF-IDF
    cosine similarity.

    Returns a list of (doc_index, similarity_score) tuples sorted
    by similarity descending.
    """
    # Transform the query into the same TF-IDF vector space as the documents.
    query_vector = vectorizer.transform([query])

    # Compute cosine similarity between the query and ALL documents.
    similarities = cosine_similarity(query_vector, tfidf_matrix)[0]

    # Build scored list and sort descending.
    scored = [(idx, float(similarities[idx])) for idx in range(len(KNOWLEDGE_BASE))]
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:top_k]


def ask_llm_with_context(question, context_docs):
    """Generate an answer using the LLM WITH retrieved context (RAG)."""
    context_parts = []
    for i, (doc_idx, score) in enumerate(context_docs, 1):
        context_parts.append(
            f"[Document {i} - {DOC_LABELS[doc_idx]}]\n{KNOWLEDGE_BASE[doc_idx]}"
        )
    context = "\n\n".join(context_parts)

    return llm_client.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful robotics teaching assistant. Answer the "
                    "student's question using ONLY the provided context documents. "
                    "If the context does not contain enough information, say so. "
                    "Keep your answer concise and educational."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context documents:\n---\n{context}\n---\n\n"
                    f"Student question: {question}\n\n"
                    f"Please answer based on the context above."
                ),
            },
        ],
        max_tokens=500,
        temperature=0.3,
    )


def ask_llm_without_context(question):
    """Generate an answer using the LLM WITHOUT any retrieved context."""
    return llm_client.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful robotics teaching assistant. Answer the "
                    "student's question concisely and educationally."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        max_tokens=500,
        temperature=0.3,
    )


# ===========================================================================
# Streamlit UI
# ===========================================================================

def main():
    st.set_page_config(
        page_title="RAG Demo: Robotics Knowledge Base",
        layout="wide",
    )

    st.title("RAG Demo: Robotics Knowledge Base")
    st.caption("Session 3 -- University of Hertfordshire AI Workshop")

    st.markdown(
        """
        **Retrieval-Augmented Generation (RAG)** improves LLM answers by first
        searching a knowledge base for relevant information, then including that
        information as context when generating a response.  This demo lets you
        compare answers **with** and **without** RAG side by side.

        Retrieval uses **TF-IDF** (scikit-learn) for similarity search --
        no API calls needed for the search step.  Generation uses the local
        LLM service.
        """
    )

    # -----------------------------------------------------------------------
    # Sidebar: Show the knowledge base documents + LLM health
    # -----------------------------------------------------------------------
    with st.sidebar:
        st.header("Knowledge Base")
        st.markdown(
            f"This demo uses **{len(KNOWLEDGE_BASE)} documents** about robotics."
        )

        for idx, (label, doc) in enumerate(zip(DOC_LABELS, KNOWLEDGE_BASE)):
            with st.expander(f"{idx + 1}. {label}"):
                st.write(doc)

        st.divider()

        # LLM service health check
        st.header("LLM Service Status")
        health = llm_client.check_health()
        if health.get("status") == "unreachable":
            st.error(f"LLM service unreachable: {health.get('error', 'unknown')}")
        else:
            st.success(f"Status: {health.get('status', 'unknown')}")
            st.write(f"Model loaded: {health.get('model_loaded', 'unknown')}")

        st.divider()

        st.markdown(
            "**How it works:**\n"
            "1. Documents are converted to TF-IDF vectors (scikit-learn)\n"
            "2. Your question is also converted to a TF-IDF vector\n"
            "3. We find the closest documents using cosine similarity\n"
            "4. Those documents become context for the LLM"
        )

    # -----------------------------------------------------------------------
    # Build the TF-IDF index (cached -- only runs once)
    # -----------------------------------------------------------------------
    vectorizer, tfidf_matrix = build_tfidf_index()

    # -----------------------------------------------------------------------
    # User input
    # -----------------------------------------------------------------------
    st.subheader("Ask a Question")

    # Provide some example questions as quick-select buttons
    example_questions = [
        "What sensors do I need for a pick-and-place robot?",
        "How do I ensure robot safety in a factory?",
        "What is ROS and how does it help in robotics?",
    ]

    selected_example = None
    cols = st.columns(len(example_questions))
    for i, (col, q) in enumerate(zip(cols, example_questions)):
        with col:
            if st.button(f"Example {i + 1}", key=f"ex_{i}", use_container_width=True):
                selected_example = q

    # Text input -- pre-fill with selected example if a button was clicked
    question = st.text_input(
        "Type your robotics question:",
        value=selected_example if selected_example else "",
        placeholder="e.g., What types of grippers are available for robots?",
    )

    if question:
        # -------------------------------------------------------------------
        # Step 1: Retrieve relevant documents using TF-IDF similarity
        # -------------------------------------------------------------------
        with st.spinner("Searching knowledge base (TF-IDF)..."):
            top_docs = retrieve_top_k(question, vectorizer, tfidf_matrix, top_k=3)

        # -------------------------------------------------------------------
        # Display retrieved documents with similarity scores
        # -------------------------------------------------------------------
        st.subheader("Retrieved Documents")
        st.markdown("These are the top 3 documents most relevant to your question:")

        for rank, (doc_idx, score) in enumerate(top_docs, 1):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(
                    label=f"#{rank}: {DOC_LABELS[doc_idx]}",
                    value=f"{score:.4f}",
                    delta=None,
                )
            with col2:
                # Show a progress bar representing the similarity score
                st.progress(
                    min(max(score, 0.0), 1.0),
                    text=f"Cosine similarity: {score:.4f}",
                )
                with st.expander("Show full document"):
                    st.write(KNOWLEDGE_BASE[doc_idx])

        st.divider()

        # -------------------------------------------------------------------
        # Step 2: Generate answers -- WITH and WITHOUT RAG side by side
        # -------------------------------------------------------------------
        st.subheader("Answer Comparison")

        col_rag, col_no_rag = st.columns(2)

        with col_rag:
            st.markdown("#### With RAG")
            st.caption("LLM receives your question + the 3 retrieved documents")
            with st.spinner("Generating RAG answer..."):
                rag_answer = ask_llm_with_context(question, top_docs)
            st.success(rag_answer)

        with col_no_rag:
            st.markdown("#### Without RAG")
            st.caption("LLM receives ONLY your question (no context)")
            with st.spinner("Generating baseline answer..."):
                no_rag_answer = ask_llm_without_context(question)
            st.info(no_rag_answer)

        # -------------------------------------------------------------------
        # Educational note
        # -------------------------------------------------------------------
        st.divider()
        st.markdown(
            """
            **What to notice:**
            - The RAG answer is grounded in specific facts from our knowledge base.
            - The non-RAG answer relies entirely on the LLM's training data, which
              may be less specific, less accurate, or missing details entirely.
            - In production, RAG lets you control *exactly* what information the LLM
              uses -- crucial for enterprise applications where accuracy matters.
            - This demo uses TF-IDF for retrieval (keyword-based).  Production
              systems typically use neural embeddings + vector databases for
              better semantic understanding.
            """
        )


if __name__ == "__main__":
    main()
