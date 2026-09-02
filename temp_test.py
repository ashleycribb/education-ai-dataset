from typing import List, Dict, Any

def _get_statements_by_session(_all_statements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Indexes statements by session_id for efficient lookup."""
    statements_by_session: Dict[str, List[Dict[str, Any]]] = {}
    for i, stmt in enumerate(_all_statements):
        session_id_path = stmt.get("context", {}).get("extensions", {})
        session_id = session_id_path.get("http://example.com/xapi/extensions/session_id", f"unknown_session_stmt{i}") if isinstance(session_id_path, dict) else f"unknown_session_stmt{i}"

        if session_id not in statements_by_session:
            statements_by_session[session_id] = []
        statements_by_session[session_id].append(stmt)
    return statements_by_session

def test_data_manager():
    """Test if data manager works"""
    print("🔄 Testing data manager...")
    try:
        mock_statements = [
            {"context": {"extensions": {"http://example.com/xapi/extensions/session_id": "session1"}}},
            {"context": {"extensions": {"http://example.com/xapi/extensions/session_id": "session2"}}},
            {"context": {"extensions": {"http://example.com/xapi/extensions/session_id": "session1"}}}
        ]
        indexed_statements = _get_statements_by_session(mock_statements)
        assert len(indexed_statements["session1"]) == 2
        assert len(indexed_statements["session2"]) == 1
        print("✅ _get_statements_by_session works as expected")

        return True
    except Exception as e:
        print(f"❌ Data manager failed: {e}")
        return False

if __name__ == "__main__":
    test_data_manager()
