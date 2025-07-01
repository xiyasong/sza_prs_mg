#!/bin/bash

# Exit immediately on error
set -e

# Inputs:
# 1. PLINK2 dataset prefix (from previous step)
# 2. Score file (tab-delimited, with 3 required columns: ID, ALT, EFFECT)
# 3. Output prefix

PGEN_PREFIX=$1      # e.g., data/1000g_pgen
SCORE_FILE=$2       # e.g., data/schizophrenia_scorefile.txt
OUT_PREFIX=$3       # e.g., results/1000g_prs_sza

if [ -z "$PGEN_PREFIX" ] || [ -z "$SCORE_FILE" ] || [ -z "$OUT_PREFIX" ]; then
  echo "Usage: bash run_prs.sh <plink2_pgen_prefix> <score_file> <out_prefix>"
  exit 1
fi

echo "Step: Calculating PRS with Plink2..."

plink2 \
  --pfile ${PGEN_PREFIX} \
  --score ${SCORE_FILE} 1 2 3 \
  --out ${OUT_PREFIX} \
  --read-freq ${PGEN_PREFIX}.afreq
echo "PRS calculation completed. Output written to ${OUT_PREFIX}.sscore"
