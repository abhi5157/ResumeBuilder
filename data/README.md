# MOS Mapping Data Dictionary

This document describes the structure of the `mos_mapping.csv` file.

## File Format

CSV (Comma-Separated Values) with the following columns:

## Column Descriptions

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `MOS_CODE` | String | Yes | Military Occupational Specialty code (e.g., "11B", "25B") |
| `BRANCH` | String | Yes | Military branch (Army, Navy, Air Force, Marines, Coast Guard) |
| `TITLE` | String | Yes | Official MOS title |
| `CIVILIAN_EQUIVALENT` | String | Yes | Equivalent civilian job title(s), separated by " \| " |
| `SKILLS` | String | Yes | Comma-separated list of transferable civilian skills |
| `KEYWORDS` | String | Yes | Comma-separated searchable keywords |

## Example Entry

```csv
25B,Army,Information Technology Specialist,IT Support Specialist | Systems Administrator,"Network administration,Troubleshooting,Hardware repair,Software installation,Cybersecurity basics","IT,technology,computers,networks,support"
```

## Adding New Entries

When adding new MOS codes:

1. Research the official MOS description from military sources
2. Identify 3-5 relevant civilian job titles
3. List 4-8 specific, actionable skills
4. Include 4-6 searchable keywords
5. Ensure no commas within individual skill names (use spaces instead)
6. Use proper capitalization

## Data Sources

- Official military MOS databases
- O*NET civilian occupation descriptions
- Industry job postings
- Military-to-civilian transition guides

## Quality Standards

- **Accuracy**: All MOS codes must be official and current
- **Relevance**: Civilian equivalents should be realistic career paths
- **Specificity**: Skills should be concrete and demonstrable
- **Searchability**: Keywords should cover common search terms

## Current Coverage

- Army: 12 MOS codes
- Navy: 10 ratings
- Air Force: 10 AFSCs
- Marines: 6 MOS codes
- Coast Guard: 10 ratings

**Total**: 50+ military occupational specialties

## Future Expansion

Priority areas for expansion:
- Special operations roles
- Technical/cyber specialties
- Medical specialties
- Aviation roles
- Engineering roles
