EVALUATION_CASES = [
    {
        "repository": "sampleproject_ast",
        "question": "Where is the add_one function defined?",
        "expected_file": "src/sample/simple.py",
    },
    {
        "repository": "sampleproject_ast",
        "question": "Where are the tests for add_one?",
        "expected_file": "tests/test_simple.py",
    },
    {
        "repository": "sampleproject_ast",
        "question": "Where is project automation configured?",
        "expected_file": "noxfile.py",
    },
]