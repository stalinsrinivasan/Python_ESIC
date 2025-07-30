import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def find_missing_periods(input_file, output_file=None):
    """
    Process input Excel/CSV file and identify missing periods (Month & Year combinations)
    Only list missing months after the starting period in the data and before the current month/year.
    """
    try:
        # Read input file - detect if it's Excel or CSV
        file_extension = Path(input_file).suffix.lower()
        if file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        elif file_extension == '.csv':
            df = pd.read_csv(input_file)
        else:
            raise ValueError("Unsupported file format. Please use Excel (.xlsx, .xls) or CSV (.csv) files.")
        print(f"Successfully loaded {len(df)} records from {input_file}")
        # Validate required columns
        required_columns = ['Month', 'Year']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        # Get unique years from the dataset
        years = sorted(df['Year'].unique())
        print(f"Years found in data: {years}")
        # Find the earliest (Year, Month) in the data
        min_year = df['Year'].min()
        min_month = df[df['Year'] == min_year]['Month'].min()
        # Get current month and year
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        # Create all possible month-year combinations from the starting period up to before current month/year
        all_periods = []
        for year in years:
            for month in range(1, 13):
                # Only include periods after or equal to (min_year, min_month)
                # and before (current_year, current_month)
                if (year > min_year or (year == min_year and month >= min_month)) and \
                   (year < current_year or (year == current_year and month < current_month)):
                    all_periods.append({'Month': month, 'Year': year})
        all_periods_df = pd.DataFrame(all_periods)
        # Get existing periods from input data
        existing_periods = df[['Month', 'Year']].drop_duplicates()
        # Find missing periods by comparing with all possible periods
        merged = all_periods_df.merge(existing_periods, on=['Month', 'Year'], how='left', indicator=True)
        missing_periods = merged[merged['_merge'] == 'left_only'][['Month', 'Year']]
        # Sort by Year and Month
        missing_periods = missing_periods.sort_values(['Year', 'Month']).reset_index(drop=True)
        print(f"\nFound {len(missing_periods)} missing periods")
        # Save to output file if specified
        if output_file:
            missing_periods.to_excel(output_file, index=False)
            print(f"Results saved to: {output_file}")
        return missing_periods
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return pd.DataFrame()


def get_user_input():
    """
    Get input file name (without extension) from user and validate it exists in the current directory
    """
    supported_extensions = ['.xlsx', '.xls', '.csv']
    while True:
        file_base = input("Enter the input file name (without extension, in current directory): ").strip()
        file_base = file_base.strip('"').strip("'")
        found_file = None
        for ext in supported_extensions:
            candidate = Path(f"{file_base}{ext}")
            if candidate.exists():
                found_file = str(candidate)
                break
        if found_file:
            return found_file
        else:
            print(f"Error: No file named '{file_base}' with supported extension ({', '.join(supported_extensions)}) found in current directory.")

def get_output_filename(input_file):
    """
    Generate output filename based on input filename (no user prompt)
    """
    input_path = Path(input_file)
    default_output = f"missing_periods_{input_path.stem}.xlsx"
    return default_output


def main():
    """
    Main function with user input handling
    """
    print("=== Missing Periods Processor ===\n")
    try:
        # Get input file from user
        input_file = get_user_input()
        # Always use default output filename
        output_file = get_output_filename(input_file)
        print(f"\nProcessing file: {input_file}")
        print("=" * 60)
        # Process the file
        missing_periods = find_missing_periods(input_file, output_file)
        # Display results
        if not missing_periods.empty:
            print(f"\nMissing Periods:")
            print("=" * 20)
            print(missing_periods.to_string(index=False))
            # Show month names for better understanding
            print(f"\nDetailed Missing Periods:")
            print("-" * 30)
            for _, row in missing_periods.iterrows():
                month_name = pd.to_datetime(f"{row['Year']}-{row['Month']}-01").strftime('%B')
                print(f"Month {row['Month']:2d} ({month_name:>9}) - Year {row['Year']}")
        else:
            print("\n✓ No missing periods found! All months are present in the data.")
        print(f"\n✓ Processing completed successfully!")
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")


def run_with_args():
    """
    Run with command line arguments if provided, otherwise interactive mode
    """
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
        output_file = get_output_filename(input_file)
        print(f"Processing: {input_file}")
        missing_periods = find_missing_periods(input_file, output_file)
        if not missing_periods.empty:
            print(f"\nMissing Periods:")
            print(missing_periods.to_string(index=False))
        else:
            print("No missing periods found!")
    else:
        # No arguments provided, run interactive mode
        main()

if __name__ == "__main__":
    run_with_args()