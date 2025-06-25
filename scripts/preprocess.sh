#!/bin/bash
# Exit immediately if a command fails
set -e

# Input VCF (bgzipped and indexed)
VCF_INPUT=$1     # Example: data/1000g_chr1_22.vcf.gz
OUT_PREFIX=$2    # Example: data/1000g_pgen

if [ -z "$VCF_INPUT" ] || [ -z "$OUT_PREFIX" ]; then
  echo "Usage: bash preprocess.sh <input.vcf.gz> <out_prefix>"
  exit 1
fi

# ------------------ Step 1: Remove 'chr' prefix in CHROM field ------------------
echo "Step 1: Removing 'chr' prefix from chromosome names..."
zcat $VCF_INPUT \
  | sed -E 's/^chr([0-9XY]+)\b/\1/' \
  | bgzip -c > ${OUT_PREFIX}.nochr.vcf.gz
tabix -p vcf ${OUT_PREFIX}.nochr.vcf.gz

# ------------------ Step 2: Keep only chromosomes 1-22 ------------------
echo "Step 2: Keeping only chromosomes 1-22..."
bcftools view -r $(seq -s, 1 22) -Oz -o ${OUT_PREFIX}.chr1_22.vcf.gz ${OUT_PREFIX}.nochr.vcf.gz
tabix -p vcf ${OUT_PREFIX}.chr1_22.vcf.gz

# ------------------ Step 3: Filter biallelic SNPs ------------------
echo "Step 3: Filtering biallelic SNPs..."
bcftools view -m2 -M2 -v snps -Oz -o ${OUT_PREFIX}.biallelic.vcf.gz ${OUT_PREFIX}.chr1_22.vcf.gz
tabix -p vcf ${OUT_PREFIX}.biallelic.vcf.gz

# ------------------ Step 4: Convert to PLINK2 ------------------
echo "Step 4: Converting to PLINK2 format and normalizing IDs..."
plink2 \
  --vcf ${OUT_PREFIX}.biallelic.vcf.gz \
  --make-pgen \
  --set-all-var-ids '@:#:$r' \
  --new-id-max-allele-len 1010 \
  --out ${OUT_PREFIX}

# ------------------ Step 5: Clean up intermediate files ------------------
echo "Step 5: Cleaning up intermediate files..."
#rm -v ${OUT_PREFIX}.nochr.vcf.gz ${OUT_PREFIX}.nochr.vcf.gz.tbi
#rm -v ${OUT_PREFIX}.chr1_22.vcf.gz ${OUT_PREFIX}.chr1_22.vcf.gz.tbi
#rm -v ${OUT_PREFIX}.biallelic.vcf.gz ${OUT_PREFIX}.biallelic.vcf.gz.tbi

# ------------------ Done ------------------
echo "Preprocessing completed."
echo "Final output:"
echo "- ${OUT_PREFIX}.pgen"
echo "- ${OUT_PREFIX}.pvar"
echo "- ${OUT_PREFIX}.psam"
# -----------Individual sample will raising lack of AF data error here
