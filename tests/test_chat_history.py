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
# 2. CONVERSATION CREATION & RETRIEVAL TESTS
# ============================================================

def test_create_and_get_conversation(temp_db_path):
    """Verify creating a conversation generates unique ID, timestamps, and default title."""
    conv_id = create_conversation(title="Healthcare Discussion", session_id="sess_123", db_path=temp_db_path)
    assert isinstance(conv_id, str)
    assert len(conv_id) > 0

    conv = get_conversation(conv_id, db_path=temp_db_path)
    assert conv is not None
    assert conv["id"] == conv_id
    assert conv["title"] == "Healthcare Discussion"
    assert conv["session_id"] == "sess_123"
    assert "created_at" in conv
    assert "updated_at" in conv


def test_default_conversation_title(temp_db_path):
    """Verify default conversation title is 'New Conversation'."""
    conv_id = create_conversation(db_path=temp_db_path)
    conv = get_conversation(conv_id, db_path=temp_db_path)
    assert conv["title"] == "New Conversation"


def test_list_conversations_ordering_and_filtering(temp_db_path):
    """Verify list_conversations orders by updated_at descending and supports session filtering."""
    c1 = create_conversation(title="Chat 1", session_id="sess_A", db_path=temp_db_path)
    c2 = create_conversation(title="Chat 2", session_id="sess_B", db_path=temp_db_path)
    c3 = create_conversation(title="Chat 3", session_id="sess_A", db_path=temp_db_path)

    # All conversations
    all_convs = list_conversations(db_path=temp_db_path)
    assert len(all_convs) == 3
    assert [c["id"] for c in all_convs] == [c3, c2, c1]

    # Filtered by session_id
    sess_a_convs = list_conversations(session_id="sess_A", db_path=temp_db_path)
    assert len(sess_a_convs) == 2
    assert [c["id"] for c in sess_a_convs] == [c3, c1]


def test_update_conversation_title_and_timestamp(temp_db_path):
    """Verify updating title and timestamp works properly."""
    conv_id = create_conversation(title="Old Title", db_path=temp_db_path)
    initial_conv = get_conversation(conv_id, db_path=temp_db_path)

    updated = update_conversation_title(conv_id, "Updated Title", db_path=temp_db_path)
    assert updated is True

    conv = get_conversation(conv_id, db_path=temp_db_path)
    assert conv["title"] == "Updated Title"

    # Timestamp update
    ts_updated = update_conversation_timestamp(conv_id, db_path=temp_db_path)
    assert ts_updated is True


def test_delete_conversation_and_cascade(temp_db_path):
    """Verify deleting a conversation cascades and deletes its messages."""
    conv_id = create_conversation(title="To Delete", db_path=temp_db_path)
    save_message(conv_id, "user", "Hello", db_path=temp_db_path)
    save_message(conv_id, "assistant", "Hi there!", db_path=temp_db_path)

    assert len(get_messages(conv_id, db_path=temp_db_path)) == 2

    deleted = delete_conversation(conv_id, db_path=temp_db_path)
    assert deleted is True

    assert get_conversation(conv_id, db_path=temp_db_path) is None
    assert len(get_messages(conv_id, db_path=temp_db_path)) == 0


# ============================================================
# 3. MESSAGE STORAGE & VALIDATION TESTS
# ============================================================

def test_save_and_retrieve_messages(temp_db_path):
    """Verify saving user and assistant messages and retrieving them in chronological order."""
    conv_id = create_conversation(title="Q&A", db_path=temp_db_path)

    m1_id = save_message(conv_id, "user", "What is the market size?", db_path=temp_db_path)
    m2_id = save_message(conv_id, "assistant", "TAM is $25B.", db_path=temp_db_path)
    m3_id = save_message(conv_id, "user", "Who are the competitors?", db_path=temp_db_path)
    m4_id = save_message(conv_id, "assistant", "Key competitors are LegalFly and Ironclad.", db_path=temp_db_path)

    msgs = get_messages(conv_id, db_path=temp_db_path)
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
    conv_id = create_conversation(db_path=temp_db_path)

    with pytest.raises(ValueError, match="Invalid message role"):
        save_message(conv_id, "system", "System prompt", db_path=temp_db_path)

    with pytest.raises(ValueError, match="Invalid message role"):
        save_message(conv_id, "admin", "Admin message", db_path=temp_db_path)


def test_save_message_empty_content(temp_db_path):
    """Verify save_message rejects empty or whitespace-only content."""
    conv_id = create_conversation(db_path=temp_db_path)

    with pytest.raises(ValueError, match="Message content cannot be empty"):
        save_message(conv_id, "user", "", db_path=temp_db_path)

    with pytest.raises(ValueError, match="Message content cannot be empty"):
        save_message(conv_id, "assistant", "   ", db_path=temp_db_path)


def test_save_message_nonexistent_conversation(temp_db_path):
    """Verify save_message raises ValueError when conversation does not exist."""
    with pytest.raises(ValueError, match="does not exist"):
        save_message("nonexistent-conv-id", "user", "Hello", db_path=temp_db_path)


def test_messages_chronological_order_with_limit(temp_db_path):
    """Verify get_messages with limit returns the most recent N messages in chronological order."""
    conv_id = create_conversation(db_path=temp_db_path)

    for i in range(1, 11):
        role = "user" if i % 2 == 1 else "assistant"
        save_message(conv_id, role, f"Message {i}", db_path=temp_db_path)

    # Total 10 messages, request limit 4
    limited_msgs = get_messages(conv_id, limit=4, db_path=temp_db_path)
    assert len(limited_msgs) == 4
    # Must be messages 7, 8, 9, 10 in chronological order
    assert [m["content"] for m in limited_msgs] == [
        "Message 7",
        "Message 8",
        "Message 9",
        "Message 10",
    ]


def test_multiple_conversations_isolation(temp_db_path):
    """Verify messages from Conversation A never leak into Conversation B."""
    conv_a = create_conversation(title="Chat A", db_path=temp_db_path)
    conv_b = create_conversation(title="Chat B", db_path=temp_db_path)

    save_message(conv_a, "user", "Question for A", db_path=temp_db_path)
    save_message(conv_a, "assistant", "Answer for A", db_path=temp_db_path)

    save_message(conv_b, "user", "Question for B", db_path=temp_db_path)

    msgs_a = get_messages(conv_a, db_path=temp_db_path)
    msgs_b = get_messages(conv_b, db_path=temp_db_path)

    assert len(msgs_a) == 2
    assert len(msgs_b) == 1
    assert msgs_a[0]["content"] == "Question for A"
    assert msgs_b[0]["content"] == "Question for B"


# ============================================================
# 4. EDGE CASES & UTILITY TESTS
# ============================================================

def test_empty_conversation_safe(temp_db_path):
    """Verify querying an empty conversation returns empty list without error."""
    conv_id = create_conversation(db_path=temp_db_path)
    msgs = get_messages(conv_id, db_path=temp_db_path)
    assert msgs == []


def test_invalid_conversation_id_safe(temp_db_path):
    """Verify querying an invalid conversation ID behaves safely."""
    assert get_conversation("invalid-id", db_path=temp_db_path) is None
    assert get_conversation("", db_path=temp_db_path) is None
    assert get_messages("invalid-id", db_path=temp_db_path) == []
    assert get_messages("", db_path=temp_db_path) == []
    assert delete_conversation("invalid-id", db_path=temp_db_path) is False


def test_generate_title_from_message():
    """Verify deterministic title generation extracts clean, concise titles."""
    assert generate_title_from_message("") == "New Conversation"
    assert generate_title_from_message("   ") == "New Conversation"

    t1 = generate_title_from_message("What is the biggest risk in my healthcare startup?")
    assert "Risk In My Healthcare Startup" in t1 or "Biggest Risk" in t1
    assert len(t1) <= 40

    t2 = generate_title_from_message("How can I reduce customer acquisition cost?")
    assert "Reduce Customer Acquisition Cost" in t2 or "Customer Acquisition Cost" in t2
    assert len(t2) <= 40

    t3 = generate_title_from_message("Tell me about our direct competitors in legal tech")
    assert "Direct Competitors In Legal Tech" in t3 or "Competitors" in t3

    t4 = generate_title_from_message("What is my viability score?")
    assert "Viability Score" in t4


def test_chat_history_db_class_wrapper(temp_db_path):
    """Verify ChatHistoryDB object-oriented wrapper class works identically."""
    db = ChatHistoryDB(db_path=temp_db_path)
    conv_id = db.create_conversation(title="OOP Chat", session_id="s1")

    db.save_message(conv_id, "user", "Hello OOP")
    db.save_message(conv_id, "assistant", "Hi OOP")

    msgs = db.get_messages(conv_id)
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Hello OOP"

    conv = db.get_conversation(conv_id)
    assert conv["title"] == "OOP Chat"

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
    db1 = ChatHistoryDB(db_path=db_file)
    c_id = db1.create_conversation(title="Persistent Chat")
    db1.save_message(c_id, "user", "Message before restart")
    db1.save_message(c_id, "assistant", "Answer before restart")

    # Session 2: Fresh instance pointing to same file
    db2 = ChatHistoryDB(db_path=db_file)
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
    db = ChatHistoryDB(db_path=temp_db_path)

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
