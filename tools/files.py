"""
Sandboxed file tools — see week_3/2_agent_class.md

Implement:
  - resolve_path
  - read_file(path, start_line=1, read_lines=200)  — numbered lines, has_more
  - write_file(path, content)
  - edit_file(path, operation, start_line, end_line?, content?)  — replace | delete | append
  - list_files(path, pattern)
"""

# TODO: implement — see Build 2
# --- File tools ---
import os
import glob
from pathlib import Path
import difflib


WORKSPACE_ROOT = Path(os.getcwd()).resolve()

def resolve_path(path_str: str) -> str:
    try:
        requested_path = Path(path_str)
        if requested_path.is_absolute():
            requested_path = requested_path.relative_to(requested_path.anchor)   
        full_path = (WORKSPACE_ROOT / requested_path).resolve()
        if not full_path.is_relative_to(WORKSPACE_ROOT):
            return (
                f"Security Block: Access denied. Path '{path_str}' attempts "
                f"to leave the workspace root."
            )
        return str(full_path)     
    except Exception as e:
        return (f"Path resolution failed for '{path_str}': {str(e)}")

def read_file(path: str, start_line: int = 1, read_lines: int = 200) -> dict:
  output = []
  try:
      
      with open(path, "r") as file:
          content = file.read()
          all_lines = content.splitlines()
          total_lines = len(all_lines) 
          window_lines = all_lines[start_line - 1 : start_line - 1 + read_lines]
          
          for line_num, line_content in enumerate(window_lines, start=start_line):
              output.append(f"{line_num} | {line_content}")
          
          
          return {
              "file": path,
              "total_lines": total_lines,
              "start_line": start_line,
              "lines_returned": len(window_lines),
              "content": "\n".join(output)
          }
          
  except Exception as e:
      return {"error": f"Error executing read_file: {str(e)}"}
    


def write_file(path: str, content: str) -> dict:
  try:
    with open(path,"w") as file:
      file.write(content)
    return{"Success":f"Content successfully written to file which is at {path}"}
  except Exception as e:
    return{"Error":str(e)}
    


def edit_file(
    path: str,
    operation: str,
    start_line: int,
    end_line: int | None = None,
    content: str | None = None,
) -> dict:
  try:  
    with open(path,"r+") as file:
      lines_before=file.read().splitlines()
      temp=lines_before.copy()
      if operation=='replace':
        new_lines=content.splitlines()

      elif operation=='delete':
        new_lines=[]

      elif operation=='append':
        new_lines=content.splitlines()
        end_line=start_line
        start_line=start_line+1
      lines_before[start_line-1:end_line]=new_lines
      file.seek(0)
      file_cont="\n".join(lines_before)
      file.write(file_cont)
      diff = difflib.unified_diff(
        temp, 
        lines_before, 
        fromfile="before_edit", 
        tofile="after_edit",
        lineterm="" # Prevents accidental extra double spacing breaks
      )
      diff_string = "\n".join(list(diff))
      file.truncate()
      return {"Changes":diff_string}
  except Exception as e:
    return{"Error": str(e)}


def list_files(path: str = ".", pattern: str = "*") -> dict:
  try:
      # 1. Safety check using the os module
      if not os.path.exists(path):
          return {"error": f"Directory '{path}' does not exist."}
          
      # 2. Convert the input string path into a Path object
      path_obj = Path(path)
      
      # 3. Use glob and loop over the results to convert path objects to clean text strings
      # We use .name to only get the filename, or str(p) if you want the relative folder path
      matching_files = [p.name for p in path_obj.glob(pattern) if p.is_file()]
      
      # 4. Return the list inside the promised dictionary structure
      return {
          "directory": path,
          "pattern": pattern,
          "files": matching_files
      }
      
  except Exception as e:
      return {"error": f"Failed to list files: {str(e)}"}
