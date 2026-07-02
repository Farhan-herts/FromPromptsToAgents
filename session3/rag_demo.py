"""
=============================================================================
  Session 3: RAG Demo - Retrieval-Augmented Generation (Console Version)
  University of Hertfordshire AI Workshop
  Time: 14:00 - 14:30
=============================================================================

  What is RAG?
  ------------
  RAG (Retrieval-Augmented Generation) is a technique that improves LLM
  responses by first RETRIEVING relevant information from a knowledge base,
  then providing that information as CONTEXT to the LLM when GENERATING
  an answer.

  Why RAG matters:
  - LLMs have a knowledge cutoff date -- they don't know recent information.
  - LLMs can hallucinate -- they may confidently state incorrect facts.
  - RAG grounds the LLM's response in YOUR data, making answers more
    accurate, verifiable, and up-to-date.

  The RAG Pipeline:
  -----------------
  1. User asks a QUESTION
  2. We VECTORISE the question using TF-IDF (Term Frequency-Inverse
     Document Frequency) -- a classic NLP technique from scikit-learn
  3. We SEARCH our knowledge base by comparing TF-IDF vectors
     (cosine similarity)
  4. We RETRIEVE the top-K most relevant documents
  5. We send the QUESTION + RETRIEVED DOCUMENTS to the LLM
  6. The LLM generates an ANSWER grounded in the retrieved context

  This demo keeps things simple:
  - No vector database (we use scikit-learn's TfidfVectorizer)
  - Small knowledge base (8 short documents about robotics)
  - TF-IDF for similarity search -- no API calls needed for retrieval!
  - Local LLM service for text generation (via llm_client.py)

  TF-IDF vs. Neural Embeddings:
  - TF-IDF is a bag-of-words approach: it counts how important each word
    is in a document relative to the entire corpus.  It is fast, requires
    no API calls, and works well for keyword-heavy queries.
  - Neural embeddings (e.g., from sentence-transformers) capture semantic
    meaning better, but require a model or API.
  - For this workshop, TF-IDF demonstrates the RAG concept clearly
    without any external API dependency for the retrieval step.

  In production, you would typically use a vector database (Pinecone,
  Chroma, Weaviate, Qdrant, pgvector) with neural embeddings for
  higher-quality semantic search at scale.
=============================================================================
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
# scikit-learn provides TfidfVectorizer for converting text to TF-IDF vectors
# and cosine_similarity for measuring how similar two vectors are.
# llm_client wraps our local LLM service (no external AI SDK needed).
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import llm_client


# ===========================================================================
# Step 1: Define our Knowledge Base
# ===========================================================================
# In a real system this could be thousands of documents loaded from PDFs,
# databases, or web scraping.  Here we use a small list of paragraphs about
# robotics topics that are relevant to today's workshop.

KNOWLEDGE_BASE = [
    # Document 0 -- Robot Arms
    (
        "Robot arms, also called manipulators, are the most common type of "
        "industrial robot. A typical robot arm has 6 degrees of freedom (DOF) "
        "allowing it to reach any position and orientation within its workspace. "
        "Key joints include revolute (rotational) and prismatic (linear) types. "
        "Popular models include the Universal Robots UR5e (collaborative) and "
        "the FANUC M-20iA (industrial). Payload capacity, reach, and "
        "repeatability are the primary specifications when choosing an arm."
    ),

    # Document 1 -- Sensors
    (
        "Sensors are essential for robot perception. Common types include: "
        "proximity sensors (detect nearby objects), force/torque sensors "
        "(measure contact forces for delicate tasks), LiDAR (laser-based "
        "distance scanning for mapping), cameras (RGB and depth for computer "
        "vision), encoders (track joint positions), and IMUs (inertial "
        "measurement units for orientation). Sensor fusion -- combining data "
        "from multiple sensor types -- is key to robust perception."
    ),

    # Document 2 -- Autonomous Navigation
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

    # Document 3 -- Computer Vision
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

    # Document 4 -- ROS (Robot Operating System)
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

    # Document 5 -- Safety Standards
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

    # Document 6 -- Gripper Types
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

    # Document 7 -- Conveyor Systems
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

# Give each document a short label for display purposes.
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
# Step 2: Build the TF-IDF Vectorizer
# ===========================================================================
# TF-IDF (Term Frequency-Inverse Document Frequency) is a classic technique
# for converting text into numerical vectors.
#
# How it works:
# - Term Frequency (TF): How often a word appears in a document.
#   More frequent words get higher scores within that document.
# - Inverse Document Frequency (IDF): How rare a word is across ALL
#   documents.  Words that appear in every document (like "the", "is")
#   get lower scores; words unique to a few documents get higher scores.
# - TF-IDF = TF * IDF -- this gives high scores to words that are
#   both frequent in a specific document AND rare across the corpus.
#
# scikit-learn's TfidfVectorizer handles tokenisation, stop-word removal,
# and the TF-IDF calculation in one step.  The result is a sparse matrix
# where each row is a document and each column is a word in the vocabulary.

def build_tfidf_index(documents):
    """
    Build a TF-IDF index over the knowledge base documents.

    Parameters
    ----------
    documents : list[str]
        The document texts to index.

    Returns
    -------
    vectorizer : TfidfVectorizer
        The fitted vectorizer (needed to transform queries later).
    tfidf_matrix : sparse matrix
        The TF-IDF matrix with shape (n_documents, n_vocabulary_terms).
    """
    # Create the vectorizer.
    # - stop_words="english" removes common English words (the, is, at, ...)
    #   so they don't dominate the similarity scores.
    # - The default tokenizer splits on whitespace and punctuation.
    vectorizer = TfidfVectorizer(stop_words="english")

    # fit_transform() learns the vocabulary from the documents AND
    # transforms them into TF-IDF vectors in one step.
    tfidf_matrix = vectorizer.fit_transform(documents)

    return vectorizer, tfidf_matrix


# ===========================================================================
# Step 3: The RAG Pipeline -- Retrieval
# ===========================================================================

def retrieve_relevant_documents(
    query,
    knowledge_base,
    vectorizer,
    tfidf_matrix,
    top_k=3,
):
    """
    Given a user query, find the top-K most relevant documents using
    TF-IDF cosine similarity.

    Steps:
      1. Transform the query into a TF-IDF vector using the SAME
         vectorizer that was fitted on the knowledge base.  This ensures
         the query vector lives in the same vector space as the documents.
      2. Compute cosine similarity between the query vector and every
         document vector.
      3. Sort by similarity (highest first) and return the top K.

    Parameters
    ----------
    query : str
        The user's question.
    knowledge_base : list[str]
        The original document texts.
    vectorizer : TfidfVectorizer
        The fitted TF-IDF vectorizer.
    tfidf_matrix : sparse matrix
        Pre-computed TF-IDF vectors for the knowledge base.
    top_k : int
        How many documents to retrieve.

    Returns
    -------
    list[tuple[int, float, str]]
        A list of (doc_index, similarity_score, doc_text) tuples,
        sorted by similarity descending.
    """
    # Transform the query using the SAME vectorizer (same vocabulary).
    # Note: we use transform(), NOT fit_transform(), because the
    # vocabulary is already learned from the knowledge base.
    query_vector = vectorizer.transform([query])

    # Compute cosine similarity between the query and ALL documents.
    # cosine_similarity returns a 2D array; we want the first (only) row.
    similarities = cosine_similarity(query_vector, tfidf_matrix)[0]

    # Build a list of (index, score, text) and sort by score descending.
    scored_docs = [
        (idx, float(similarities[idx]), knowledge_base[idx])
        for idx in range(len(knowledge_base))
    ]
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    # Return only the top K most relevant documents.
    return scored_docs[:top_k]


# ===========================================================================
# Step 4: The RAG Pipeline -- Generation
# ===========================================================================

def generate_answer_with_rag(query, retrieved_docs):
    """
    Send the user's question PLUS the retrieved documents to the LLM.

    This is the "Augmented Generation" part of RAG.  By including relevant
    documents in the prompt, we give the LLM factual context to draw from,
    reducing hallucination and improving accuracy.

    Parameters
    ----------
    query : str
        The user's original question.
    retrieved_docs : list[tuple[int, float, str]]
        The retrieved documents as (doc_index, score, text) tuples.

    Returns
    -------
    str
        The LLM's generated answer.
    """
    # Build the context string from retrieved documents
    context_parts = []
    for i, (doc_idx, score, doc_text) in enumerate(retrieved_docs, 1):
        context_parts.append(f"[Document {i} - {DOC_LABELS[doc_idx]}]\n{doc_text}")

    context = "\n\n".join(context_parts)

    # Construct the messages with the retrieved context
    system_prompt = (
        "You are a helpful robotics teaching assistant. Answer the student's "
        "question using ONLY the provided context documents. If the context "
        "does not contain enough information, say so. Keep your answer concise "
        "and educational."
    )

    user_prompt = (
        f"Context documents:\n"
        f"---\n"
        f"{context}\n"
        f"---\n\n"
        f"Student question: {query}\n\n"
        f"Please answer based on the context above."
    )

    # Use our local LLM service via llm_client -- no external AI SDK needed!
    return llm_client.chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        temperature=0.3,  # Lower temperature for more factual answers
    )


def generate_answer_without_rag(query):
    """
    Send the user's question to the LLM WITHOUT any retrieved context.

    This serves as a baseline to compare against the RAG-augmented answer,
    demonstrating how much retrieved context improves the response.

    Parameters
    ----------
    query : str
        The user's question.

    Returns
    -------
    str
        The LLM's generated answer (based only on its training data).
    """
    system_prompt = (
        "You are a helpful robotics teaching assistant. Answer the student's "
        "question concisely and educationally."
    )

    return llm_client.chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        max_tokens=500,
        temperature=0.3,
    )


# ===========================================================================
# Step 5: Run the Demo
# ===========================================================================

def run_rag_query(query, knowledge_base, vectorizer, tfidf_matrix):
    """
    Execute the full RAG pipeline for a single query and print results.
    Also runs the same query WITHOUT RAG for comparison.
    """
    print("=" * 70)
    print(f"  QUESTION: {query}")
    print("=" * 70)

    # --- Retrieval Phase ---
    print("\n--- Step 1: Retrieving relevant documents (TF-IDF similarity) ---\n")
    retrieved = retrieve_relevant_documents(
        query, knowledge_base, vectorizer, tfidf_matrix, top_k=3
    )

    for rank, (doc_idx, score, doc_text) in enumerate(retrieved, 1):
        print(f"  [{rank}] {DOC_LABELS[doc_idx]}  (similarity: {score:.4f})")
        # Show a truncated preview of the document
        preview = doc_text[:120] + "..." if len(doc_text) > 120 else doc_text
        print(f"      {preview}")
        print()

    # --- Generation Phase: WITH RAG ---
    print("--- Step 2: Generating answer WITH RAG (LLM + retrieved context) ---\n")
    rag_answer = generate_answer_with_rag(query, retrieved)
    print(f"  ANSWER (with RAG):\n  {rag_answer}\n")

    # --- Generation Phase: WITHOUT RAG ---
    print("--- Step 3: Generating answer WITHOUT RAG (LLM only, no context) ---\n")
    no_rag_answer = generate_answer_without_rag(query)
    print(f"  ANSWER (without RAG):\n  {no_rag_answer}\n")

    print("-" * 70)
    print()


def main():
    """
    Main entry point for the RAG demo.
    """
    print()
    print("=" * 70)
    print("  RAG DEMO: Robotics Knowledge Base")
    print("  Session 3 - University of Hertfordshire AI Workshop")
    print("=" * 70)
    print()

    # ------------------------------------------------------------------
    # Check LLM service health
    # ------------------------------------------------------------------
    print("Checking LLM service health...")
    health = llm_client.check_health()
    if health.get("status") == "unreachable":
        print(f"  WARNING: LLM service is unreachable: {health.get('error')}")
        print("  The retrieval step will still work, but generation will fail.")
        print("  Make sure your .env file has the correct LLM_SERVICE_URL and LLM_API_TOKEN.")
    else:
        print(f"  LLM service status: {health.get('status')}")
        print(f"  Model loaded: {health.get('model_loaded')}")
    print()

    # ------------------------------------------------------------------
    # Phase 1: Build the TF-IDF index over the knowledge base
    # ------------------------------------------------------------------
    # Unlike neural embeddings which require an API call, TF-IDF runs
    # entirely locally using scikit-learn -- fast and free!
    print("Building TF-IDF index over knowledge base...")
    print(f"  - {len(KNOWLEDGE_BASE)} documents to index")

    vectorizer, tfidf_matrix = build_tfidf_index(KNOWLEDGE_BASE)

    print(f"  - Vocabulary size: {len(vectorizer.vocabulary_)} unique terms")
    print(f"  - TF-IDF matrix shape: {tfidf_matrix.shape}")
    print(f"    (rows = documents, columns = vocabulary terms)")
    print("  Done!\n")

    # ------------------------------------------------------------------
    # Phase 2: Run example queries through the RAG pipeline
    # ------------------------------------------------------------------
    example_queries = [
        "What sensors do I need for a pick-and-place robot?",
        "How do I ensure robot safety in a factory?",
        "What is ROS and how does it help in robotics?",
    ]

    for query in example_queries:
        run_rag_query(query, KNOWLEDGE_BASE, vectorizer, tfidf_matrix)

    # ------------------------------------------------------------------
    # Bonus: Let the user ask their own questions
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  TRY IT YOURSELF")
    print("  Type a robotics question (or 'quit' to exit)")
    print("=" * 70 + "\n")

    while True:
        user_input = input("Your question: ").strip()
        if user_input.lower() in ("quit", "exit", "q", ""):
            print("Goodbye!")
            break
        run_rag_query(user_input, KNOWLEDGE_BASE, vectorizer, tfidf_matrix)


if __name__ == "__main__":
    main()
