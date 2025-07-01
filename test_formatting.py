import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Duplicate_Tool'))

from preprocessing import format_java_code, normalize_code

# Test code with inconsistent formatting
test_code = """
public class TestFormat{
public int calculate(int a,int b){
int result=a+b;
System.out.println("Result: "+result);
return result;}

public int add(int x,   int y)   {
    int sum = x + y;
    System.out.println("Sum: " + sum);
    return sum;
}
}
"""

print("="*50)
print("ORIGINAL CODE:")
print("="*50)
print(test_code)

print("\n" + "="*50)
print("GOOGLE JAVA FORMAT:")
print("="*50)
formatted = format_java_code(test_code)
print(formatted)

print("\n" + "="*50)
print("BASIC NORMALIZATION:")
print("="*50)
normalized = normalize_code(test_code)
print(normalized)
