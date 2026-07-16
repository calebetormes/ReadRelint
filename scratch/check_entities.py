import sys
import subprocess
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, root_dir)

print("VENV Python Executable:", sys.executable)
try:
    from src.domain.entities import IncidentReport
    print("VENV IncidentReport required fields:")
    print({k: v.is_required() for k, v in IncidentReport.model_fields.items() if v.is_required()})
except Exception as e:
    print("Error in VENV:", e)

# Test with global python
global_python = r"C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe"
print("\nGlobal Python Executable:", global_python)
script_code = f"""
import sys
sys.path.insert(0, r'{root_dir}')
try:
    from src.domain.entities import IncidentReport
    print("Global IncidentReport required fields:")
    print({{k: v.is_required() for k, v in IncidentReport.model_fields.items() if v.is_required()}})
except Exception as e:
    print("Error in Global:", e)
"""
try:
    res = subprocess.run([global_python, "-c", script_code], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Global Error Output:", res.stderr)
except Exception as e:
    print("Error spawning global python:", e)
