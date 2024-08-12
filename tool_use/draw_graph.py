# from PIL import Image
# import pytesseract
# import pandas as pd

# # Load the uploaded image
# image_path = "/mnt/data/6712C1A7-6CA5-4C78-AF11-113012338F10.png"
# image = Image.open(image_path)

# # Use pytesseract to extract text from the image
# text = pytesseract.image_to_string(image)
# text
import matplotlib.pyplot as plt

# Extract the data for the plot
methods = ['zero-shot', 'asrank-zero-shot', 'asrank-zero-shot-COT', 'few-shot', 'few-shot-COT', 'rag-COT (clique+transit degree)', 'fine-tune']
acc_values = [0.58, 0.56, 0.56, 0.63, 0.65, 0.62, 0.75]  # Assuming 66/88 translates to 0.75 accuracy

# Recreate the bar chart with non-tilted text, using line breaks for labels
plt.figure(figsize=(10, 6))
plt.bar(methods, acc_values, color='skyblue')
plt.axhline(y=0.53, color='red', linestyle='--', linewidth=1, label='ASrank algorithm')
plt.xlabel('Method')
plt.ylabel('Accuracy (Acc)')
plt.title('Accuracy for Different Methods')
plt.ylim(0, 1)
plt.grid(axis='y')
plt.legend(loc='upper right')

# Adjust x-tick labels with line breaks for better readability
methods_wrapped = [
    'zero-shot', 
    'asrank-\nzero-shot', 
    'asrank-zero-\nshot-COT', 
    'few-shot', 
    'few-shot-\nCOT', 
    'rag-COT\n(clique+transit\ndegree)', 
    'fine-tune'
]
plt.xticks(range(len(methods_wrapped)), methods_wrapped)

# Show the plot with the new label formatting
plt.tight_layout()
plt.show()