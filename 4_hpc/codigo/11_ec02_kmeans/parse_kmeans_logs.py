import os
import re

import polars as pl


def parse_log_files():
    """
    Parses all .out files in the 'logs' subdirectory to extract and store
    K-means performance metrics in a Polars DataFrame.
    """
    log_directory = "11_ec02_kmeans/logs"
    results_list = []

    # Regex patterns to find the required data
    patterns = {
        "N": re.compile(r"Total points: (\d+),"),
        "MPI_size": re.compile(r"MPI size: (\d+)"),
        "Tcomp": re.compile(r"K-means Tcomp ([\d.]+) seconds\."),
        "Tcomm": re.compile(r"K-means Tcomm ([\d.]+) seconds\."),
    }

    if not os.path.isdir(log_directory):
        print(f"Error: Directory not found at '{log_directory}'")
        return

    # Iterate over each file in the log directory
    for filename in sorted(os.listdir(log_directory)):
        if filename.endswith(".out"):
            filepath = os.path.join(log_directory, filename)
            with open(filepath, "r") as f:
                content = f.read()

                # Search for all patterns in the file content
                n_match = patterns["N"].search(content)
                mpi_size_match = patterns["MPI_size"].search(content)
                tcomp_match = patterns["Tcomp"].search(content)
                tcomm_match = patterns["Tcomm"].search(content)

                # Extract data, using None as a default if not found
                n = int(n_match.group(1)) if n_match else None
                mpi_size = int(mpi_size_match.group(1)) if mpi_size_match else None
                tcomp = float(tcomp_match.group(1)) if tcomp_match else None
                tcomm = float(tcomm_match.group(1)) if tcomm_match else None

                # Only add rows where all data was found
                if all(val is not None for val in [n, mpi_size, tcomp, tcomm]):
                    results_list.append(
                        {
                            "Filename": filename,
                            "N": n,
                            "MPI Size": mpi_size,
                            "Tcomp (s)": tcomp,
                            "Tcomm (s)": tcomm,
                        }
                    )

    # Create and print the Polars DataFrame
    if results_list:
        # Create a Polars DataFrame from the list of dictionaries
        df = pl.DataFrame(results_list)

        # Sort the DataFrame by MPI Size, then by N
        df = df.sort(["MPI Size", "N"])

        print("Successfully parsed log files into a Polars DataFrame:")
        print(df)
    else:
        print("No data could be extracted. Please check the log files and patterns.")


if __name__ == "__main__":
    # Check for polars library and provide installation instructions if missing
    parse_log_files()
