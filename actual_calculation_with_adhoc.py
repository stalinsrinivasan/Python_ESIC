import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ContributionAnalyzer:
    def __init__(self):
        self.data = None
        self.results = []
        
    def load_data(self, file_path):
        """
        Load data from various file formats (CSV, Excel)
        Expected columns: Month, Year, ContributionAmount, NumberOfEmployees, 
                         ContributionPaid, ChallanAmount, ChallanNumber, 
                         ChallanCreatedDate, ChallanRealisedDate
        """
        try:
            if file_path.endswith('.csv'):
                import csv
                try:
                    # First, try to detect the actual data start
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Look for the actual header row (containing expected column names)
                    header_row = 0
                    expected_keywords = ['month', 'year', 'contribution', 'employee', 'challan']
                    
                    for i, line in enumerate(lines[:20]):  # Check first 20 lines
                        line_lower = line.lower()
                        if any(keyword in line_lower for keyword in expected_keywords):
                            header_row = i
                            break
                    
                    # Try loading with detected header row
                    self.data = pd.read_csv(file_path, skiprows=header_row, encoding='utf-8')
                    
                    # If that fails, try different approaches
                    if self.data.empty or len(self.data.columns) < 5:
                        # Try with different encodings and parameters
                        encodings = ['utf-8', 'cp1252', 'iso-8859-1']
                        for encoding in encodings:
                            try:
                                # Try skipping first few rows and auto-detect delimiter
                                for skip in range(0, min(10, len(lines))):
                                    self.data = pd.read_csv(file_path, skiprows=skip, encoding=encoding, 
                                                          sep=None, engine='python')
                                    if len(self.data.columns) >= 5 and not self.data.empty:
                                        print(f"Successfully loaded with encoding: {encoding}, skipping {skip} rows")
                                        break
                                if len(self.data.columns) >= 5 and not self.data.empty:
                                    break
                            except Exception as e:
                                continue
                        
                        # If still failing, try manual delimiter detection
                        if self.data.empty or len(self.data.columns) < 5:
                            delimiters = [',', ';', '\t', '|']
                            for delimiter in delimiters:
                                try:
                                    for skip in range(0, min(5, len(lines))):
                                        self.data = pd.read_csv(file_path, skiprows=skip, 
                                                              delimiter=delimiter, encoding='utf-8')
                                        if len(self.data.columns) >= 5 and not self.data.empty:
                                            print(f"Successfully loaded with delimiter: '{delimiter}', skipping {skip} rows")
                                            break
                                    if len(self.data.columns) >= 5 and not self.data.empty:
                                        break
                                except Exception:
                                    continue
                
                except Exception as csv_e:
                    print(f"CSV loading failed: {csv_e}\nTrying to load as Excel...")
                    try:
                        self.data = pd.read_excel(file_path)
                        print("Loaded as Excel successfully.")
                    except Exception as excel_e:
                        print(f"Excel loading with default engine failed: {excel_e}\nTrying with openpyxl...")
                        try:
                            self.data = pd.read_excel(file_path, engine='openpyxl')
                            print("Loaded as Excel with openpyxl successfully.")
                        except Exception as openpyxl_e:
                            print(f"Excel loading with openpyxl failed: {openpyxl_e}\nTrying with xlrd...")
                            try:
                                self.data = pd.read_excel(file_path, engine='xlrd')
                                print("Loaded as Excel with xlrd successfully.")
                            except Exception as xlrd_e:
                                print(f"Excel loading with xlrd also failed: {xlrd_e}")
                                print("Printing first 500 bytes of the file for inspection:")
                                try:
                                    with open(file_path, 'rb') as f:
                                        print(f.read(500))
                                except Exception as read_e:
                                    print(f"Could not read file bytes: {read_e}")
                                return False
            elif file_path.endswith(('.xlsx', '.xls')):
                try:
                    self.data = pd.read_excel(file_path)
                except Exception as excel_e:
                    print(f"Excel loading with default engine failed: {excel_e}\nTrying with openpyxl...")
                    try:
                        self.data = pd.read_excel(file_path, engine='openpyxl')
                        print("Loaded as Excel with openpyxl successfully.")
                    except Exception as openpyxl_e:
                        print(f"Excel loading with openpyxl failed: {openpyxl_e}\nTrying with xlrd...")
                        try:
                            self.data = pd.read_excel(file_path, engine='xlrd')
                            print("Loaded as Excel with xlrd successfully.")
                        except Exception as xlrd_e:
                            print(f"Excel loading with xlrd also failed: {xlrd_e}")
                            print("Printing first 500 bytes of the file for inspection:")
                            try:
                                with open(file_path, 'rb') as f:
                                    print(f.read(500))
                            except Exception as read_e:
                                print(f"Could not read file bytes: {read_e}")
                            return False
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel files.")
            
            print(f"Data loaded successfully. Shape: {self.data.shape}")
            print(f"Columns: {list(self.data.columns)}")
            print("First few rows:")
            print(self.data.head())
            
            # Clean column names (remove extra spaces, quotes)
            self.data.columns = [col.strip().strip('"').strip("'") for col in self.data.columns]
            
            # Validate required columns with flexible matching
            required_columns = ['Month', 'Year', 'ContributionAmount', 'ChallanRealisedDate', 'ChallanAmount']
            missing_columns = []
            
            # Create a mapping for flexible column name matching
            column_mapping = {}
            data_columns_lower = [col.lower() for col in self.data.columns]
            
            for req_col in required_columns:
                found = False
                req_col_lower = req_col.lower()
                
                # Direct match
                if req_col in self.data.columns:
                    found = True
                else:
                    # Flexible matching
                    for i, col in enumerate(self.data.columns):
                        col_lower = col.lower()
                        if ('month' in req_col_lower and 'month' in col_lower) or \
                           ('year' in req_col_lower and 'year' in col_lower) or \
                           ('contribution' in req_col_lower and 'contribution' in col_lower) or \
                           ('challan' in req_col_lower and 'challan' in col_lower and 'realised' in col_lower) or \
                           ('challan' in req_col_lower and 'challan' in col_lower and 'amount' in col_lower):
                            column_mapping[req_col] = self.data.columns[i]
                            found = True
                            break
                
                if not found:
                    missing_columns.append(req_col)
            
            # Rename columns based on mapping
            if column_mapping:
                self.data = self.data.rename(columns={v: k for k, v in column_mapping.items()})
                print(f"Column mapping applied: {column_mapping}")
            
            if missing_columns:
                print(f"Warning: Missing columns: {missing_columns}")
                print("Available columns:")
                for i, col in enumerate(self.data.columns):
                    print(f"  {i}: {col}")
                print("\nPlease check if the column names match your data.")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            print("If this is a CSV file, please check the delimiter and file format. Try opening the file in a text editor to verify.")
            return False
    
    def preprocess_data(self):
        """
        Preprocess the data - handle missing values, data types, etc.
        """
        # Convert ChallanRealisedDate to datetime if it's not already
        if 'ChallanRealisedDate' in self.data.columns:
            self.data['ChallanRealisedDate'] = pd.to_datetime(self.data['ChallanRealisedDate'], errors='coerce')
        
        if 'ChallanCreatedDate' in self.data.columns:
            self.data['ChallanCreatedDate'] = pd.to_datetime(self.data['ChallanCreatedDate'], errors='coerce')
        
        # Ensure numeric columns are properly formatted
        numeric_columns = ['ContributionAmount', 'ChallanAmount', 'NumberOfEmployees']
        for col in numeric_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
        
        # Create month-year combination for grouping
        self.data['MonthYear'] = self.data['Month'].astype(str) + '-' + self.data['Year'].astype(str)
        
        # Handle missing values
        self.data['ChallanAmount'] = self.data['ChallanAmount'].fillna(0)
        self.data['NumberOfEmployees'] = self.data['NumberOfEmployees'].fillna(0)
        
        # Create a row identifier for tracking multiple entries
        self.data['RowID'] = range(len(self.data))
        
        print("Data preprocessing completed.")
        print(f"Data shape after preprocessing: {self.data.shape}")
        return self.data.head()
    
    def analyze_contributions(self):
        """
        Main analysis function that applies the three conditions
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return None
        
        self.results = []  # Reset results
        
        # Group by Month and Year to analyze each month separately
        grouped_data = self.data.groupby(['Month', 'Year'])
        
        for (month, year), group in grouped_data:
            self._analyze_month_group(group, month, year)
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(self.results)

        # Filter out entries with Reasoning 'No default amount'
        results_df = results_df[results_df['Reasoning'] != 'No default amount']
        
        return results_df
    
    def _analyze_month_group(self, group, month, year):
        """
        Analyze each month-year combination based on the conditions
        """
        # Separate entries with and without challan realized dates
        # Treat entries as 'not paid' if ChallanRealisedDate is missing, regardless of ChallanAmount
        entries_with_challan = group[group['ChallanRealisedDate'].notna()].copy()
        entries_without_challan = group[group['ChallanRealisedDate'].isna()].copy()
        
        # Contribution amount is unique per period, so take the first value
        unique_contribution = group['ContributionAmount'].iloc[0]
        total_contribution = unique_contribution
        total_challan = entries_with_challan['ChallanAmount'].sum()  # Only sum paid challans
        total_employees = group['NumberOfEmployees'].sum()
        
        reasoning = []
        detailed_breakdown = []
        
        # Calculate the shortfall amount (this is the actual default amount)
        shortfall_amount = max(0, total_contribution - total_challan)
        
        # Condition 1: No Payment Filed (No ChallanRealisedDate, even if ChallanAmount is present)
        if len(entries_without_challan) > 0:
            no_payment_amount = entries_without_challan['ContributionAmount'].sum()
            no_payment_employees = entries_without_challan['NumberOfEmployees'].sum()
            reasoning.append(f"No payment filed: ₹{no_payment_amount:,.2f} ({no_payment_employees} employees)")
            detailed_breakdown.append({
                'condition': 'No Payment Filed',
                'amount': no_payment_amount,
                'employees': no_payment_employees,
                'entries': len(entries_without_challan)
            })
        
        # Process entries with challan dates
        if len(entries_with_challan) > 0:
            # Group by ContributionAmount to handle multiple entries with same contribution
            contribution_groups = entries_with_challan.groupby('ContributionAmount')
            
            processed_contributions = set()
            
            for contribution_amt, contrib_group in contribution_groups:
                if contribution_amt in processed_contributions:
                    continue

                actual_contribution_amt = contrib_group['ContributionAmount'].iloc[0]
                total_challan_for_contribution = contrib_group['ChallanAmount'].sum()
                num_entries = len(contrib_group)
                employees_in_group = contrib_group['NumberOfEmployees'].sum()
                
                if num_entries == 1:
                    # Condition 2: Single entry, check if challan < contribution
                    challan_amt = contrib_group['ChallanAmount'].iloc[0]
                    if challan_amt < actual_contribution_amt:
                        individual_shortfall = actual_contribution_amt - challan_amt
                        reasoning.append(f"Single entry shortfall: ₹{individual_shortfall:,.2f} (₹{actual_contribution_amt:,.2f} - ₹{challan_amt:,.2f})")
                        detailed_breakdown.append({
                            'condition': 'Single Entry Shortfall',
                            'amount': individual_shortfall,
                            'employees': employees_in_group,
                            'entries': 1,
                            'contribution': contribution_amt,
                            'challan': challan_amt
                        })
                else:
                    # Condition 3: Multiple entries with same contribution amount
                    if total_challan_for_contribution < actual_contribution_amt:
                        individual_shortfall = actual_contribution_amt - total_challan_for_contribution
                        reasoning.append(f"Multiple entries shortfall: ₹{individual_shortfall:,.2f} ({num_entries} entries, ₹{actual_contribution_amt:,.2f} - ₹{total_challan_for_contribution:,.2f})")
                        detailed_breakdown.append({
                            'condition': 'Multiple Entries Shortfall',
                            'amount': individual_shortfall,
                            'employees': employees_in_group,
                            'entries': num_entries,
                            'contribution': actual_contribution_amt,
                            'total_challan': total_challan_for_contribution
                        })
                
                processed_contributions.add(contribution_amt)
        
        # Calculate metrics based on the shortfall amount
        default_percentage = (shortfall_amount / total_contribution * 100) if total_contribution > 0 else 0
        payment_percentage = (total_challan / total_contribution * 100) if total_contribution > 0 else 0
        
        # Store results - Use shortfall_amount as the default amount consistently
        result_entry = {
            'Month': month,
            'Year': year,
            'MonthYear': f"{month}-{year}",
            'TotalContribution': total_contribution,
            'TotalChallan': total_challan,
            'TotalEmployees': total_employees,
            'DefaultActualAmount': shortfall_amount,  # This is the consistent shortfall amount
            'DefaultPercentage': round(default_percentage, 2),
            'PaymentPercentage': round(payment_percentage, 2),
            'TotalEntries': len(group),
            'EntriesWithPayment': len(entries_with_challan),
            'EntriesWithoutPayment': len(entries_without_challan),
            'Reasoning': '; '.join(reasoning) if reasoning else 'No default amount',
            'DetailedBreakdown': detailed_breakdown
        }
        
        self.results.append(result_entry)
        
        # Print monthly analysis
        print(f"\n--- Analysis for {month}/{year} ---")
        print(f"Total Contribution: ₹{total_contribution:,.2f}")
        print(f"Total Challan Paid: ₹{total_challan:,.2f}")
        print(f"Default Amount (Shortfall): ₹{shortfall_amount:,.2f} ({default_percentage:.2f}%)")
        if reasoning:
            for reason in reasoning:
                print(f"  - {reason}")
    
    def generate_summary_statistics(self, results_df):
        """
        Generate comprehensive summary statistics
        """
        if results_df is None or results_df.empty:
            print("No results to summarize.")
            return None
        
        # Overall statistics
        total_contribution = results_df['TotalContribution'].sum()
        total_challan = results_df['TotalChallan'].sum()
        total_default = results_df['DefaultActualAmount'].sum()
        total_employees = results_df['TotalEmployees'].sum()
        
        # Monthly averages
        avg_monthly_contribution = results_df['TotalContribution'].mean()
        avg_monthly_default = results_df['DefaultActualAmount'].mean()
        
        # Create summary dictionary
        summary_stats = {
            'total_contribution': total_contribution,
            'total_challan_paid': total_challan,
            'total_default_amount': total_default,
            'total_employees': total_employees,
            'overall_default_percentage': (total_default / total_contribution * 100) if total_contribution > 0 else 0,
            'overall_payment_percentage': (total_challan / total_contribution * 100) if total_contribution > 0 else 0,
            'avg_monthly_contribution': avg_monthly_contribution,
            'avg_monthly_default': avg_monthly_default,
            'number_of_months': len(results_df),
            'months_with_defaults': len(results_df[results_df['DefaultActualAmount'] > 0]),
        }
        
        return summary_stats
    
    def create_detailed_breakdown_sheet(self, results_df):
        """
        Create detailed breakdown data for Excel export
        """
        breakdown_data = []
        
        for _, row in results_df.iterrows():
            if row['DetailedBreakdown']:
                for breakdown in row['DetailedBreakdown']:
                    breakdown_entry = {
                        'Month': row['Month'],
                        'Year': row['Year'],
                        'MonthYear': row['MonthYear'],
                        'Condition': breakdown['condition'],
                        'DefaultAmount': breakdown['amount'],
                        'Employees': breakdown['employees'],
                        'Entries': breakdown['entries']
                    }
                    
                    # Add specific fields based on condition
                    if 'contribution' in breakdown:
                        breakdown_entry['ContributionAmount'] = breakdown['contribution']
                    if 'challan' in breakdown:
                        breakdown_entry['ChallanAmount'] = breakdown['challan']
                    if 'total_challan' in breakdown:
                        breakdown_entry['TotalChallanAmount'] = breakdown['total_challan']
                    
                    breakdown_data.append(breakdown_entry)
        
        return pd.DataFrame(breakdown_data)
    
    def export_to_excel(self, results_df, output_file='employer_contribution_analysis.xlsx'):
        """
        Export results to Excel with multiple sheets and formatting
        """
        # Filter out entries with Reasoning 'No default amount'
        results_df = results_df[results_df['Reasoning'] != 'No default amount']
        try:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # Main results - include all entries, even those with zero defaults
                results_export = results_df[['Month', 'Year', 'TotalContribution', 'TotalChallan', 'TotalEmployees', 'DefaultActualAmount', 'Reasoning']]
                results_export.to_excel(writer, sheet_name='Monthly_Analysis', index=False)
                
                # Detailed breakdown
                breakdown_df = self.create_detailed_breakdown_sheet(results_df)
                if not breakdown_df.empty:
                    breakdown_df.to_excel(writer, sheet_name='Detailed_Breakdown', index=False)
                
                # Summary statistics
                summary_stats = self.generate_summary_statistics(results_df)
                if summary_stats:
                    summary_df = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
                    summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
                
                # Get workbook and add formatting
                workbook = writer.book
                
                # Define formats
                money_format = workbook.add_format({'num_format': '₹#,##0.00'})
                percentage_format = workbook.add_format({'num_format': '0.00%'})
                header_format = workbook.add_format({
                    'bold': True, 
                    'bg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Format Monthly Analysis sheet
                worksheet1 = writer.sheets['Monthly_Analysis']
                for col_num, value in enumerate(results_export.columns.values):
                    worksheet1.write(0, col_num, value, header_format)
                
                # Format money columns
                money_cols = ['TotalContribution', 'TotalChallan', 'DefaultActualAmount']
                for col in money_cols:
                    if col in results_export.columns:
                        col_idx = results_export.columns.get_loc(col)
                        worksheet1.set_column(col_idx, col_idx, 18, money_format)
                
                # Format percentage columns
                pct_cols = ['DefaultPercentage', 'PaymentPercentage']
                for col in pct_cols:
                    if col in results_export.columns:
                        col_idx = results_export.columns.get_loc(col)
                        worksheet1.set_column(col_idx, col_idx, 15)
                
                # Format other sheets similarly
                if not breakdown_df.empty:
                    worksheet2 = writer.sheets['Detailed_Breakdown']
                    for col_num, value in enumerate(breakdown_df.columns.values):
                        worksheet2.write(0, col_num, value, header_format)
                
            print(f"Results exported successfully to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            return False
    
    def print_summary(self, results_df):
        """
        Print comprehensive summary
        """
        # Filter out entries with Reasoning 'No default amount'
        results_df = results_df[results_df['Reasoning'] != 'No default amount']
        print("\n" + "="*80)
        print("EMPLOYER CONTRIBUTION DEFAULT AMOUNT ANALYSIS SUMMARY")
        print("="*80)
        
        if results_df is not None and not results_df.empty:
            summary_stats = self.generate_summary_statistics(results_df)
            
            if summary_stats:
                print(f"Analysis Period: {results_df['MonthYear'].min()} to {results_df['MonthYear'].max()}")
                print(f"Number of Months Analyzed: {summary_stats['number_of_months']}")
                print(f"Months with Defaults: {summary_stats['months_with_defaults']}")
                print(f"Total Employees: {summary_stats['total_employees']:,.0f}")
                print()
                print(f"Total Contribution Amount: ₹{summary_stats['total_contribution']:,.2f}")
                print(f"Total Challan Paid: ₹{summary_stats['total_challan_paid']:,.2f}")
                print(f"Total Default Amount: ₹{summary_stats['total_default_amount']:,.2f}")
                print()
                print(f"Overall Payment Rate: {summary_stats['overall_payment_percentage']:.2f}%")
                print(f"Overall Default Rate: {summary_stats['overall_default_percentage']:.2f}%")
                print()
                print(f"Average Monthly Contribution: ₹{summary_stats['avg_monthly_contribution']:,.2f}")
                print(f"Average Monthly Default: ₹{summary_stats['avg_monthly_default']:,.2f}")
                
                # Top months with highest defaults
                print("\nTop 5 Months with Highest Default Amounts:")
                top_defaults = results_df.nlargest(5, 'DefaultActualAmount')[
                    ['MonthYear', 'DefaultActualAmount', 'DefaultPercentage', 'TotalEmployees']
                ]
                print(top_defaults.to_string(index=False, formatters={
                    'DefaultActualAmount': lambda x: f"₹{x:,.2f}",
                    'DefaultPercentage': lambda x: f"{x:.2f}%",
                    'TotalEmployees': lambda x: f"{x:,.0f}"
                }))

def main():
    """
    Main function to run the analysis or adhoc month count
    """
    # Initialize analyzer
    analyzer = ContributionAnalyzer()
    # Load data (replace with your file path)
    # file_path = "contribution_data.xlsx"  # Change this to your file path
    file_name = input("Enter the name of your contribution data file (without extension, located in the current directory): ")
    file_name = file_name.strip()
    import os
    # Try possible extensions
    possible_extensions = ['.csv', '.xlsx', '.xls']
    file_path = None
    for ext in possible_extensions:
        candidate = file_name + ext
        if os.path.isfile(candidate):
            file_path = candidate
            break
    if not file_path:
        print(f"File not found with any of the supported extensions (.csv, .xlsx, .xls): {file_name}")
        return

    # Ask user for choice
    print("\nSelect an option:")
    print("1. Actual Calculation (Default)")
    print("2. Adhoc Month Count (Find missing periods)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '2':
        # Import and call the Adhoc Month Count logic
        try:
            # Try importing from the same directory first (for exe)
            from Adhoc_Month_Find import find_missing_periods, get_output_filename
        except ImportError:
            try:
                # Try importing from subdirectory
                import sys
                import os
                # Get the directory where the script/exe is located
                if getattr(sys, 'frozen', False):
                    # Running as exe
                    script_dir = os.path.dirname(sys.executable)
                else:
                    # Running as script
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                adhoc_path = os.path.join(script_dir, 'Adhoc_Month_Find_Python_Program')
                if os.path.exists(adhoc_path):
                    sys.path.insert(0, adhoc_path)
                from Adhoc_Month_Find import find_missing_periods, get_output_filename
            except ImportError as e:
                print(f"Could not import Adhoc_Month_Find: {e}")
                print("Please ensure Adhoc_Month_Find.py is in the same directory as this executable")
                return
        print("\nRunning Adhoc Month Count...")
        output_file = get_output_filename(file_path)
        missing_periods = find_missing_periods(file_path, output_file)
        if not missing_periods.empty:
            print(f"\nMissing Periods:")
            print(missing_periods.to_string(index=False))
        else:
            print("No missing periods found!")
        print(f"\nResults saved to: {output_file}")
        return
    else:
        print("Starting Employer Contribution Default Amount Analysis...")
        print("-" * 80)
        # Load and preprocess data
        if analyzer.load_data(file_path):
            print("\nPreprocessing data...")
            analyzer.preprocess_data()
            # Run analysis
            print("\nAnalyzing contributions based on specified conditions...")
            results = analyzer.analyze_contributions()
            if results is not None and not results.empty:
                # Print summary
                analyzer.print_summary(results)
                # Export to Excel with suffix
                input_base = os.path.splitext(os.path.basename(file_path))[0]
                output_file = f"employer_contribution_analysis_{input_base}.xlsx"
                print(f"\nExporting results to Excel as {output_file} ...")
                analyzer.export_to_excel(results, output_file=output_file)
                print("\nAnalysis completed successfully!")
                print(f"Check the generated Excel file ({output_file}) for detailed results.")
            else:
                print("No results generated. Please check your data format.")
        else:
            print("Failed to load data. Please check the file path and format.")

def create_sample_data():
    """
    Create sample data matching the specified format for testing
    """
    np.random.seed(42)
    
    months = list(range(1, 13))
    years = [2023, 2024]
    
    sample_data = []
    
    for year in years:
        for month in months[:8]:  # 8 months of data per year
            # Create multiple scenarios for each month
            scenarios = ['no_payment', 'partial_payment', 'full_payment', 'multiple_partial']
            
            for scenario in scenarios:
                if np.random.random() > 0.7:  # Skip some scenarios randomly
                    continue
                
                contrib_amt = np.random.randint(50000, 500000)
                num_employees = np.random.randint(10, 100)
                
                if scenario == 'no_payment':
                    sample_data.append({
                        'Month': month,
                        'Year': year,
                        'ContributionAmount': contrib_amt,
                        'NumberOfEmployees': num_employees,
                        'ContributionPaid': 0,
                        'ChallanAmount': None,
                        'ChallanNumber': None,
                        'ChallanCreatedDate': None,
                        'ChallanRealisedDate': None
                    })
                
                elif scenario == 'partial_payment':
                    challan_amt = contrib_amt * np.random.uniform(0.5, 0.9)
                    challan_number = f"CH{year}{month:02d}{np.random.randint(1000, 9999)}"
                    challan_date = f"{year}-{month:02d}-{np.random.randint(15, 28)}"
                    
                    sample_data.append({
                        'Month': month,
                        'Year': year,
                        'ContributionAmount': contrib_amt,
                        'NumberOfEmployees': num_employees,
                        'ContributionPaid': challan_amt,
                        'ChallanAmount': challan_amt,
                        'ChallanNumber': challan_number,
                        'ChallanCreatedDate': challan_date,
                        'ChallanRealisedDate': challan_date
                    })
                
                elif scenario == 'full_payment':
                    challan_number = f"CH{year}{month:02d}{np.random.randint(1000, 9999)}"
                    challan_date = f"{year}-{month:02d}-{np.random.randint(10, 25)}"
                    
                    sample_data.append({
                        'Month': month,
                        'Year': year,
                        'ContributionAmount': contrib_amt,
                        'NumberOfEmployees': num_employees,
                        'ContributionPaid': contrib_amt,
                        'ChallanAmount': contrib_amt,
                        'ChallanNumber': challan_number,
                        'ChallanCreatedDate': challan_date,
                        'ChallanRealisedDate': challan_date
                    })
                
                elif scenario == 'multiple_partial':
                    # Create multiple entries for same contribution amount
                    base_challan = contrib_amt * 0.3
                    for i in range(2):
                        challan_number = f"CH{year}{month:02d}{np.random.randint(1000, 9999)}"
                        challan_date = f"{year}-{month:02d}-{15 + i*3}"
                        
                        sample_data.append({
                            'Month': month,
                            'Year': year,
                            'ContributionAmount': contrib_amt,
                            'NumberOfEmployees': num_employees // 2,
                            'ContributionPaid': base_challan,
                            'ChallanAmount': base_challan,
                            'ChallanNumber': challan_number,
                            'ChallanCreatedDate': challan_date,
                            'ChallanRealisedDate': challan_date
                        })
    
    # Create DataFrame and save
    df = pd.DataFrame(sample_data)
    df.to_excel('contribution_data.xlsx', index=False)
    print("Sample data created: contribution_data.xlsx")
    print(f"Sample data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    return df

if __name__ == "__main__":
    # Uncomment the next line to create sample data for testing
    # create_sample_data()
    
    # Run the main analysis
    main()