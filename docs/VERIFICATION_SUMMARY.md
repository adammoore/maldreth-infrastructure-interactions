# MaLDReTH Definition Verification Summary

**Date**: 2025-10-02
**Verified By**: PRISM Development Team
**Sources**: RDA-OfR Mapping the Landscape of Digital Research Tools Working Group Deliverables (July 2024)

---

## Overview

All MaLDReTH terminology and lifecycle stage definitions have been verified against official RDA documents and updated throughout the PRISM application.

---

## Verified Definitions

### ✅ MaLDReTH Acronym
**Expansion**: **M**apping the **L**andscape of **D**igital **Re**search **T**ools **H**armonised

**Official Definition**: The harmonised Research Data Lifecycle (RDL) model created by the RDA-OfR Working Group to serve as the foundational framework for categorising and characterising various types of digital research tools.

**Source**: RDA Deliverable 1, Page 2
**Status**: VERIFIED ✓

---

### ✅ Research Data Lifecycle (RDL)
**Official Definition**: The complete journey of research data from initial concept through to reuse and transformation, represented in the MaLDReTH model as 12 distinct stages.

**12 Stages**: CONCEPTUALISE, PLAN, FUND, COLLECT, PROCESS, ANALYSE, STORE, PUBLISH, PRESERVE, SHARE, ACCESS, TRANSFORM

**Source**: RDA Deliverable 1, Pages 1-2, 8-9
**Status**: VERIFIED ✓

---

### ✅ All 12 Lifecycle Stage Definitions

| Stage | Verification Status | Source |
|-------|---------------------|--------|
| 1. CONCEPTUALISE | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 2. PLAN | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 3. FUND | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 4. COLLECT | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 5. PROCESS | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 6. ANALYSE | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 7. STORE | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 8. PUBLISH | ✓ VERIFIED | RDA Deliverable 1, Page 8 |
| 9. PRESERVE | ✓ VERIFIED | RDA Deliverable 1, Pages 8-9 |
| 10. SHARE | ✓ VERIFIED | RDA Deliverable 1, Pages 8-9 |
| 11. ACCESS | ✓ VERIFIED | RDA Deliverable 1, Page 9 |
| 12. TRANSFORM | ✓ VERIFIED | RDA Deliverable 1, Page 9 |

---

### ✅ Tool-Related Terminology

| Term | Verification Status | Source |
|------|---------------------|--------|
| Digital Research Tools | ✓ VERIFIED | RDA Deliverable 2, Page 1 |
| Tool Category | ✓ VERIFIED | RDA Deliverable 2, Page 3 |
| Exemplar Tool / Representative Example Tool | ✓ VERIFIED | RDA Deliverable 2, Page 3 |

---

### ✅ Other Key Terms

| Term | Verification Status | Source |
|------|---------------------|--------|
| PRISM | ✓ VERIFIED | PRISM Development Team |
| GORC (Global Open Research Commons) | ✓ VERIFIED | RDA Deliverable 2, Page 2 |

---

## Files Updated

### 1. `/docs/OFFICIAL_RDA_DEFINITIONS.md` (NEW)
- Comprehensive extraction of all official definitions
- Complete 12-stage lifecycle with full definitions
- Working group information
- Tool landscape statistics
- Document references

### 2. `/config/glossary_content.py`
- Updated MaLDReTH definition with official text
- Updated RDL definition with complete 12-stage information
- Added verification metadata (verified_by, verified_date, source_url)
- Changed verification_status from 'NEEDS_VERIFICATION' to 'VERIFIED'

### 3. `/streamlined_app.py`
- Updated all 12 LIFECYCLE_STAGE_DEFINITIONS with official RDA definitions
- Added 'source': 'RDA MaLDReTH Deliverable 1' to each stage
- Added 'verified': True flag to each stage
- Enhanced activities and outputs lists based on official definitions
- Added notes about iterative cycle (COLLECT > PROCESS > ANALYSE > STORE)
- Added note about FUND stage tool categorisation

### 4. `/docs/rda_sources/` (NEW DIRECTORY)
- Downloaded all 4 official RDA MaLDReTH deliverables:
  - D1_RDL_model.pdf (1.7MB)
  - D2_categorisation_schema.pdf (518KB)
  - D3_structural_framework.pdf (3.1MB)
  - Recommendation_Package.pdf (385KB)

---

## Key Findings from RDA Documents

### 1. MaLDReTH Model Creation
- **Methodology**: Semantic distance methodology over etymological/taxonomic net
- **Source Models**: Harmonised from 5 existing RDL models:
  1. DCC Data Curation Lifecycle
  2. RDMkit Data Life Cycle (ELIXIR)
  3. Best Practice Data Life Cycle (EMBL-ABR)
  4. Research Data Framework (NIST)
  5. The Research Data Lifecycle (UCL)

### 2. Tool Landscape Statistics
- **Total Tools Identified**: 244 representative tools (excluding FUND)
- **Stages with Most Tools**: COLLECT (48), STORE (47), PROCESS (38)
- **Stages with Fewest Tools**: ACCESS (4), TRANSFORM (7), ANALYSE (10)

### 3. Important Notes
- **Iterative Cycle**: "COLLECT > PROCESS > ANALYSE > STORE may be a repeating cycle"
- **FUND Stage**: Tools identified but omitted from categorisation schema as they "were not categorised as digital research tools"
- **GORC Connection**: Work contributes to Global Open Research Commons initiative

---

## Verification Checklist

### HIGH PRIORITY - Now Verified ✓
- [x] MaLDReTH acronym expansion
- [x] Research Data Lifecycle 12-stage model definition
- [x] All 12 lifecycle stage names verified
- [x] All 12 lifecycle stage descriptions verified and updated in code

### MEDIUM PRIORITY - Previously Verified ✓
- [x] Tool-related terminology (Exemplar Tool, Tool Category, Tool Interaction)
- [x] PRISM acronym and definition
- [x] GORC definition

### Interaction Type Definitions
- [ ] Not addressed in official RDA documents
- [ ] Current PRISM definitions remain as working definitions
- [ ] May require future verification if RDA publishes guidance

---

## Changes to User-Facing Content

### Glossary Page (`/glossary`)
- All lifecycle stage definitions now show official RDA text
- Source attribution added: "RDA MaLDReTH Deliverable 1"
- Verified flag added to indicate official definitions
- Additional context provided (e.g., iterative cycle notes)

### FAQ System
- Now dynamically loaded from `config/glossary_content.py`
- Can be updated without modifying templates
- Includes verification status tracking

### Data Entry Forms
- Lifecycle stage dropdown tooltips will show verified definitions
- Users will see authoritative RDA language throughout the application

---

## Next Steps

### Immediate
1. Test updated definitions in running application
2. Verify glossary page displays correctly
3. Check that all 12 stages show verified content

### Short-term
1. Consider adding "Source: RDA Deliverable 1" attribution in UI where definitions appear
2. Add FAQ entry explaining verification process
3. Update About page to mention verification against official RDA sources

### Future Considerations
1. Monitor RDA for updates to definitions (check annually)
2. Consider adding interaction type definitions if RDA publishes guidance
3. Explore adding tool categorisation schema from Deliverable 2
4. Consider implementing the structural framework from Deliverable 3

---

## Documentation References

### Official RDA Documents
- **D1**: https://www.rd-alliance.org/wp-content/uploads/2024/09/D1_The-creation-of-a-harmonised-research-data-lifecycle-RDL-model-and-crosswalk-to-existing-models-.pdf
- **D2**: https://www.rd-alliance.org/wp-content/uploads/2024/09/D2_The-identification-categorisation-and-mapping-of-different-types-of-research-tools_-A-categorisation-schema.pdf
- **D3**: https://www.rd-alliance.org/wp-content/uploads/2024/09/D3_The-creation-of-a-preliminary-structural-framework-for-an-online-open-access-%E2%80%98map-of-the-digital-research-tool-landscape.pdf
- **Recommendation Package**: https://www.rd-alliance.org/wp-content/uploads/2024/09/Recommendation-Package_Mapping_the_Landscape_WG.pdf

### Local Copies
- All documents downloaded to `/docs/rda_sources/`
- Detailed extraction in `/docs/OFFICIAL_RDA_DEFINITIONS.md`

### RDA Working Group Page
- https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii

---

## Acknowledgments

**RDA-OfR Mapping the Landscape of Digital Research Tools Working Group**

**Co-chairs**:
- Emmanuel Adamolekun (0000-0003-2992-5448)
- Francis P. Crawley (0000-0002-6893-5916)
- Rory Macneil (0000-0002-8429-096X)
- Adam Vials Moore (0000-0002-2085-1908) - *PRISM co-chair*
- Hea Lim Rhee (0000-0002-4171-5710)

**Assisting co-chairs**:
- Marcelo Garcia (0000-0002-2927-2371)
- Richard Pitts (0000-0002-2037-3360)

**Facilitator and Editor**: Connie Clare (0000-0002-4369-196X)

---

**Verification Completed**: 2025-10-02
**Document Version**: 1.0
**Maintainer**: PRISM Development Team
