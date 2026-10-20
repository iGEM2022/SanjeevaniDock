# Receptor structures

Apo (metal-free) AlphaFold monomer models used as receptors in SanjeevaniDock.
Files are the unmodified AlphaFold PDB downloads. Hydrogens, charges and atom
types are added later by `prepare_receptor4.py`.

| File | Protein | Organism | UniProt | Length (aa) | Cys | AlphaFold model date | Mean pLDDT (CA) |
|---|---|---|---|---|---|---|---|
| `AtMT1A.pdb` | MT1A | *A. thaliana* | P43392 | 45 | 13 | 2025-08-01 | 51.0 |
| `AtMT1B.pdb` | MT1B (putative) | *A. thaliana* | Q38803 | 45 | 10 | 2025-08-01 | 56.5 |
| `AtMT1C.pdb` | MT1C | *A. thaliana* | Q38804 | 45 | 13 | 2025-08-01 | 52.2 |
| `AtMT2A.pdb` | MT2A | *A. thaliana* | P25860 | 81 | 14 | 2025-08-01 | 63.8 |
| `AtMT2B.pdb` | MT2B | *A. thaliana* | Q38805 | 77 | 14 | 2025-08-01 | 59.9 |
| `AtMT3.pdb` | MT3 | *A. thaliana* | O22433 | 69 | 12 | 2025-08-01 | 55.9 |
| `ATMT4A.pdb` | MT4a, 120-aa isoform (see note 1) | *A. thaliana* | F4ILY7 | 120 | 18 | 2022-06-01 | 52.6 |
| `AtMT4b.pdb` | MT4b | *A. thaliana* | Q42377 (see note 2) | 85 | 17 | 2022-06-01 | 50.1 |
| `PpMT2.pdb` | MT type 2 | *P. patens* | A0A2K1KI10 | 59 | 14 | 2022-06-01 | 47.8 |

Each file's sequence was checked residue by residue against the UniProt
sequence for the accession shown (retrieved October 2026). The SEQRES records
match the ATOM records in every file, each file has a single chain (A) and a
single model, and the number of CYS SG atoms equals the number of Cys in the
sequence.

## Notes

1. **AtMT4a (`ATMT4A.pdb`)** is the unreviewed UniProt entry F4ILY7 (gene
   At2g42000), a 120-aa form. It is the reviewed MT4A entry
   [P93746](https://rest.uniprot.org/uniprotkb/P93746.fasta) (84 aa, 17 Cys)
   plus a 36-residue N-terminal extension
   (`MTLITDHVCSLSAGDRVDSLLDALSRLRGTLRLKTK`) that contains one additional Cys,
   giving 18 Cys. The residue numbering in results therefore differs from
   P93746 by 36.
2. **AtMT4b (`AtMT4b.pdb`)**: the AlphaFold header cites A0A178VZU5, which is
   now a deleted UniProt entry. The sequence is identical to the reviewed
   entry Q42377 (MT4B_ARATH, gene At2g23240), so Q42377 is given as the
   reference accession.
3. **AtMT1B** is annotated in UniProt as a putative protein (protein existence
   level 5, "uncertain") and is not used in the final comparison.
4. **PpMT2**: UniProt lists A0A2K1KI10 as "Uncharacterized protein"
   (unreviewed). The name "PpMT2" is the project's own label. The AlphaFold
   title is "Metallothionein type 2". Gene/locus ID: _TODO: add Phytozome /
   Phypa locus ID._

## Model confidence

All structures are low-to-moderate confidence AlphaFold predictions (mean
pLDDT 48-64; per-residue values are in the B-factor column). Metallothioneins
fold around their bound metals, so these apo models should be read as
approximate Cys-cluster geometries, not as experimentally resolved binding
sites.

## Attribution

Structures were predicted by AlphaFold (DeepMind / EMBL-EBI) and are
distributed under CC-BY 4.0:

- Jumper, J. et al. Highly accurate protein structure prediction with
  AlphaFold. *Nature* 596, 583-589 (2021). doi:10.1038/s41586-021-03819-2
- Varadi, M. et al. AlphaFold Protein Structure Database. *Nucleic Acids Res.*
  (2022). The AlphaFold DB entry for each protein is `AF-<UniProt>-F1`.
