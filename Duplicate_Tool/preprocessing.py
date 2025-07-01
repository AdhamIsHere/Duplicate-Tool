import re
import subprocess
import os

def preprocess_code(java_code, use_formatting=True):
    """Extract complete methods as chunks"""
    # Format code first for better consistency
    if use_formatting:
        code = format_java_code(java_code)
    else:
        code = normalize_code(java_code)
    
    # Remove comments and normalize whitespace
    code = remove_comments(code)
    
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

def format_java_code(java_code):
    """Format Java code using Google Java Format"""
    try:
        # Path to the Google Java Format jar file
        jar_path = os.path.join(os.path.dirname(__file__), 'resources', 'google-java-format-1.25.2-all-deps.jar')
        
        if not os.path.exists(jar_path):
            print(f"Warning: Google Java Format jar not found at {jar_path}")
            return java_code
        
        # Create a temporary file with the Java code
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as temp_file:
            temp_file.write(java_code)
            temp_file_path = temp_file.name
        
        try:
            # Run Google Java Format
            result = subprocess.run([
                'java', '-jar', jar_path,
                '--replace',  # Replace the file in place
                temp_file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Read the formatted code
                with open(temp_file_path, 'r') as f:
                    formatted_code = f.read()
                return formatted_code
            else:
                print(f"Google Java Format error: {result.stderr}")
                return java_code
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"Error formatting code: {e}")
        return java_code

def normalize_code(java_code):
    """Normalize code formatting for better duplicate detection"""
    # Basic normalization if Google Java Format is not available
    lines = java_code.split('\n')
    normalized_lines = []
    
    for line in lines:
        # Remove extra whitespace but preserve structure
        stripped = line.strip()
        if stripped:
            normalized_lines.append(stripped)
    
    return '\n'.join(normalized_lines)