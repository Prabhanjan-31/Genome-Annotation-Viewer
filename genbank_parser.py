from Bio import SeqIO
import pandas as pd

def parse_genbank(file_handle):
    """
    Parse a GenBank (.gb/.gbff) file.
    Returns: (DataFrame, genome_length)
    """

    try:
        records = list(SeqIO.parse(file_handle, "genbank"))
    except Exception as e:
        raise RuntimeError(f"Error reading GenBank file: {e}")

    if not records:
        raise ValueError("No GenBank records found in this file.")

    record = records[0]
    genome_length = len(record.seq)
    features = []

    for feature in record.features:

        if feature.type not in ["gene", "CDS", "tRNA", "rRNA"]:
            continue

        # Start/end
        try:
            start = int(feature.location.start)
            end = int(feature.location.end)
        except:
            continue

        # Strand (safe)
        strand_val = feature.location.strand
        if strand_val == 1:
            strand = "+"
        elif strand_val == -1:
            strand = "-"
        else:
            strand = "."  # unknown or not applicable

        # Qualifiers
        qualifiers = feature.qualifiers
        gene = qualifiers.get("gene", [""])[0]
        if not gene:
            gene = qualifiers.get("locus_tag", [""])[0]

        product = qualifiers.get("product", [""])[0]

        features.append({
            "Type": feature.type,
            "Gene": gene,
            "Product": product,
            "Start": start,
            "End": end,
            "Strand": strand,
            "Length": end - start
        })

    df = pd.DataFrame(features).sort_values("Start").reset_index(drop=True)
    return df, genome_length
