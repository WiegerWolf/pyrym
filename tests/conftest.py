"""
Configuration for the pytest test suite.
"""
import sys
from os.path import abspath, dirname

# Add the project root directory to the Python path
# This allows tests to import modules from the 'src' directory
root_dir = dirname(dirname(abspath(__file__)))
sys.path.insert(0, root_dir)