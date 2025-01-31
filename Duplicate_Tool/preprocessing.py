import re
import subprocess
import os

# Get the absolute path to the JAR file inside the package
JAR_PATH = os.path.join(os.path.dirname(__file__), "resources", "google-java-format-1.25.2-all-deps.jar")


def remove_comments(code):
    code = re.sub(r'//.*', '', code)  # Remove single-line comments
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)  # Remove multi-line comments
    return code.strip()

def format_code(code):
    with open("temp.java", "w") as f:
        f.write(code)

    process = subprocess.run(
        ["java", "-jar", JAR_PATH, "-i", "temp.java"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode == 0:
        with open("temp.java", "r") as f:
            # delete the temp file
            lines = f.read()
            
            return lines
    else:
        print("Error formatting code:", process.stderr.decode())
        return code  

def extract_chunks(java_code, window_size=5):
    stride = window_size // 2
    lines = java_code.split("\n")
    return ["\n".join(lines[i:i + window_size]) for i in range(0, len(lines) - window_size + 1, stride)]

def handle_overlapping_chunks(chunks, threshold=0.5):
    # This function handles overlapping chunks by merging or filtering based on threshold
    filtered_chunks = []
    i = 0
    while i < len(chunks):
        if i + 1 < len(chunks):
            overlap = calculate_overlap(chunks[i], chunks[i + 1])
            if overlap > threshold:
                # Merge chunks if overlap is too high
                merged_chunk = chunks[i] + "\n" + chunks[i + 1]
                filtered_chunks.append(merged_chunk)
                i += 2  # Skip the next chunk as it's merged
            else:
                filtered_chunks.append(chunks[i])
                i += 1
        else:
            filtered_chunks.append(chunks[i])
            i += 1
    return filtered_chunks

def calculate_overlap(chunk1, chunk2):
    # Calculate the overlap ratio between two chunks
    chunk1_lines = chunk1.split("\n")
    chunk2_lines = chunk2.split("\n")

    common_lines = len(set(chunk1_lines) & set(chunk2_lines))
    overlap = common_lines / min(len(chunk1_lines), len(chunk2_lines))

    return overlap

def preprocess_code(java_code):
    code = remove_comments(java_code)
    code = format_code(code)
    return extract_chunks(code)