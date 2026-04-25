from reviewer import review_code

code = input("Paste your code:\n")

result = review_code(code)

print("\n--- AI Review ---\n")
print(result)