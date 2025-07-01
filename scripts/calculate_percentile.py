#!/usr/bin/env python3

import pandas as pd
from scipy.stats import rankdata
import argparse
import sys

# ---------------------- Argument parser ---------------------- #
parser = argparse.ArgumentParser(description="Calculate PRS percentile and relative risk.")
parser.add_argument('--sscore', required=True, help='Path to .sscore file from Plink2')
parser.add_argument('--user_score', type=float, help='PRS score of the target individual')
parser.add_argument('--user_sscore_file', help='Optional: user PRS .sscore file instead of direct score')
parser.add_argument('--trait', default="Trait", help='Trait name for reporting (optional)')

args = parser.parse_args()

# ---------------------- Define automatic extract user sscore -------------- #
def read_user_score_from_sscore(user_sscore_path):
    df_user = pd.read_csv(user_sscore_path, delim_whitespace=True)
    score_col = "SCORE1_AVG" if "SCORE1_AVG" in df_user.columns else "SCORE"
    return df_user.iloc[0][score_col]

if args.user_score is not None:
    user_score = args.user_score
elif args.user_sscore_file:
    user_score = read_user_score_from_sscore(args.user_sscore_file)
else:
    raise ValueError("You must provide either --user_score or --user_sscore_file")

# ---------------------- Load PRS data ------------------------ #
# Read .sscore file
df = pd.read_csv(args.sscore, delim_whitespace=True)

# Strip possible whitespace from column names
df.columns = df.columns.str.strip()
# Fix column names that start with #
df.columns = df.columns.str.replace('^#', '', regex=True)

# Determine score column name (varies by Plink2 version)
score_col = "SCORE1_AVG" if "SCORE1_AVG" in df.columns else "SCORE"

# Ensure score column is float
df[score_col] = pd.to_numeric(df[score_col], errors="coerce")

# Debug: print
print(df.head())
print(df.dtypes)

# ---------------------- Statistics --------------------------- #
# Extract all 1000G scores
mean_score = df[score_col].mean()
double_mean = 2 * mean_score
relative_risk = user_score / mean_score
percent_of_double_mean = (user_score / double_mean) * 100

# Add user's score to cohort and calculate percentile
df_user = pd.DataFrame([["USER", user_score]], columns=["IID", score_col])
df_all = pd.concat([df[["IID", score_col]], df_user], ignore_index=True)

# Higher score = higher risk → rank in descending order
df_all["percentile"] = rankdata(-df_all[score_col], method="average") / len(df_all) * 100
user_percentile = df_all[df_all["IID"] == "USER"]["percentile"].values[0]

# ---------------------- Output ------------------------------- #
print(f"\n=== PRS Summary for {args.trait} ===")
print(f"1000G mean PRS:         {mean_score:.6f}")
print(f"User PRS:               {user_score:.6f}")
print(f"Relative Risk:          {relative_risk:.2f}x")
print(f"Score as % of 2x mean:  {percent_of_double_mean:.2f}%")
print(f"Percentile (1000G ref): {user_percentile:.2f}%")
# ---------------------- Output into TSV ---------------------- #

# Save to TSV file
with open("prs_summary.tsv", "w") as f:
    # Write header
    f.write("Trait\t1000G_mean_PRS\tUser_PRS\tRelative_Risk\tScore_%_of_2x_mean\tPercentile_1000G\n")
    # Write data
    f.write(
        f"{args.trait}\t"
        f"{mean_score:.6f}\t"
        f"{user_score:.6f}\t"
        f"{relative_risk:.2f}\t"
        f"{percent_of_double_mean:.2f}\t"
        f"{user_percentile:.2f}\n"
    )
