import pandas as pd

# Load CSV file
csv_file = "C:\\Users\\sophi\\Downloads\\export_demo.csv"  # Replace with your actual CSV file path
df = pd.read_csv(csv_file, sep=';')
df_excel = pd.read_excel("C:\\Users\\sophi\\Documents\\PersonalProjects\\code\\deforestation_map\\data\\input\\raw\\plots_colombia.xlsx")
df_excel.head()

# Save as Excel file
xlsx_file = "C:\\Users\\sophi\\Documents\\PersonalProjects\\code\\deforestation_map\\data\\input\\raw\\export_demo.xlsx"  # Replace with your desired output file name
df.to_excel(xlsx_file, index=False, engine='openpyxl')

print(f"CSV file has been converted to {xlsx_file}")

(pd.read_excel("C:\\Users\\sophi\\Documents\\PersonalProjects\\code\\deforestation_map\\data\\input\\raw\\export_demo.xlsx")).head()