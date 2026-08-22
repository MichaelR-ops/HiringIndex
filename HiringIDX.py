"""
HiringIndex - Calculate hiring index from company career pages.

This module loads company information, fetches their career pages,
extracts open job counts, and calculates hiring indices.
"""

from src.io_handler import save_hiring_index
from src.pipeline import process_companies


def main() -> None:
    """
    Main entry point for hiring index calculation.
    
    Loads companies from JSON, processes them, and saves results.
    """
    print("=" * 60)
    print("HiringIndex - Job Listing Analyzer")
    print("=" * 60)
    
    # Process companies and extract job counts
    print("\nProcessing companies...")
    result_df = process_companies("config/companies.json")
    
    # Save results
    print("\nSaving results...")
    save_hiring_index(result_df, "hiring_index.xlsx", format="xlsx")
    print("Results saved to hiring_index.xlsx")
    
    # Display summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(result_df.to_string(index=False))
    
    # Statistics
    successful = result_df[result_df["job_count"].notna()].shape[0]
    print(f"\nSuccessfully processed: {successful}/{len(result_df)} companies")


if __name__ == "__main__":
    main()