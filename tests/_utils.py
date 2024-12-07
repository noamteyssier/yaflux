def _assert_out_of_order(analysis, step):
    """Tests for out of order execution of analysis steps."""
    try:
        step()
        assert False
    except ValueError:
        assert True
    assert step.__name__ not in analysis.completed_steps


def _assert_in_order(analysis, step):
    """Tests for in order execution of analysis steps."""
    step()
    assert step.__name__ in analysis.completed_steps
