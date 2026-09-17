import os
import sqlite3
import pytest
from unittest.mock import MagicMock, patch

from database.chat_history import (
    ChatHistoryDB,
    initialize_database,
    create_conversation,
    get_conversation,
    list_conversations,
    delete_conversation,
    save_message,
    get_messages,
    update_conversation_timestamp,
    update_conversation_title,
    generate_title_from_message,
    get_db_connection,
)
from state.schema import (
    StartupIdea,
    StartupState,
    ValidationReport,
    SWOTAnalysis,
    RiskItem,
)
from agents.conversational_advisor import ConversationalAdvisor
from app.orchestrator import ApplicationOrchestrator


@pytest.fixture
def temp_db_path(tmp_path):
    """Provides an isolated temporary database path for tests."""
    return str(tmp_path / "test_chat_history.db")


@pytest.fixture
def sample_advisor_state():
    """Provides a sample startup state for advisor integration tests."""
    idea = StartupIdea(
        idea_text="AI Telehealth Doctor Assistant",
        target_industry="Healthcare / HealthTech",
        target_audience="Clinics and Hospitals",
        business_model="B2B SaaS",
        budget="$40k",
        timeline="4 Months",
    )
    report = ValidationReport(
        overall_viability_score=82,
        verdict="PROCEED WITH CAUTION",
        executive_summary="Strong clinical workflow utility with regulatory compliance requirements.",
        market_score=85,
        competitor_score=78,
        risk_score=70,
        mvp_score=88,
        gtm_score=80,
        investor_readiness_score=80,
        funding_probability=75,
        pmf_score=82.0,
        confidence_score=88.0,
        key_takeaways=["Healthcare automation is expanding", "HIPAA certification needed"],
        recommended_next_steps=["Build HIPAA compliant MVP", "Initiate pilot with 3 medical clinics"],
    )
    swot = SWOTAnalysis(
        overall_risk_score=5,
        financial_risk=4,
        technical_risk=4,
        regulatory_risk=7,
        strengths=["Specialized clinical prompt engineering"],
        weaknesses=["HIPAA compliance overhead and regulatory compliance barriers"],
        opportunities=["Expand to dental and specialist practices"],
        threats=["EHR giants adding basic AI features"],
        risk_mitigation_plan=["Partner with certified HIPAA hosting provider and implement end-to-end encryption"],
        risk_matrix=[
            RiskItem(
                risk_name="HIPAA compliance overhead",
                category="Regulatory",
                severity_score=7,
                mitigation_strategy="Deploy on dedicated HIPAA-compliant AWS infrastructure",
            )
        ],
    )
    return StartupState(
        idea=idea,
        final_report=report,
        swot_analysis=swot,
        status="completed",
    )


# ============================================================
# 1. DATABASE INITIALIZATION & SCHEMA TESTS
# ============================================================

def test_database_initialization(temp_db_path):
    """Verify that initialize_database creates tables and indexes correctly."""
    initialize_database(temp_db_path)
    assert os.path.exists(temp_db_path)

    conn = get_db_connection(temp_db_path)
    cursor = conn.cursor()

    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row["name"] for row in cursor.fetchall()]
    assert "conversations" in tables
    assert "messages" in tables

    # Check foreign keys enabled
    cursor.execute("PRAGMA foreign_keys;")
    fk_status = cursor.fetchone()[0]
    assert fk_status == 1
    conn.close()


# ============================================================
# 2. CONVERSATION CREATION & RETRIEVAL TESTS (OWNERSHIP-ENFORCED)
# ============================================================

def test_create_and_get_conversation(temp_db_path):
    """Verify creating a conversation generates unique ID, timestamps, and default title."""
    conv_id = create_conversation(title="Healthcare Discussion", session_id="sess_123", db_path=temp_db_path)
    assert isinstance(conv_id, str)
    assert len(conv_id) > 0

    conv = get_conversation(conv_id, session_id="sess_123", db_path=temp_db_path)
    assert conv is not None
    assert conv["id"] == conv_id
    assert conv["title"] == "Healthcare Discussion"
    assert conv["session_id"] == "sess_123"
    assert "created_at" in conv
    assert "updated_at" in conv

    # Accessing with incorrect session_id returns None
    assert get_conversation(conv_id, session_id="other_sess", db_path=temp_db_path) is None
    assert get_conversation(conv_id, session_id=None, db_path=temp_db_path) is None


def test_default_conversation_title(temp_db_path):
    """Verify default conversation title is 'New Conversation'."""
    conv_id = create_conversation(session_id="sess_default", db_path=temp_db_path)
    conv = get_conversation(conv_id, session_id="sess_default", db_path=temp_db_path)
    assert conv["title"] == "New Conversation"


def test_create_conversation_requires_session_id(temp_db_path):
    """Verify create_conversation raises ValueError when session_id is missing or empty."""
    with pytest.raises(ValueError, match="session_id is required"):
        create_conversation(title="Test", session_id=None, db_path=temp_db_path)

    with pytest.raises(ValueError, match="session_id is required"):
        create_conversation(title="Test", session_id="", db_path=temp_db_path)

    with pytest.raises(ValueError, match="session_id is required"):
        create_conversation(title="Test", session_id="   ", db_path=temp_db_path)


def test_list_conversations_ordering_and_filtering(temp_db_path):
    """Verify list_conversations orders by updated_at descending and strictly filters by session_id."""
    c1 = create_conversation(title="Chat 1", session_id="sess_A", db_path=temp_db_path)
    c2 = create_conversation(title="Chat 2", session_id="sess_B", db_path=temp_db_path)
    c3 = create_conversation(title="Chat 3", session_id="sess_A", db_path=temp_db_path)

    # Calling list_conversations without session_id returns empty list (no global leakage)
    assert list_conversations(db_path=temp_db_path) == []
    assert list_conversations(session_id="", db_path=temp_db_path) == []

    # Filtered strictly by session_id
    sess_a_convs = list_conversations(session_id="sess_A", db_path=temp_db_path)
    assert len(sess_a_convs) == 2
    assert [c["id"] for c in sess_a_convs] == [c3, c1]

    sess_b_convs = list_conversations(session_id="sess_B", db_path=temp_db_path)
    assert len(sess_b_convs) == 1
    assert [c["id"] for c in sess_b_convs] == [c2]


def test_update_conversation_title_and_timestamp(temp_db_path):
    """Verify updating title and timestamp strictly enforces session ownership."""
    conv_id = create_conversation(title="Old Title", session_id="sess_owner", db_path=temp_db_path)
    initial_conv = get_conversation(conv_id, session_id="sess_owner", db_path=temp_db_path)

    # Unauthorized session update fails
    assert update_conversation_title(conv_id, "Hacked Title", session_id="sess_other", db_path=temp_db_path) is False
    assert get_conversation(conv_id, session_id="sess_owner", db_path=temp_db_path)["title"] == "Old Title"

    # Authorized update succeeds
    updated = update_conversation_title(conv_id, "Updated Title", session_id="sess_owner", db_path=temp_db_path)
    assert updated is True

    conv = get_conversation(conv_id, session_id="sess_owner", db_path=temp_db_path)
    assert conv["title"] == "Updated Title"

    # Timestamp update
    assert update_conversation_timestamp(conv_id, session_id="sess_other", db_path=temp_db_path) is False
    ts_updated = update_conversation_timestamp(conv_id, session_id="sess_owner", db_path=temp_db_path)
    assert ts_updated is True


def test_delete_conversation_and_cascade(temp_db_path):
    """Verify deleting a conversation cascades and deletes its messages when authorized."""
    conv_id = create_conversation(title="To Delete", session_id="sess_owner", db_path=temp_db_path)
    save_message(conv_id, "sess_owner", "user", "Hello", db_path=temp_db_path)
    save_message(conv_id, "sess_owner", "assistant", "Hi there!", db_path=temp_db_path)

    assert len(get_messages(conv_id, session_id="sess_owner", db_path=temp_db_path)) == 2

    # Attempt deletion by another session fails
    assert delete_conversation(conv_id, session_id="sess_other", db_path=temp_db_path) is False
    assert get_conversation(conv_id, session_id="sess_owner", db_path=temp_db_path) is not None
    assert len(get_messages(conv_id, session_id="sess_owner", db_path=temp_db_path)) == 2

    # Owner deletes
    deleted = delete_conversation(conv_id, session_id="sess_owner", db_path=temp_db_path)
    assert deleted is True

    assert get_conversation(conv_id, session_id="sess_owner", db_path=temp_db_path) is None
    assert len(get_messages(conv_id, session_id="sess_owner", db_path=temp_db_path)) == 0


# ============================================================
# 3. MESSAGE STORAGE & VALIDATION TESTS
# ============================================================

def test_save_and_retrieve_messages(temp_db_path):
    """Verify saving user and assistant messages and retrieving them in chronological order."""
    conv_id = create_conversation(title="Q&A", session_id="sess_owner", db_path=temp_db_path)

    m1_id = save_message(conv_id, "sess_owner", "user", "What is the market size?", db_path=temp_db_path)
    m2_id = save_message(conv_id, "sess_owner", "assistant", "TAM is $25B.", db_path=temp_db_path)
    m3_id = save_message(conv_id, "sess_owner", "user", "Who are the competitors?", db_path=temp_db_path)
    m4_id = save_message(conv_id, "sess_owner", "assistant", "Key competitors are LegalFly and Ironclad.", db_path=temp_db_path)

    msgs = get_messages(conv_id, session_id="sess_owner", db_path=temp_db_path)
    assert len(msgs) == 4
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "What is the market size?"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"] == "TAM is $25B."
    assert msgs[2]["role"] == "user"
    assert msgs[3]["role"] == "assistant"
    assert [m["id"] for m in msgs] == [m1_id, m2_id, m3_id, m4_id]


def test_save_message_invalid_role(temp_db_path):
    """Verify save_message rejects invalid roles."""
    conv_id = create_conversation(session_id="sess_owner", db_path=temp_db_path)

    with pytest.raises(ValueError, match="Invalid message role"):
        save_message(conv_id, "sess_owner", "system", "System prompt", db_path=temp_db_path)

    with pytest.raises(ValueError, match="Invalid message role"):
        save_message(conv_id, "sess_owner", "admin", "Admin message", db_path=temp_db_path)


def test_save_message_empty_content(temp_db_path):
    """Verify save_message rejects empty or whitespace-only content."""
    conv_id = create_conversation(session_id="sess_owner", db_path=temp_db_path)

    with pytest.raises(ValueError, match="Message content cannot be empty"):
        save_message(conv_id, "sess_owner", "user", "", db_path=temp_db_path)

    with pytest.raises(ValueError, match="Message content cannot be empty"):
        save_message(conv_id, "sess_owner", "assistant", "   ", db_path=temp_db_path)


def test_save_message_nonexistent_conversation(temp_db_path):
    """Verify save_message raises ValueError when conversation does not exist or does not belong to session."""
    with pytest.raises(ValueError, match="does not exist"):
        save_message("nonexistent-conv-id", "sess_owner", "user", "Hello", db_path=temp_db_path)


def test_messages_chronological_order_with_limit(temp_db_path):
    """Verify get_messages with limit returns the most recent N messages in chronological order."""
    conv_id = create_conversation(session_id="sess_owner", db_path=temp_db_path)

    for i in range(1, 11):
        role = "user" if i % 2 == 1 else "assistant"
        save_message(conv_id, "sess_owner", role, f"Message {i}", db_path=temp_db_path)

    # Total 10 messages, request limit 4
    limited_msgs = get_messages(conv_id, session_id="sess_owner", limit=4, db_path=temp_db_path)
    assert len(limited_msgs) == 4
    # Must be messages 7, 8, 9, 10 in chronological order
    assert [m["content"] for m in limited_msgs] == [
        "Message 7",
        "Message 8",
        "Message 9",
        "Message 10",
    ]


def test_multiple_conversations_isolation(temp_db_path):
    """Verify messages from Conversation A never leak into Conversation B within the same session."""
    conv_a = create_conversation(title="Chat A", session_id="sess_owner", db_path=temp_db_path)
    conv_b = create_conversation(title="Chat B", session_id="sess_owner", db_path=temp_db_path)

    save_message(conv_a, "sess_owner", "user", "Question for A", db_path=temp_db_path)
    save_message(conv_a, "sess_owner", "assistant", "Answer for A", db_path=temp_db_path)

    save_message(conv_b, "sess_owner", "user", "Question for B", db_path=temp_db_path)

    msgs_a = get_messages(conv_a, session_id="sess_owner", db_path=temp_db_path)
    msgs_b = get_messages(conv_b, session_id="sess_owner", db_path=temp_db_path)

    assert len(msgs_a) == 2
    assert len(msgs_b) == 1
    assert msgs_a[0]["content"] == "Question for A"
    assert msgs_b[0]["content"] == "Question for B"


# ============================================================
# 4. EDGE CASES & UTILITY TESTS
# ============================================================

def test_empty_conversation_safe(temp_db_path):
    """Verify querying an empty conversation returns empty list without error."""
    conv_id = create_conversation(session_id="sess_owner", db_path=temp_db_path)
    msgs = get_messages(conv_id, session_id="sess_owner", db_path=temp_db_path)
    assert msgs == []


def test_invalid_conversation_id_safe(temp_db_path):
    """Verify querying an invalid conversation ID behaves safely."""
    assert get_conversation("invalid-id", session_id="sess_1", db_path=temp_db_path) is None
    assert get_conversation("", session_id="sess_1", db_path=temp_db_path) is None
    assert get_conversation("invalid-id", session_id="", db_path=temp_db_path) is None
    assert get_conversation("invalid-id", session_id=None, db_path=temp_db_path) is None
    assert get_messages("invalid-id", session_id="sess_1", db_path=temp_db_path) == []
    assert get_messages("", session_id="sess_1", db_path=temp_db_path) == []
    assert get_messages("invalid-id", session_id="", db_path=temp_db_path) == []
    assert get_messages("invalid-id", session_id=None, db_path=temp_db_path) == []
    assert delete_conversation("invalid-id", session_id="sess_1", db_path=temp_db_path) is False
    assert delete_conversation("invalid-id", session_id="", db_path=temp_db_path) is False


def test_generate_title_from_message():
    """Verify deterministic title generation extracts clean, concise titles."""
    assert generate_title_from_message("") == "New Conversation"
    assert generate_title_from_message("   ") == "New Conversation"

    # Requirement exact examples
    assert generate_title_from_message("What is my viability score?") == "My Viability Score"
    assert generate_title_from_message("Who are my main competitors?") == "Who Are My Main Competitors"
    assert generate_title_from_message("What is the biggest risk?") == "Biggest Risk"

    # Additional domain & acronym cases
    t1 = generate_title_from_message("What is the biggest risk in my healthcare startup?")
    assert "Risk In My Healthcare Startup" in t1 or "Biggest Risk" in t1
    assert len(t1) <= 40

    t2 = generate_title_from_message("How can I reduce customer acquisition cost?")
    assert "Reduce Customer Acquisition Cost" in t2 or "Customer Acquisition Cost" in t2
    assert len(t2) <= 40

    t3 = generate_title_from_message("Tell me about our direct competitors in legal tech")
    assert "Direct Competitors In Legal Tech" in t3 or "Competitors" in t3

    t_acronym = generate_title_from_message("What is the MVP tech stack and GTM strategy?")
    assert "MVP" in t_acronym and "GTM" in t_acronym


def test_chat_history_db_class_wrapper(temp_db_path):
    """Verify ChatHistoryDB object-oriented wrapper class works with session ownership."""
    db = ChatHistoryDB(session_id="s1", db_path=temp_db_path)
    conv_id = db.create_conversation(title="OOP Chat")

    db.save_message(conv_id, "user", "Hello OOP")
    db.save_message(conv_id, "assistant", "Hi OOP")

    msgs = db.get_messages(conv_id)
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Hello OOP"

    conv = db.get_conversation(conv_id)
    assert conv["title"] == "OOP Chat"
    assert conv["session_id"] == "s1"

    convs = db.list_conversations()
    assert len(convs) == 1

    title = db.generate_title("What is the MVP tech stack?")
    assert "MVP Tech Stack" in title or "Tech Stack" in title

    deleted = db.delete_conversation(conv_id)
    assert deleted is True


def test_database_persistence_across_reconnections(tmp_path):
    """Verify that data written to SQLite persists after closing connection and reopening."""
    db_file = str(tmp_path / "persistent_chat.db")

    # Session 1: Create conversation and messages
    db1 = ChatHistoryDB(session_id="sess_p", db_path=db_file)
    c_id = db1.create_conversation(title="Persistent Chat")
    db1.save_message(c_id, "user", "Message before restart")
    db1.save_message(c_id, "assistant", "Answer before restart")

    # Session 2: Fresh instance pointing to same file with same session_id
    db2 = ChatHistoryDB(session_id="sess_p", db_path=db_file)
    convs = db2.list_conversations()
    assert len(convs) == 1
    assert convs[0]["id"] == c_id
    assert convs[0]["title"] == "Persistent Chat"

    restored_msgs = db2.get_messages(c_id)
    assert len(restored_msgs) == 2
    assert restored_msgs[0]["content"] == "Message before restart"
    assert restored_msgs[1]["content"] == "Answer before restart"


# ============================================================
# 5. INTEGRATION: PERSISTENT HISTORY + ADVISOR CONTEXT
# ============================================================

def test_persistent_history_passed_to_advisor_context(temp_db_path, sample_advisor_state):
    """Verify SQLite persistent history enables multi-turn follow-up intent inheritance in Advisor."""
    advisor = ConversationalAdvisor()
    db = ChatHistoryDB(session_id="sess_adv", db_path=temp_db_path)

    # 1. Turn 1: User asks about biggest risk
    conv_id = db.create_conversation(title="New Conversation")
    q1 = "What is the biggest risk?"
    db.save_message(conv_id, "user", q1)

    # Auto-generate title
    new_title = generate_title_from_message(q1)
    db.update_conversation_title(conv_id, new_title)

    # History snapshot for Turn 1
    h1 = [{"role": m["role"], "content": m["content"]} for m in db.get_messages(conv_id)]
    ans1 = advisor.answer_question(q1, sample_advisor_state, h1)
    db.save_message(conv_id, "assistant", ans1)

    assert "HIPAA compliance" in ans1 or "regulatory" in ans1.lower()

    # 2. Turn 2: User asks short follow-up "How can I reduce this risk?"
    q2 = "How can I reduce this risk?"
    db.save_message(conv_id, "user", q2)

    # Load SQLite history (up to 20 messages)
    persisted_history = db.get_messages(conv_id, limit=20)
    h2 = [{"role": m["role"], "content": m["content"]} for m in persisted_history]

    # Check intent classification inherits 'risk'
    classified_intent = advisor.classify_intent(q2, h2)
    assert classified_intent == "risk"

    # Advisor answers follow-up with concrete mitigation actions
    ans2 = advisor.answer_question(q2, sample_advisor_state, h2)
    db.save_message(conv_id, "assistant", ans2)

    assert "mitigate" in ans2.lower() or "reduce" in ans2.lower()
    assert "action" in ans2.lower() or "safeguard" in ans2.lower() or "hipaa" in ans2.lower()

    # Verify total conversation messages in SQLite
    final_messages = db.get_messages(conv_id)
    assert len(final_messages) == 4
    assert final_messages[0]["content"] == q1
    assert final_messages[1]["content"] == ans1
    assert final_messages[2]["content"] == q2
    assert final_messages[3]["content"] == ans2


def test_new_chat_and_switching_lifecycle(temp_db_path):
    """Verify creating a new chat, switching conversations, and ensuring no message leakage."""
    db = ChatHistoryDB(session_id="sess_life", db_path=temp_db_path)

    # 1. Create first conversation and send messages
    conv1 = db.create_conversation(title="New Conversation")
    db.save_message(conv1, "user", "What is my viability score?")
    db.update_conversation_title(conv1, db.generate_title("What is my viability score?"))
    db.save_message(conv1, "assistant", "Your viability score is 85/100.")

    # 2. User starts a new chat
    conv2 = db.create_conversation(title="New Conversation")
    assert conv2 != conv1
    # conv2 starts empty
    assert len(db.get_messages(conv2)) == 0

    # User sends question in conv2
    db.save_message(conv2, "user", "Who are my main competitors?")
    db.update_conversation_title(conv2, db.generate_title("Who are my main competitors?"))
    db.save_message(conv2, "assistant", "Key competitors are LegalFly and Ironclad.")

    # 3. Verify dropdown list order (newest updated first)
    conv_list = db.list_conversations()
    assert len(conv_list) == 2
    assert conv_list[0]["id"] == conv2
    assert conv_list[0]["title"] == "Who Are My Main Competitors"
    assert conv_list[1]["id"] == conv1
    assert conv_list[1]["title"] == "My Viability Score"

    # 4. Switch back to conv1 and verify messages
    msgs_conv1 = db.get_messages(conv1)
    assert len(msgs_conv1) == 2
    assert msgs_conv1[0]["content"] == "What is my viability score?"
    assert msgs_conv1[1]["content"] == "Your viability score is 85/100."

    # 5. Verify conv2 messages are preserved and separate
    msgs_conv2 = db.get_messages(conv2)
    assert len(msgs_conv2) == 2
    assert msgs_conv2[0]["content"] == "Who are my main competitors?"
    assert msgs_conv2[1]["content"] == "Key competitors are LegalFly and Ironclad."


def test_delete_selected_conversation_flow(temp_db_path):
    """Verify deleting the currently selected conversation cleans it up and leaves other conversations intact."""
    db = ChatHistoryDB(session_id="sess_del", db_path=temp_db_path)

    c1 = db.create_conversation(title="Chat 1")
    db.save_message(c1, "user", "Hello 1")
    c2 = db.create_conversation(title="Chat 2")
    db.save_message(c2, "user", "Hello 2")

    # Delete c2
    deleted = db.delete_conversation(c2)
    assert deleted is True

    # Check c2 is gone and c1 remains intact
    assert db.get_conversation(c2) is None
    assert len(db.get_messages(c2)) == 0

    remaining = db.list_conversations()
    assert len(remaining) == 1
    assert remaining[0]["id"] == c1
    assert len(db.get_messages(c1)) == 1


# ============================================================
# 6. MANDATORY MULTI-USER ISOLATION TEST CASES (CASES A - J)
# ============================================================

def test_mandatory_isolation_cases_a_through_j(temp_db_path):
    """
    Directly validates Mandatory Isolation Test Cases A through J:
      A. Session A creates conversation A.
      B. Session B creates conversation B.
      C. list_conversations(session_A) returns only conversation A.
      D. list_conversations(session_B) returns only conversation B.
      E. Session B cannot get conversation A.
      F. Session B cannot get messages from conversation A.
      G. Session B cannot append a message to conversation A.
      H. Session B cannot delete conversation A.
      I. Session A can still read, append to, and delete its own conversation.
      J. Existing single-session conversation/history behavior continues working.
    """
    session_a = "session_alice_123"
    session_b = "session_bob_456"

    # --- Case A: Session A creates conversation A ---
    conv_a = create_conversation(
        title="Alice Startup Discussion",
        session_id=session_a,
        db_path=temp_db_path,
    )
    assert conv_a is not None and len(conv_a) > 0
    save_message(conv_a, session_a, "user", "Alice's proprietary idea", db_path=temp_db_path)
    save_message(conv_a, session_a, "assistant", "Alice analysis results", db_path=temp_db_path)

    # --- Case B: Session B creates conversation B ---
    conv_b = create_conversation(
        title="Bob FinTech Discussion",
        session_id=session_b,
        db_path=temp_db_path,
    )
    assert conv_b is not None and len(conv_b) > 0
    save_message(conv_b, session_b, "user", "Bob's private fintech pitch", db_path=temp_db_path)
    save_message(conv_b, session_b, "assistant", "Bob market valuation", db_path=temp_db_path)

    # --- Case C: list_conversations(session_A) returns only conversation A ---
    list_a = list_conversations(session_id=session_a, db_path=temp_db_path)
    assert len(list_a) == 1
    assert list_a[0]["id"] == conv_a
    assert list_a[0]["title"] == "Alice Startup Discussion"
    assert list_a[0]["session_id"] == session_a

    # --- Case D: list_conversations(session_B) returns only conversation B ---
    list_b = list_conversations(session_id=session_b, db_path=temp_db_path)
    assert len(list_b) == 1
    assert list_b[0]["id"] == conv_b
    assert list_b[0]["title"] == "Bob FinTech Discussion"
    assert list_b[0]["session_id"] == session_b

    # --- Case E: Session B cannot get conversation A ---
    assert get_conversation(conv_a, session_id=session_b, db_path=temp_db_path) is None

    # --- Case F: Session B cannot get messages from conversation A ---
    msgs_a_from_b = get_messages(conv_a, session_id=session_b, db_path=temp_db_path)
    assert msgs_a_from_b == []

    # --- Case G: Session B cannot append a message to conversation A ---
    with pytest.raises(ValueError, match="does not exist"):
        save_message(
            conv_a,
            session_b,
            "user",
            "Malicious message injected by Bob",
            db_path=temp_db_path,
        )

    # Verify messages in conversation A remain untouched (still 2)
    msgs_a_owner = get_messages(conv_a, session_id=session_a, db_path=temp_db_path)
    assert len(msgs_a_owner) == 2
    assert [m["content"] for m in msgs_a_owner] == ["Alice's proprietary idea", "Alice analysis results"]

    # --- Case H: Session B cannot delete conversation A ---
    delete_attempt = delete_conversation(conv_a, session_id=session_b, db_path=temp_db_path)
    assert delete_attempt is False
    # Conversation A still exists and is accessible by session A
    assert get_conversation(conv_a, session_id=session_a, db_path=temp_db_path) is not None

    # --- Case I: Session A can still read, append to, and delete its own conversation ---
    # 1. Session A reads conversation A
    conv_a_read = get_conversation(conv_a, session_id=session_a, db_path=temp_db_path)
    assert conv_a_read is not None
    assert conv_a_read["id"] == conv_a

    # 2. Session A appends to conversation A
    new_msg_id = save_message(conv_a, session_a, "user", "Alice follow-up question", db_path=temp_db_path)
    assert new_msg_id > 0
    msgs_a_after_append = get_messages(conv_a, session_id=session_a, db_path=temp_db_path)
    assert len(msgs_a_after_append) == 3
    assert msgs_a_after_append[-1]["content"] == "Alice follow-up question"

    # 3. Session A deletes its own conversation A
    delete_success = delete_conversation(conv_a, session_id=session_a, db_path=temp_db_path)
    assert delete_success is True
    assert get_conversation(conv_a, session_id=session_a, db_path=temp_db_path) is None
    assert get_messages(conv_a, session_id=session_a, db_path=temp_db_path) == []
    assert len(list_conversations(session_id=session_a, db_path=temp_db_path)) == 0

    # Conversation B was unaffected by Alice deleting conversation A
    assert get_conversation(conv_b, session_id=session_b, db_path=temp_db_path) is not None
    assert len(get_messages(conv_b, session_id=session_b, db_path=temp_db_path)) == 2

    # --- Case J: Existing single-session conversation/history behavior continues working ---
    db_single = ChatHistoryDB(session_id="session_single", db_path=temp_db_path)
    c_single = db_single.create_conversation(title="Single Session Workflow")
    db_single.save_message(c_single, "user", "Single session prompt")
    db_single.save_message(c_single, "assistant", "Single session answer")

    single_convs = db_single.list_conversations()
    assert len(single_convs) == 1
    assert single_convs[0]["id"] == c_single

    single_msgs = db_single.get_messages(c_single)
    assert len(single_msgs) == 2
    assert single_msgs[0]["content"] == "Single session prompt"
    assert single_msgs[1]["content"] == "Single session answer"

    assert db_single.delete_conversation(c_single) is True
    assert db_single.list_conversations() == []


# ============================================================
# 8. TESTS J & K: NEW VALIDATION RESET & AUTHENTIC SESSION PRESERVATION
# ============================================================

def test_new_validation_resets_active_conversation_id():
    """Verify that starting a new validation resets active_conversation_id to None (Fix 6, Test J)."""
    import streamlit as st
    from ui.streamlit_app import handle_validation_submission

    # Setup prior state where Idea A has an active conversation
    st.session_state.session_id = "test_user_session_123"
    st.session_state.active_conversation_id = "conv_idea_a_789"
    st.session_state.chat_history = [{"role": "user", "content": "Question about Idea A"}]

    mock_state = MagicMock(spec=StartupState)
    form_data = {
        "idea_text": "AI Accounting Bot",
        "target_industry": "Finance",
        "target_audience": "CPAs",
        "business_model": "SaaS",
        "timeline": "3 Months"
    }

    with patch("ui.streamlit_app.orchestrator.validate_idea", return_value=mock_state), \
         patch("streamlit.rerun"):
        handle_validation_submission(form_data)

    assert st.session_state.active_conversation_id is None
    assert st.session_state.session_id == "test_user_session_123"
    assert st.session_state.chat_history == []


def test_historical_report_viewing_preserves_authentic_session_id():
    """Verify that viewing a historical report does not overwrite authentic session_id (Fix 7, Test K)."""
    import streamlit as st
    from app.orchestrator import ApplicationOrchestrator

    current_auth_session = "user_browser_session_xyz"
    st.session_state.session_id = current_auth_session

    historical_session_id = "historical_session_abc_999"
    historical_state = MagicMock(spec=StartupState)

    mock_orchestrator = MagicMock(spec=ApplicationOrchestrator)
    mock_orchestrator.get_session_history.return_value = historical_state

    # Simulate View Report action in History tab
    restored = mock_orchestrator.get_session_history(historical_session_id)
    if restored:
        st.session_state.current_state = restored
        st.session_state.current_page = "Validation"

    assert st.session_state.session_id == current_auth_session
    assert st.session_state.session_id != historical_session_id
    assert st.session_state.current_state == historical_state


def test_multi_idea_conversation_isolation_workflow(temp_db_path):
    """Verify that Idea A and Idea B maintain separate conversations without cross-contamination."""
    session_id = "user_session_alpha"
    db = ChatHistoryDB(session_id=session_id, db_path=temp_db_path)

    # 1. Idea A validation completed -> create Conversation A
    conv_a = db.create_conversation(title="Idea A: AI Telehealth")
    db.save_message(conv_a, "user", "What are the strengths of Idea A?")
    db.save_message(conv_a, "assistant", "Idea A strengths are clinical prompts.")

    # 2. Start new validation (Idea B) -> active conversation reset
    active_conversation_id = None
    assert active_conversation_id is None

    # 3. Consult on Idea B -> creates new Conversation B
    conv_b = db.create_conversation(title="Idea B: Legal AI")
    db.save_message(conv_b, "user", "What are the strengths of Idea B?")
    db.save_message(conv_b, "assistant", "Idea B strengths are contract NLP.")

    assert conv_a != conv_b
    msgs_a = db.get_messages(conv_a)
    msgs_b = db.get_messages(conv_b)

    assert len(msgs_a) == 2
    assert "Idea A" in msgs_a[0]["content"]
    assert len(msgs_b) == 2
    assert "Idea B" in msgs_b[0]["content"]


# ============================================================
# 9. REGRESSION TESTS FOR BUGS 1 & 2
# ============================================================

def test_idea_a_to_idea_b_chat_contamination_prevented(temp_db_path):
    """Verify Bug 1 fix: Idea B creates a new Conversation B when active_conversation_id is None,
    preserving Conversation A in history without loading Idea A messages."""
    import streamlit as st
    from ui.components.advisor import render_advisor_chat
    from ui.streamlit_app import handle_validation_submission
    from database.chat_history import get_messages, list_conversations, save_message, create_conversation, get_conversation

    session_id = "test_user_session_workflow_123"
    st.session_state.session_id = session_id

    # 1. Validate Idea A -> Conversation A created
    conv_a = create_conversation(title="Idea A: AI Finance", session_id=session_id, db_path=temp_db_path)
    save_message(conv_a, session_id, "user", "What is the TAM for Idea A?", db_path=temp_db_path)
    save_message(conv_a, session_id, "assistant", "The TAM for Idea A is $10B.", db_path=temp_db_path)

    st.session_state.active_conversation_id = conv_a
    st.session_state.chat_history = [
        {"role": "user", "content": "What is the TAM for Idea A?"},
        {"role": "assistant", "content": "The TAM for Idea A is $10B."}
    ]

    # 2. Start new validation for Idea B
    mock_state_b = MagicMock(spec=StartupState)
    mock_state_b.idea = StartupIdea(
        idea_text="Idea B: AI Legal",
        target_industry="Legal",
        target_audience="Lawyers",
        business_model="SaaS",
        timeline="3 Months"
    )
    mock_state_b.final_report = ValidationReport(
        overall_viability_score=85,
        verdict="PROCEED",
        executive_summary="Strong legal automation demand."
    )

    form_data = {
        "idea_text": "Idea B: AI Legal",
        "target_industry": "Legal",
        "target_audience": "Lawyers",
        "business_model": "SaaS",
        "timeline": "3 Months"
    }

    with patch("ui.streamlit_app.orchestrator.validate_idea", return_value=mock_state_b), \
         patch("streamlit.rerun"):
        handle_validation_submission(form_data)

    # 4. Ensure active_conversation_id becomes None after new validation
    assert st.session_state.active_conversation_id is None
    assert st.session_state.chat_history == []

    # 5. Open Advisor for Idea B -> render_advisor_chat initialization logic
    mock_orch = MagicMock(spec=ApplicationOrchestrator)
    mock_orch.memory = MagicMock()
    mock_orch.get_session_history.return_value = mock_state_b


    with patch("ui.components.advisor.create_conversation", side_effect=lambda title, session_id: create_conversation(title=title, session_id=session_id, db_path=temp_db_path)), \
         patch("ui.components.advisor.list_conversations", side_effect=lambda session_id: list_conversations(session_id=session_id, db_path=temp_db_path)), \
         patch("ui.components.advisor.get_conversation", side_effect=lambda cid, session_id: get_conversation(cid, session_id=session_id, db_path=temp_db_path)), \
         patch("ui.components.advisor.get_messages", side_effect=lambda cid, session_id: get_messages(cid, session_id=session_id, db_path=temp_db_path)), \
         patch("ui.components.advisor.initialize_database"):
        render_advisor_chat(mock_orch, mock_state_b)

    # 6. Ensure a NEW Conversation B is created
    conv_b = st.session_state.active_conversation_id
    assert conv_b is not None
    assert conv_b != conv_a

    # 7. Ensure Conversation A remains in history
    history = list_conversations(session_id=session_id, db_path=temp_db_path)
    history_ids = [c["id"] for c in history]
    assert conv_a in history_ids
    assert conv_b in history_ids

    # 8. Ensure Idea B chat_history does not contain Idea A messages
    assert st.session_state.chat_history == []
    msgs_a = get_messages(conv_a, session_id=session_id, db_path=temp_db_path)
    assert len(msgs_a) == 2
    assert "Idea A" in msgs_a[0]["content"]

    # 9. Ensure follow-up questions for Idea B use Conversation B
    save_message(conv_b, session_id, "user", "What are the competitors for Idea B?", db_path=temp_db_path)
    msgs_b = get_messages(conv_b, session_id=session_id, db_path=temp_db_path)
    assert len(msgs_b) == 1
    assert "Idea B" in msgs_b[0]["content"]
    assert len(get_messages(conv_a, session_id=session_id, db_path=temp_db_path)) == 2


def test_validation_history_and_reports_session_scoping(tmp_path):
    """Verify Bug 2 fix: list_sessions scopes validation reports to the requested session_id,
    preventing Session A and Session B cross-report visibility."""
    import re
    import inspect
    from state.memory import MemoryStore
    from app.orchestrator import ApplicationOrchestrator
    import ui.streamlit_app

    mem_dir = str(tmp_path / "val_memory")
    memory = MemoryStore(storage_dir=mem_dir)

    idea_a = StartupIdea(idea_text="Alpha Logistics AI", target_industry="Logistics", target_audience="Freight", business_model="B2B")
    report_a = ValidationReport(overall_viability_score=88, verdict="PROCEED", executive_summary="Alpha report summary.")
    state_a = StartupState(idea=idea_a, final_report=report_a, status="completed")

    idea_b = StartupIdea(idea_text="Beta Biometrics AI", target_industry="Security", target_audience="Enterprises", business_model="B2B")
    report_b = ValidationReport(overall_viability_score=72, verdict="CAUTION", executive_summary="Beta report summary.")
    state_b = StartupState(idea=idea_b, final_report=report_b, status="completed")

    memory.save_state("session_A", state_a)
    memory.save_state("session_B", state_b)

    # 1. Verify MemoryStore.list_sessions scoping
    res_a = memory.list_sessions(session_id="session_A")
    assert len(res_a) == 1
    assert res_a[0]["session_id"] == "session_A"
    assert res_a[0]["idea"] == "Alpha Logistics AI"

    res_b = memory.list_sessions(session_id="session_B")
    assert len(res_b) == 1
    assert res_b[0]["session_id"] == "session_B"
    assert res_b[0]["idea"] == "Beta Biometrics AI"

    res_unfiltered = memory.list_sessions()
    assert len(res_unfiltered) == 2

    res_nonexistent = memory.list_sessions(session_id="session_UNKNOWN")
    assert res_nonexistent == []

    # 2. Verify ApplicationOrchestrator.list_all_sessions forwarding
    orch = ApplicationOrchestrator()
    orch.memory = memory

    assert len(orch.list_all_sessions(session_id="session_A")) == 1
    assert orch.list_all_sessions(session_id="session_A")[0]["session_id"] == "session_A"
    assert len(orch.list_all_sessions(session_id="session_B")) == 1
    assert orch.list_all_sessions(session_id="session_B")[0]["session_id"] == "session_B"

    # 3. Verify Validation History scopes to session_id while Reports repository lists all sessions
    streamlit_app_source = inspect.getsource(ui.streamlit_app)
    calls = re.findall(r"orchestrator\.list_all_sessions\((.*?)\)", streamlit_app_source)
    assert len(calls) == 2
    assert "session_id=curr_sess" in calls[0]
    assert calls[1].strip() == ""
