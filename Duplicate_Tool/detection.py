import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from embedding import get_embedding
from preprocessing import preprocess_code, handle_overlapping_chunks

# def detect_duplicate_groups(java_code, threshold=0.95):
#     chunks = preprocess_code(java_code)  # This includes formatting and chunk extraction
#     filtered_chunks = handle_overlapping_chunks(chunks)
#     embeddings = [get_embedding(chunk) for chunk in filtered_chunks]

#     # Compute similarity matrix between all pairs of filtered_chunks
#     similarity_matrix = np.zeros((len(filtered_chunks), len(filtered_chunks)))
#     for i in range(len(embeddings)):
#         for j in range(i + 1, len(embeddings)):
#             similarity = cosine_similarity(embeddings[i].numpy(), embeddings[j].numpy())[0][0]
#             similarity_matrix[i, j] = similarity
#             similarity_matrix[j, i] = similarity  # Symmetric matrix

#     # Find groups of similar filtered_chunks using a simple threshold for similarity
#     visited = set()
#     duplicate_groups = []

#     for i in range(len(filtered_chunks)):
#         if i not in visited:
#             group = [i]  # Start a new group
#             visited.add(i)
#             # Explore the group by checking similarities
#             for j in range(i + 1, len(filtered_chunks)):
#                 if similarity_matrix[i, j] > threshold and j not in visited:
#                     group.append(j)
#                     visited.add(j)
#             if len(group) > 1:  # If a group has more than one chunk, it's a duplicate group
#                 avg_similarity = np.mean([similarity_matrix[group[0], index] for index in group[1:]])  # Average similarity of the group
#                 duplicate_groups.append(([filtered_chunks[index] for index in group], avg_similarity))

#     return duplicate_groups

def detect_duplicate_groups(java_code, threshold=0.90):
    chunks = preprocess_code(java_code)
    filtered_chunks = handle_overlapping_chunks(chunks)
    embeddings = [get_embedding(chunk) for chunk in filtered_chunks]

    # Compute similarity matrix
    similarity_matrix = np.zeros((len(filtered_chunks), len(filtered_chunks)))
    for i in range(len(embeddings)):
        for j in range(len(embeddings)):
            if i != j:
                similarity = cosine_similarity(embeddings[i].reshape(1, -1), embeddings[j].reshape(1, -1))[0][0]
                similarity_matrix[i, j] = similarity

    # Improved grouping using connected components with stricter criteria
    visited = set()
    duplicate_groups = []

    for i in range(len(filtered_chunks)):
        if i not in visited:
            group = []
            stack = [i]
            
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    group.append(current)
                    
                    # Find all similar chunks with stricter threshold
                    for j in range(len(filtered_chunks)):
                        if j not in visited and similarity_matrix[current, j] > threshold:
                            # Additional check: ensure all members are similar to each other
                            should_add = True
                            for existing_member in group:
                                if similarity_matrix[existing_member, j] <= threshold * 0.9:  # Stricter criteria
                                    should_add = False
                                    break
                            if should_add:
                                stack.append(j)
            
            if len(group) > 1:
                similarities = []
                for g1 in group:
                    for g2 in group:
                        if g1 != g2:
                            similarities.append(similarity_matrix[g1, g2])
                avg_similarity = np.mean(similarities)
                duplicate_groups.append(([filtered_chunks[index] for index in group], avg_similarity))

    return duplicate_groups

def extract_code_blocks(java_code, min_lines=2):
    """Extract code blocks (both methods and statement groups) for duplicate detection"""
    lines = java_code.split('\n')
    blocks = []
    
    # First, extract complete methods
    methods = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line starts a method
        if (line and 
            ('public' in line or 'private' in line or 'protected' in line) and
            '(' in line and ')' in line):
            
            method_lines = []
            brace_count = 0
            method_started = False
            
            j = i
            while j < len(lines):
                current_line = lines[j]
                method_lines.append(current_line)
                
                open_braces = current_line.count('{')
                close_braces = current_line.count('}')
                
                if open_braces > 0:
                    method_started = True
                
                brace_count += open_braces - close_braces
                
                if method_started and brace_count == 0:
                    method_code = '\n'.join(method_lines).strip()
                    if method_code:
                        methods.append((method_code, i, j))
                    i = j + 1
                    break
                
                j += 1
            else:
                i += 1
        else:
            i += 1
    
    # Add complete methods to blocks
    for method_code, start, end in methods:
        blocks.append(method_code)
    
    # Extract statement blocks from within methods using a simpler approach
    for method_code, method_start, method_end in methods:
        method_lines = method_code.split('\n')
        
        # Find all consecutive statement groups separated by comments or empty lines
        current_block = []
        
        for line_idx, line in enumerate(method_lines):
            stripped = line.strip()
            
            # Skip method signature line
            if ('public' in stripped or 'private' in stripped or 'protected' in stripped) and '(' in stripped:
                continue
                
            # Skip empty lines, comments, and lone braces
            if not stripped or stripped.startswith('//') or stripped in ['{', '}']:
                # Save current block if it's substantial
                if len(current_block) >= min_lines:
                    block_code = '\n'.join(current_block).strip()
                    if block_code and block_code not in blocks:
                        blocks.append(block_code)
                current_block = []
                continue
            
            # Add non-empty code lines to current block
            if stripped:
                current_block.append(line.strip())
        
        # Add final block
        if len(current_block) >= min_lines:
            block_code = '\n'.join(current_block).strip()
            if block_code and block_code not in blocks:
                blocks.append(block_code)
    
    return blocks

def detect_duplicate_groups_enhanced(java_code, threshold=0.90, detect_intra_method=True, prefer_methods=True):
    """Enhanced duplicate detection that can find both inter-method and intra-method duplicates"""
    if detect_intra_method:
        chunks = extract_code_blocks(java_code)
    else:
        chunks = preprocess_code(java_code)
    
    filtered_chunks = handle_overlapping_chunks(chunks)
    
    if len(filtered_chunks) < 2:
        return []
    
    # Separate methods from code blocks if prefer_methods is True
    if prefer_methods and detect_intra_method:
        methods = [chunk for chunk in filtered_chunks if ("public" in chunk or "private" in chunk) and "(" in chunk]
        code_blocks = [chunk for chunk in filtered_chunks if not (("public" in chunk or "private" in chunk) and "(" in chunk)]
        
        # First try to find duplicates among complete methods
        method_groups = []
        if len(methods) >= 2:
            method_groups = find_duplicate_groups(methods, threshold)
        
        # Only look for code block duplicates if we found few or no method duplicates
        block_groups = []
        if len(method_groups) <= 1 and len(code_blocks) >= 2:  # Only if we have very few method groups
            block_threshold = threshold + 0.05  # Higher threshold for code blocks
            block_groups = find_duplicate_groups(code_blocks, block_threshold)
        
        return method_groups + block_groups
    else:
        return find_duplicate_groups(filtered_chunks, threshold)

def find_duplicate_groups(chunks, threshold):
    """Helper function to find duplicate groups from a list of chunks"""
    embeddings = [get_embedding(chunk) for chunk in chunks]

    # Compute similarity matrix
    similarity_matrix = np.zeros((len(chunks), len(chunks)))
    for i in range(len(embeddings)):
        for j in range(len(embeddings)):
            if i != j:
                similarity = cosine_similarity(embeddings[i].reshape(1, -1), embeddings[j].reshape(1, -1))[0][0]
                similarity_matrix[i, j] = similarity

    # Improved grouping using connected components with stricter criteria
    visited = set()
    duplicate_groups = []

    for i in range(len(chunks)):
        if i not in visited:
            group = []
            stack = [i]
            
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    group.append(current)
                    
                    # Find all similar chunks with stricter threshold
                    for j in range(len(chunks)):
                        if j not in visited and similarity_matrix[current, j] > threshold:
                            # Additional check: ensure all members are similar to each other
                            should_add = True
                            for existing_member in group:
                                if similarity_matrix[existing_member, j] <= threshold * 0.95:  # Even stricter criteria
                                    should_add = False
                                    break
                            if should_add:
                                stack.append(j)
            
            if len(group) > 1:
                similarities = []
                for g1 in group:
                    for g2 in group:
                        if g1 != g2:
                            similarities.append(similarity_matrix[g1, g2])
                avg_similarity = np.mean(similarities)
                duplicate_groups.append(([chunks[index] for index in group], avg_similarity))

    return duplicate_groups

# def print_groups(duplicate_groups):
#     i=1
#     for group, similarity in duplicate_groups:
#         print("="*50)
#         print(f"Duplicate Group: {i}")
#         i+=1
#         print(f"Avg Similarity: {similarity}")
#         for chunk in group:
#             print("start chunk")
#             print(chunk)
#             print("end chunk")
#         print("="*50)
#         print("\n")
#     if not duplicate_groups:
#         print("No duplicate groups found.")

def print_groups(duplicate_groups):
    print(f"\nFound {len(duplicate_groups)} duplicate groups:\n")
    
    for i, (group, similarity) in enumerate(duplicate_groups, 1):
        print("="*60)
        print(f"Duplicate Group {i} - Similarity: {similarity:.3f}")
        print("="*60)
        
        for j, chunk in enumerate(group, 1):
            # Determine if it's a method or code block
            chunk_type = "Method" if ("public" in chunk or "private" in chunk) and "(" in chunk else "Code Block"
            print(f"\n{chunk_type} {j}:")
            print("-" * 30)
            # Clean up the chunk display
            clean_chunk = '\n'.join(line for line in chunk.split('\n') if line.strip())
            print(clean_chunk)
            print("-" * 30)
        
        print("\n")
    
    if not duplicate_groups:
        print("No duplicate groups found.")
        
if __name__ == "__main__":

    java_code = """
    public class DuplicateExample {
        // Duplicate method 1 - calculateSum
        public int calculateSum(int a, int b) {
            int result = a + b;
            System.out.println("Sum calculated: " + result);
            return result;
        }
        
        // Duplicate method 2 - same as calculateSum
        public int addNumbers(int x, int y) {
            int result = x + y;
            System.out.println("Sum calculated: " + result);
            return result;
        }
        
        // Duplicate method 3 - slight variation of calculateSum
        public int computeTotal(int num1, int num2) {
            int result = num1 + num2;
            System.out.println("Sum calculated: " + result);
            return result;
        }
        
        // Duplicate loop pattern 1
        public void printNumbers1() {
            for (int i = 0; i < 10; i++) {
                System.out.println("Number: " + i);
            }
        }
        
        // Duplicate loop pattern 2 - same logic
        public void displayNumbers() {
            for (int j = 0; j < 10; j++) {
                System.out.println("Number: " + j);
            }
        }
        
        // Duplicate validation pattern 1
        public boolean validateUser(String username, String password) {
            if (username == null || username.isEmpty()) {
                return false;
            }
            if (password == null || password.length() < 6) {
                return false;
            }
            return true;
        }
        
        // Duplicate validation pattern 2
        public boolean checkCredentials(String user, String pass) {
            if (user == null || user.isEmpty()) {
                return false;
            }
            if (pass == null || pass.length() < 6) {
                return false;
            }
            return true;
        }
        
        // Non-duplicate method for comparison
        public void processData(String data) {
            if (data != null) {
                String processed = data.trim().toUpperCase();
                System.out.println("Processed: " + processed);
            }
        }
        
        // Another duplicate - file reading pattern 1
        public String readFile(String filename) {
            try {
                BufferedReader reader = new BufferedReader(new FileReader(filename));
                String line = reader.readLine();
                reader.close();
                return line;
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }
        
        // Duplicate file reading pattern 2
        public String loadFile(String path) {
            try {
                BufferedReader reader = new BufferedReader(new FileReader(path));
                String line = reader.readLine();
                reader.close();
                return line;
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }
    }
    """

    # Use enhanced detection for intra-method duplicates
    duplicate_groups = detect_duplicate_groups_enhanced(java_code, threshold=0.90, detect_intra_method=True, prefer_methods=True)
    # print_groups(duplicate_groups)
    print(duplicate_groups)