import pandas as pd
import numpy as np

# Read the Excel file containing payment details for a single customer
file_path = input("Enter the C6 File Name: ") + ".xlsx"
df = pd.read_excel(file_path)

# Extract month and year from the 'Month' column
df['Month'] = pd.to_datetime(df['Month'], format='%b %Y')

# Generate a list of all months in the year
all_months = pd.period_range(start=df['Month'].min(), end=df['Month'].max(), freq='M')

# Extract unique months from the DataFrame
unique_months = pd.to_datetime(df['Month']).dt.to_period('M')

# Convert both lists to sets for efficient comparison
all_months_set = set(all_months)
unique_months_set = set(unique_months)

# Find the missing months for the customer
missing_months = sorted(list(all_months_set - unique_months_set))

# Output the missing months
print()
emp_count = int(input("Enter the Number of Employees to calculate Adhoc Amount: "))
print()
print("C18 Adhoc Months:")
print("==================")
for month in missing_months:
    print('[' + month.strftime("%B %Y") + ']')

# Calculate the Adhoc_amount

# Calculate the number of missing months
count_missing_months = len(missing_months)

adhoc_amount = [11550 * 0.04 * emp_count * count_missing_months]
print()
print("Total C18 Adhoc Amount (Rs.):", adhoc_amount)

# Filter rows where 'Challan Realised Date' is NaN and get the corresponding values from the 'Month' column
notrealised_months = df[df['Challan Realised Date'].isna()]['Month']

# Filter the months in notrealised_months that are not in zero_contribution_months
notrealised_months = notrealised_months[~notrealised_months.isin(df[df['Contribution Amount'] == 0]['Month'])]

# Calculate the sum of "Contribution Amount" for notrealised_months
sum_contribution_amount = df[df['Month'].isin(notrealised_months)]['Contribution Amount'].sum()

# Output the months without corresponding values in 'Challan Realised Date'
print()
print("C18 Actual Months:")
print("==================")
for month in notrealised_months:
    print('[' + month.strftime("%B %Y") + ']')

# Filter rows where 'Contribution Amount' is greater than 'Contribution Paid'
df_not_null_realised = df[~df['Challan Realised Date'].isna()]
greater_contribution = df_not_null_realised[df_not_null_realised['Contribution Amount'] > df_not_null_realised['Contribution Paid']]

# Find the months that appear more than once
duplicated_months = greater_contribution[greater_contribution.duplicated(subset='Month', keep=False)]['Month']

# Initialize a list to store the months where 'Contribution Paid' equals 'Contribution Amount'
equal_contribution_months = []

# Iterate over the duplicated months
for month in duplicated_months:
    # Get the rows corresponding to the current month
    month_rows = greater_contribution[greater_contribution['Month'] == month]
    # Calculate the total 'Contribution Paid' for the current month
    total_paid = month_rows['Contribution Paid'].sum()
    # Check if the total 'Contribution Paid' equals the 'Contribution Amount'
    if total_paid == month_rows.iloc[0]['Contribution Amount']:
        equal_contribution_months.append(month)

# Filter the unequal contribution months to exclude those where 'Contribution Paid' equals 'Contribution Amount'
unequal_contribution_months = greater_contribution[~greater_contribution['Month'].isin(equal_contribution_months)]

# Output the months where 'Contribution Amount' and 'Contribution Paid' are not equal and 'Challan Realised Date' is not empty
print()
print("Less Contribution Paid Months")
print("=============================")
for month in unequal_contribution_months['Month']:
    print('[' + month.strftime("%B %Y") + ']')

# Calculate the difference between 'Contribution Amount' and 'Contribution Paid' in unequal_contribution_months
unequal_contribution_months['Difference'] = unequal_contribution_months['Contribution Amount'] - unequal_contribution_months['Contribution Paid']

# Calculate the sum of "Contribution Amount" for notrealised_months including the difference in unequal_contribution_months
sum_contribution_amount_with_difference = sum_contribution_amount + unequal_contribution_months['Difference'].sum()

# Output the updated total C18 Actual amount
print("Total C18 Actual Amount (Rs.):", sum_contribution_amount_with_difference)

zero_contribution_months = df[df['Contribution Amount'] == 0]['Month']
# Output the months with zero contribution amount
print()
print("Nil Filing Months:")
print("==================")
for month in zero_contribution_months:
    print('[' + month.strftime("%B %Y") + ']')

def calculate_due_date(month):
    exceptions = {
        pd.Timestamp('2020-02-01'): pd.Timestamp('2020-05-15'),
        pd.Timestamp('2020-03-01'): pd.Timestamp('2020-05-15'),
        pd.Timestamp('2021-04-01'): pd.Timestamp('2021-06-15'),
        pd.Timestamp('2021-10-01'): pd.Timestamp('2021-11-30'),
        pd.Timestamp('2022-03-01'): pd.Timestamp('2022-04-30'),
        pd.Timestamp('2022-08-01'): pd.Timestamp('2022-09-22')
    }
    if month in exceptions:
        return exceptions[month]
    elif month > pd.Timestamp('2020-05-15') and month < pd.Timestamp('2020-06-15'):
        return pd.Timestamp('2020-05-15')
    elif month > pd.Timestamp('2017-10-15'):
        return (month + pd.DateOffset(months=1)).replace(day=15)
    else:
        return (month + pd.DateOffset(months=1)).replace(day=21)

# Apply the function to each month to get due dates
df['Due Date'] = df['Month'].apply(calculate_due_date)

# Calculate the number of days between due date and challan realized date
df['Days Late'] = (df['Challan Realised Date'] - df['Due Date']).dt.days

interest_rate = 12

# Calculate interest for each month where both challan is realized, and contribution paid equals contribution amount
def calculate_interest(row):
    if pd.isnull(row['Challan Realised Date']) or row['Contribution Paid'] != row['Contribution Amount'] or row['Days Late'] < 0:
        return 0
    else:
        return (row['Contribution Paid'] * row['Days Late'] * interest_rate) / 36500

# Apply the interest calculation function to each row
df['Interest'] = df.apply(calculate_interest, axis=1)

# Filter out rows where 'Challan Realized Date' is not null
df_interest = df[~df['Challan Realised Date'].isna()].copy()

# Convert datetime columns to date format
df_interest['Month'] = df_interest['Month'].dt.date
df_interest['Due Date'] = df_interest['Due Date'].dt.date
df_interest['Challan Realised Date'] = df_interest['Challan Realised Date'].dt.date

# Calculate interest for each row
df_interest['Interest'] = df_interest.apply(calculate_interest, axis=1)

# Round 'Interest' column to two decimal places
df_interest['Interest'] = df_interest['Interest'].round(2)

# Select columns of interest
df_interest = df_interest[['Month', 'Due Date', 'Challan Realised Date', 'Days Late', 'Contribution Paid', 'Interest']]

# Calculate total interest amount
total_interest_amount = round(df['Interest'].sum(), 2)

# Print the total interest amount
print()
print("Total Interest Amount:", total_interest_amount)

damages_rates = {60: 5, 120: 10, 180: 15, float('inf'): 25}

def calculate_damages(row):
    if pd.isnull(row['Challan Realised Date']) or row['Contribution Paid'] != row['Contribution Amount'] or row['Days Late'] < 0:
        return 0
    else:
        days_late = row['Days Late']
        for days, rate in damages_rates.items():
           if days_late < days:
               return (row['Contribution Paid'] * rate * days_late) / 36500

# Apply the damages calculation function to each row
df['Damages'] = df.apply(calculate_damages, axis=1)

# Filter out rows where 'Challan Realized Date' is not null
df_damages = df[~df['Challan Realised Date'].isna()].copy()

# Convert datetime columns to date format
df_damages['Month'] = df_damages['Month'].dt.date
df_damages['Due Date'] = df_damages['Due Date'].dt.date
df_damages['Challan Realised Date'] = df_damages['Challan Realised Date'].dt.date

# Calculate Damages for each row
df_damages['Damages'] = df_damages.apply(calculate_damages, axis=1)

# Round 'Damages' column to two decimal places
df_damages['Damages'] = df_damages['Damages'].round(2)

# Select columns of Damages
df_damages = df_damages[['Month', 'Due Date', 'Challan Realised Date', 'Days Late', 'Contribution Paid', 'Damages']]

# Calculate total Damages amount
total_damages_amount = round(df['Damages'].sum(), 2)

# Print the total Damages amount
print()
print("Total Damages Amount:", total_damages_amount)

# Create a Pandas Excel writer using XlsxWriter as the engine.
with pd.ExcelWriter('Interest_and_Damages.xlsx') as writer:
    # Write each DataFrame to a separate worksheet.
    df_interest.to_excel(writer, sheet_name='Interest', index=False)
    df_damages.to_excel(writer, sheet_name='Damages', index=False)
