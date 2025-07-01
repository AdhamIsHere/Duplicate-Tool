# Duplicate Tool v0.2

A sophisticated tool for detecting duplicate code in Java files using CodeT5 embeddings and cosine similarity analysis.

## Features

- **Inter-method duplicate detection**: Finds similar methods across different classes/files
- **Intra-method duplicate detection**: Identifies duplicate code blocks within methods
- **Google Java Format integration**: Normalizes code formatting for better detection accuracy
- **CodeT5 embeddings**: Uses state-of-the-art transformer models for semantic code understanding
- **Configurable similarity thresholds**: Adjust detection sensitivity
- **Connected components grouping**: Advanced algorithm to group related duplicates

## Installation

```bash
pip install duplicate_tool-0.2.tar.gz
```

## Requirements

- Python 3.8+
- PyTorch
- Transformers
- scikit-learn
- NumPy
- Java Runtime Environment (for Google Java Format)

## Usage

### As a Python Module

```python
from Duplicate_Tool.detection import detect_duplicate_groups_enhanced
from Duplicate_Tool.preprocessing import format_java_code

java_code = """
public class Example {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int sum(int x, int y) {
        return x + y;
    }
}
"""

# Detect duplicates with formatting
duplicates = detect_duplicate_groups_enhanced(
    java_code, 
    threshold=0.90, 
    detect_intra_method=True, 
    prefer_methods=True, 
    use_formatting=True
)

for group, similarity in duplicates:
    print(f"Duplicate group (similarity: {similarity:.3f}):")
    for chunk in group:
        print(chunk)
        print("-" * 40)
```

### Command Line Interface

```bash
# Run duplicate detection on sample code
duplicate-tool
```

## Configuration Options

- **threshold**: Similarity threshold for duplicate detection (default: 0.90)
- **detect_intra_method**: Enable detection of duplicates within methods (default: True)
- **prefer_methods**: Prioritize complete method duplicates over code blocks (default: True)
- **use_formatting**: Apply Google Java Format for better accuracy (default: True)

## How It Works

1. **Code Normalization**: Optionally formats Java code using Google Java Format
2. **Chunk Extraction**: Extracts methods and code blocks from the source
3. **Embedding Generation**: Uses CodeT5 to generate semantic embeddings
4. **Similarity Analysis**: Computes cosine similarity between all code chunks
5. **Group Formation**: Uses connected components algorithm to group similar code

## Examples

### Inter-method Duplicates
Detects when entire methods have similar functionality:

```java
public int calculateSum(int a, int b) {
    int result = a + b;
    return result;
}

public int addNumbers(int x, int y) {
    int result = x + y;
    return result;
}
```

### Intra-method Duplicates
Finds repeated code patterns within different methods:

```java
public void processUsers() {
    // Duplicate validation pattern
    if (user == null || user.isEmpty()) {
        return false;
    }
}

public void validateInput() {
    // Same validation pattern
    if (input == null || input.isEmpty()) {
        return false;
    }
}
```

## Version History

### v0.2
- Added Google Java Format integration
- Improved similarity thresholds and grouping algorithms
- Enhanced intra-method duplicate detection
- Better code block extraction
- Added comprehensive CLI interface

### v0.1
- Initial release with basic duplicate detection
- CodeT5 embedding integration
- Basic similarity analysis

## License

MIT License

## Author

Adham Mohamed
