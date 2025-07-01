# import re
# import subprocess
# import os

# # Get the absolute path to the JAR file inside the package
# JAR_PATH = os.path.join(os.path.dirname(__file__), "resources", "google-java-format-1.25.2-all-deps.jar")


# def remove_comments(code):
#     code = re.sub(r'//.*', '', code)  # Remove single-line comments
#     code = re.sub(r'/\*[\s\S]*?\*/', '', code)  # Remove multi-line comments
#     return code.strip()

# def format_code(code):
#     try:
#         with open("temp.java", "w") as f:
#             f.write(code)

#         process = subprocess.run(
#             ["java", "-jar", JAR_PATH, "-i", "temp.java"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )

#         if process.returncode == 0:
#             with open("temp.java", "r") as f:
#                 # delete the temp file
#                 lines = f.read()
                
#                 return lines
#         else:
#             print("Error formatting code:", process.stderr.decode())
#             return code
#     except Exception as e:
#         print("Exception occurred while formatting code:", str(e))
#         return code
#     finally:
#         if os.path.exists("temp.java"):
#             os.remove("temp.java")

# def extract_chunks(java_code, window_size=5):
#     stride = window_size // 2
#     lines = java_code.split("\n")
#     return ["\n".join(lines[i:i + window_size]) for i in range(0, len(lines) - window_size + 1, stride)]

# def handle_overlapping_chunks(chunks, threshold=0.5):
#     # This function handles overlapping chunks by merging or filtering based on threshold
#     filtered_chunks = []
#     i = 0
#     while i < len(chunks):
#         if i + 1 < len(chunks):
#             overlap = calculate_overlap(chunks[i], chunks[i + 1])
#             if overlap > threshold:
#                 # Merge chunks if overlap is too high
#                 merged_chunk = chunks[i] + "\n" + chunks[i + 1]
#                 filtered_chunks.append(merged_chunk)
#                 i += 2  # Skip the next chunk as it's merged
#             else:
#                 filtered_chunks.append(chunks[i])
#                 i += 1
#         else:
#             filtered_chunks.append(chunks[i])
#             i += 1
#     return filtered_chunks

# def calculate_overlap(chunk1, chunk2):
#     # Calculate the overlap ratio between two chunks
#     chunk1_lines = chunk1.split("\n")
#     chunk2_lines = chunk2.split("\n")

#     common_lines = len(set(chunk1_lines) & set(chunk2_lines))
#     overlap = common_lines / min(len(chunk1_lines), len(chunk2_lines))

#     return overlap

# def preprocess_code(java_code):
#     code = remove_comments(java_code)
#     code = format_code(code)
#     return extract_chunks(code)


# import javalang

# def extract_methods_from_java(java_code):
#     """Extract complete methods as chunks using Java AST parsing"""
#     try:
#         tree = javalang.parse.parse(java_code)
#         methods = []
        
#         for _, node in tree.filter(javalang.tree.MethodDeclaration):
#             # Convert method back to string representation
#             method_lines = java_code.split('\n')
#             method_start = node.position.line - 1
            
#             # Find method end by counting braces
#             brace_count = 0
#             method_end = method_start
#             for i in range(method_start, len(method_lines)):
#                 line = method_lines[i]
#                 brace_count += line.count('{') - line.count('}')
#                 if brace_count == 0 and '{' in method_lines[method_start:i+1]:
#                     method_end = i
#                     break
            
#             method_code = '\n'.join(method_lines[method_start:method_end+1])
#             methods.append(method_code.strip())
        
#         return methods
#     except:
#         # Fallback to simpler method extraction
#         return extract_methods_simple(java_code)


import re

def preprocess_code(java_code):
    """Extract complete methods as chunks"""
    # Remove comments and normalize whitespace
    code = remove_comments(java_code)
    
    # Extract complete methods
    methods = extract_complete_methods(code)
    
    return methods

def extract_complete_methods(java_code):
    """Extract complete method definitions"""
    methods = []
    lines = java_code.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line starts a method (simple heuristic)
        if (line and 
            ('public' in line or 'private' in line or 'protected' in line) and
            '(' in line and ')' in line and 
            '{' in line):
            
            # Found method start, now find the complete method
            method_lines = []
            brace_count = 0
            method_started = False
            
            j = i
            while j < len(lines):
                current_line = lines[j]
                method_lines.append(current_line)
                
                # Count braces to find method end
                open_braces = current_line.count('{')
                close_braces = current_line.count('}')
                
                if open_braces > 0:
                    method_started = True
                
                brace_count += open_braces - close_braces
                
                # Method complete when braces balance
                if method_started and brace_count == 0:
                    method_code = '\n'.join(method_lines).strip()
                    if method_code:
                        methods.append(method_code)
                    i = j + 1
                    break
                
                j += 1
            else:
                # If we reach here, method wasn't properly closed
                i += 1
        else:
            i += 1
    
    return methods

def remove_comments(java_code):
    """Remove single-line and multi-line comments"""
    # Remove single-line comments
    java_code = re.sub(r'//.*', '', java_code)
    
    # Remove multi-line comments
    java_code = re.sub(r'/\*.*?\*/', '', java_code, flags=re.DOTALL)
    
    return java_code

def handle_overlapping_chunks(chunks):
    """Remove duplicate chunks and very short chunks"""
    filtered_chunks = []
    seen_chunks = set()
    
    for chunk in chunks:
        # Normalize chunk for comparison
        normalized = ' '.join(chunk.split())
        
        # Skip very short chunks or duplicates
        if len(normalized) > 50 and normalized not in seen_chunks:
            filtered_chunks.append(chunk)
            seen_chunks.add(normalized)
    
    return filtered_chunks