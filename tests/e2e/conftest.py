def pytest_addoption(parser):
    parser.addoption(
        "--only-discard-tests",
        action="store_true",
        default=False,
        help="Run only the discard staged file tests (for rapid debugging)"
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("--only-discard-tests"):
        keep = []
        for item in items:
            if (
                "test_discard_staged_by_filename" in item.nodeid
                or "test_multiple_staged_files_same_id" in item.nodeid
                or "test_malformed_staged_file_handling" in item.nodeid
            ):
                keep.append(item)
        items[:] = keep 