# 000 - Shared Patterns Reference

This document contains templates and boilerplate code that specs can reference to avoid repetition.

## Spec Template

Standard template for new specification documents:

```markdown
# XXX - Feature Name

**Purpose:** One-line description of what this does and why

**Requirements:**
- Key functional requirement 1
- Key functional requirement 2
- Important constraints or non-functional requirements

**Design Approach:**
- High-level design decision 1
- High-level design decision 2
- Key technical choices and rationale

**Implementation Notes:**
- Critical implementation details only
- Dependencies or special considerations
- Integration points with existing code

**Status:** [Draft/Approved/Implemented]
```

## Test Function Template

Standard test structure:

```python
def test_feature_basic():
    """Test basic functionality works correctly."""
    # Test happy path
    # Verify expected outputs


def test_feature_edge_cases():
    """Test edge cases and error handling."""
    # Test boundary conditions
    # Test error scenarios
```
