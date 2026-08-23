import sys
import traceback

try:
    import runpy
    runpy.run_path('painel.py', run_name='__main__')
except Exception as e:
    with open('error_log.txt', 'w') as f:
        traceback.print_exc(file=f)
