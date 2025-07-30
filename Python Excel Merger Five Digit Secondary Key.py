import pandas as pd

#Give Five Digit Employer Code in both primary and secondary keys
# Read the Excel files
file_path = input("Enter the Master Excel File Name: ") + ".xlsx"
closure_file_path = input("Enter the Lookup Excel File Name: ") + ".xlsx"
# Get column names from the user
Primary_Key_Column = input("Enter the Primary Key Column Name: ")
Secondary_Key_Column = input("Enter the Secondary Key Column Name: ")

dtype_spec = {Primary_Key_Column: str, Secondary_Key_Column: str}  # Specify dtype for columns
df = pd.read_excel(file_path, dtype=dtype_spec)
cdf = pd.read_excel(closure_file_path, dtype=dtype_spec)


# Finding Missing Primary Key Column Values in Master
df[Primary_Key_Column] = df[Primary_Key_Column].astype(str).str.strip()
df[Secondary_Key_Column] = df[Secondary_Key_Column].astype(str).str.strip()
cdf[Primary_Key_Column] = cdf[Primary_Key_Column].astype(str).str.strip()
main_employer_codes_set = set(df[Primary_Key_Column])
closure_employer_codes_set = set(cdf[Primary_Key_Column])
missing_employer_codes = closure_employer_codes_set - main_employer_codes_set
missing_df = pd.DataFrame({Primary_Key_Column: list(missing_employer_codes)})
missing_df.to_excel("Missing_Primary_Key.xlsx", index=False)
print("Missing Primary Key Columns in Master File Created")

# Update the Status for only matching fields
# Merge the main file with the closure file using a merge type of "both"
#merged_df = pd.merge(df, cdf[[Primary_Key_Column, Update_Column]], on=Primary_Key_Column, how='outer', indicator=True)
merged_df = pd.merge(df, cdf, on=Primary_Key_Column, how='outer')

# Mark the registration status as "Closed" where applicable
merged_df.to_excel("Merged.xlsx", index=False)
print("Merged File Created")
