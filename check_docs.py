import inspect
import sys
import os
import pkgutil

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

def check_module(module_name):
    try:
        module = __import__(module_name, fromlist=[''])
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            # Check if function is defined in this module
            if obj.__module__ != module_name:
                continue
            try:
                sig = inspect.signature(obj)
            except ValueError:
                continue
                
            if 'work_root' in sig.parameters:
                doc = inspect.getdoc(obj)
                if not doc:
                    print(f"FAIL: {module_name}.{name} has no docstring")
                    continue
                
                lower_doc = doc.lower()
                idx_work_root = lower_doc.find('work_root')
                idx_args = lower_doc.find('args:')
                idx_params = lower_doc.find('parameters:')
                
                header_pos = max(idx_args, idx_params)
                
                if idx_work_root == -1:
                     print(f"FAIL: {module_name}.{name} docstring does not mention 'work_root'")
                elif header_pos == -1:
                     print(f"FAIL: {module_name}.{name} docstring has 'work_root' but no 'Args:' or 'Parameters:' section")
                elif header_pos > idx_work_root:
                     print(f"FAIL: {module_name}.{name} 'work_root' appears before 'Args:' or 'Parameters:'")
                else:
                     print(f"PASS: {module_name}.{name}")
    except Exception as e:
        print(f"ERROR: Could not import {module_name}: {e}")

# Walk through src/abacusagent/modules
for root, dirs, files in os.walk('src/abacusagent/modules'):
    for file in files:
        if file.endswith('.py') and file != '__init__.py':
            rel_path = os.path.relpath(os.path.join(root, file), 'src')
            module_name = rel_path.replace(os.sep, '.')[:-3]
            check_module(module_name)
