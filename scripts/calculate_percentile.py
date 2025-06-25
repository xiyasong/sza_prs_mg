#!/usr/bin/env python3

import pandas as pd
from scipy.stats import rankdata
import argparse

# ---------------------- Argument parser ---------------------- #
parser = argparse.ArgumentParser(description="Calculate PRS percentile and relative risk.")
parser.add_argument('--sscore', required=True, help='Path to .sscore file from Plink2')
parser.add_argument('--user_score', type=float, required=True, help='PRS score of the target individual')
parser.add_argument('--trait', default="Trait", help='Trait name for reporting (optional)')
args = parser.parse_args()

# ---------------------- Load PRS data ------------------------ #
# Read .sscore file
df = pd.read_csv(args.sscore, delim_whitespace=True)

# Determine score column name (varies by Plink2 version)
score_col = "SCORE1_AVG" if "SCORE1_AVG" in df.columns else "SCORE"

# ---------------------- Statistics --------------------------- #
# Extract all 1000G scores
mean_score = df[score_col].mean()
double_mean = 2 * mean_score
relative_risk = args.user_score / mean_score
percent_of_double_mean = (args.user_score / double_mean) * 100

# Add user's score to cohort and calculate percentile
df_user = pd.DataFrame([["USER", args.user_score]], columns=["IID", score_col])
df_all = pd.concat([df[["IID", score_col]], df_user], ignore_index=True)

# Higher score = higher risk → rank in descending order
df_all["percentile"] = rankdata(-df_all[score_col], method="average") / len(df_all) * 100
user_percentile = df_all[df_all["IID"] == "USER"]["percentile"].values[0]

# ---------------------- Output ------------------------------- #
print(f"\n=== PRS Summary for {args.trait} ===")
print(f"1000G mean PRS:         {mean_score:.6f}")
print(f"User PRS:               {args.user_score:.6f}")
print(f"Relative Risk:          {relative_risk:.2f}x")
print(f"Score as % of 2x mean:  {percent_of_double_mean:.2f}%")
print(f"Percentile (1000G ref): {user_percentile:.2f}%")
# ---------------------- Output into tsv ---------------------- #

# Save to TSV file
with open("prs_summary.tsv", "w") as f:
    # Write header
    f.write("Trait\t1000G_mean_PRS\tUser_PRS\tRelative_Risk\tScore_%_of_2x_mean\tPercentile_1000G\n"
    # Write data
    f.write(f"{args.trait}\t"
            f"{mean_score:.6f}\t"
            f"{args.user_score:.6f}\t"
            f"{relative_risk:.2f}\t"
            f"{percent_of_double_mean:.2f}\t"
            f"{user_percentile:.2f}\n")

