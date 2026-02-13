WRAPPER_TEMPLATE = '''
import json

# === User code ===
{user_code}
# === End user code ===

# === Test runner ===
results = []
tests = {tests_json}

for i, test in enumerate(tests):
    try:
        actual = eval(test["input"])
        expected = eval(test["expected"])
        passed = actual == expected
        results.append({{
            "test_index": i,
            "passed": passed,
            "input": test["input"],
            "expected": str(expected),
            "actual": str(actual),
            "error": None,
        }})
    except Exception as e:
        results.append({{
            "test_index": i,
            "passed": False,
            "input": test["input"],
            "expected": test["expected"],
            "actual": "",
            "error": str(e),
        }})

print("__RESULTS__" + json.dumps(results))
'''
