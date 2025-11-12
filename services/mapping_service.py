"""
MOS (Military Occupational Specialty) mapping service.
Loads and searches MOS codes from Excel file, translates them to civilian skills.
"""

import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from functools import lru_cache

try:
    from utils.config import settings
    from utils.logging_utils import get_logger
    logger = get_logger(__name__)
except ImportError:
    settings = None
    logger = None
    
    class MockSettings:
        data_dir = Path(__file__).parent.parent / "data"
    
    if not settings:
        settings = MockSettings()


@dataclass
class MOSMapping:
    """Represents a single MOS mapping entry with enhanced fields."""
    
    code: str
    branch: str
    branch_code: str
    personnel_category: str
    title: str
    title_military: str
    soc_code: str
    soc_code_title: str
    soc_title: str
    onet_code: str
    onet_occupation: str
    csv_lookup_key: str
    civilian_equivalent: str = ""
    skills: List[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.keywords is None:
            self.keywords = []
    
    def matches_query(self, query: str) -> bool:
        """Check if this MOS matches a search query."""
        query_lower = query.lower()
        return (
            query_lower in self.code.lower() or
            query_lower in self.title.lower() or
            (self.title_military and query_lower in self.title_military.lower()) or
            (self.civilian_equivalent and query_lower in self.civilian_equivalent.lower()) or
            (self.soc_title and query_lower in self.soc_title.lower()) or
            (self.onet_occupation and query_lower in self.onet_occupation.lower()) or
            any(query_lower in skill.lower() for skill in self.skills) or
            any(query_lower in keyword.lower() for keyword in self.keywords)
        )


class MOSMappingService:
    """Service for loading and searching MOS mappings from Excel file."""
    
    def __init__(self, excel_path: Optional[Path] = None):
        """
        Initialize the MOS mapping service.
        
        Args:
            excel_path: Path to the MOS mapping Excel file
        """
        # Try Excel file first, then fall back to CSV
        if excel_path:
            self.data_path = excel_path
        else:
            excel_file = settings.data_dir / "MOS Mapping.xlsx"
            csv_file = settings.data_dir / "mos_mapping.csv"
            
            if excel_file.exists():
                self.data_path = excel_file
            elif csv_file.exists():
                self.data_path = csv_file
            else:
                self.data_path = excel_file  # Default to Excel
        
        self._mappings: Dict[str, MOSMapping] = {}
        self._load_mappings()
    
    def _load_mappings(self) -> None:
        """Load MOS mappings from Excel or CSV file."""
        if not self.data_path.exists():
            if logger:
                logger.warning(f"MOS mapping file not found: {self.data_path}")
            return
        
        try:
            # Load data based on file extension
            if self.data_path.suffix == '.xlsx':
                df = pd.read_excel(self.data_path, engine='openpyxl')
            else:
                df = pd.read_csv(self.data_path)
            
            # Clean column names - strip whitespace and handle case variations
            df.columns = df.columns.str.strip()
            
            # Expected columns from the Excel file
            required_cols = {
                'branch_code': ['branch_code', 'Branch Code'],
                'personnel_category': ['personnel_category', 'Personnel Category'],
                'code': ['code', 'Code', 'MOS_CODE'],
                'title_military': ['title_military', 'Title Military', 'title'],
                'soc_code': ['soc_code', 'SOC Code'],
                'soc_code_title': ['soc_code_title', 'SOC Code Title'],
                'soc_title': ['soc_title', 'SOC Title'],
                'onet_code': ['onet_code', 'O*NET Code', 'ONET Code'],
                'onet_occupation': ['onet_occupation', 'O*NET Occupation', 'ONET Occupation'],
                'csv_lookup_key': ['csv_lookup_key', 'CSV Lookup Key']
            }
            
            # Map column names (case-insensitive)
            col_mapping = {}
            df_cols_lower = {col.lower(): col for col in df.columns}
            
            for target_col, possible_names in required_cols.items():
                for name in possible_names:
                    if name.lower() in df_cols_lower:
                        col_mapping[df_cols_lower[name.lower()]] = target_col
                        break
            
            # Rename columns
            df = df.rename(columns=col_mapping)
            
            # Fill NaN values with empty strings
            df = df.fillna('')
            
            # Process each row
            for _, row in df.iterrows():
                code = str(row.get('code', '')).strip().upper()
                
                if not code:
                    continue
                
                # Extract branch from csv_lookup_key or branch_code
                lookup_key = str(row.get('csv_lookup_key', ''))
                branch_code = str(row.get('branch_code', ''))
                
                # Map branch codes to full names
                branch_map = {
                    'A': 'Army', 'Army': 'Army',
                    'N': 'Navy', 'Navy': 'Navy',
                    'AF': 'Air Force', 'Air Force': 'Air Force',
                    'M': 'Marines', 'Marines': 'Marines',
                    'CG': 'Coast Guard', 'Coast Guard': 'Coast Guard',
                    'SF': 'Space Force', 'Space Force': 'Space Force',
                    'V': 'Navy',  # V codes are typically Navy
                }
                
                # Determine branch
                if lookup_key and '|' in lookup_key:
                    branch_part = lookup_key.split('|')[0].strip()
                    branch = branch_map.get(branch_part, branch_part)
                elif branch_code:
                    branch = branch_map.get(branch_code, branch_code)
                else:
                    branch = 'Unknown'
                
                # Build civilian equivalent from SOC and O*NET titles
                soc_title = str(row.get('soc_title', '')).strip()
                onet_occupation = str(row.get('onet_occupation', '')).strip()
                civilian_equivalent = soc_title or onet_occupation or ''
                
                # Extract skills from SOC/O*NET titles (simplified)
                skills = []
                if soc_title:
                    # Parse skills from title (you can enhance this)
                    skills.extend([s.strip() for s in soc_title.split(',') if s.strip()])
                
                # Build keywords from various fields
                keywords = []
                title_military = str(row.get('title_military', '')).strip()
                if title_military:
                    keywords.extend([w.strip() for w in title_military.split() if len(w.strip()) > 3])
                
                mapping = MOSMapping(
                    code=code,
                    branch=branch,
                    branch_code=str(row.get('branch_code', '')).strip(),
                    personnel_category=str(row.get('personnel_category', '')).strip(),
                    title=title_military,  # Use military title as main title
                    title_military=title_military,
                    soc_code=str(row.get('soc_code', '')).strip(),
                    soc_code_title=str(row.get('soc_code_title', '')).strip(),
                    soc_title=soc_title,
                    onet_code=str(row.get('onet_code', '')).strip(),
                    onet_occupation=onet_occupation,
                    csv_lookup_key=lookup_key,
                    civilian_equivalent=civilian_equivalent,
                    skills=skills if skills else [],
                    keywords=keywords if keywords else []
                )
                
                # Store by code and by lookup key
                self._mappings[code] = mapping
                if lookup_key:
                    self._mappings[lookup_key] = mapping
            
            if logger:
                logger.info(f"Loaded {len(self._mappings)} MOS mappings from {self.data_path.name}")
        
        except Exception as e:
            if logger:
                logger.error(f"Error loading MOS mappings: {e}")
            raise
    
    def search_mos(self, query: str, limit: int = 10) -> List[MOSMapping]:
        """
        Search for MOS codes matching the query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
        
        Returns:
            List of matching MOS mappings
        """
        if not query or len(query) < 2:
            return []
        
        matches = [
            mapping for mapping in self._mappings.values()
            if mapping.matches_query(query)
        ]
        
        # Sort by relevance (exact code match first, then title match)
        query_upper = query.upper()
        matches.sort(key=lambda m: (
            0 if m.code == query_upper else 1,
            0 if query.lower() in m.title.lower() else 1,
            m.code
        ))
        
        return matches[:limit]
    
    def get_mos(self, code: str) -> Optional[MOSMapping]:
        """
        Get a specific MOS mapping by code.
        
        Args:
            code: MOS code to look up
        
        Returns:
            MOSMapping if found, None otherwise
        """
        return self._mappings.get(code.upper())
    
    def skills_for(self, code: str) -> List[str]:
        """
        Get civilian skills for a specific MOS code.
        
        Args:
            code: MOS code
        
        Returns:
            List of civilian skills
        """
        mapping = self.get_mos(code)
        return mapping.skills if mapping else []
    
    def get_all_codes(self) -> List[str]:
        """Get all available MOS codes."""
        return sorted(self._mappings.keys())
    
    def get_by_branch(self, branch: str) -> List[MOSMapping]:
        """
        Get all MOS mappings for a specific branch.
        
        Args:
            branch: Military branch (Army, Navy, Air Force, Marines, Coast Guard)
        
        Returns:
            List of MOS mappings for that branch
        """
        return [
            mapping for mapping in self._mappings.values()
            if mapping.branch.lower() == branch.lower()
        ]


# Global service instance
@lru_cache(maxsize=1)
def get_mos_service() -> MOSMappingService:
    """Get or create the global MOS mapping service instance."""
    return MOSMappingService()


# Simplified interface for Streamlit
class MappingService:
    """Simplified MOS mapping service for easy use."""
    
    def __init__(self):
        self._service = get_mos_service()
    
    def search_mos(self, query: str) -> List[Dict]:
        """Search for MOS and return as dictionaries with enhanced fields."""
        results = self._service.search_mos(query, limit=5)
        return [
            {
                'code': m.code,
                'branch': m.branch,
                'branch_code': m.branch_code,
                'personnel_category': m.personnel_category,
                'title': m.title,
                'title_military': m.title_military,
                'civilian_equivalent': m.civilian_equivalent,
                'civilian_skills': m.skills,
                'keywords': m.keywords,
                'soc_code': m.soc_code,
                'soc_title': m.soc_title,
                'onet_code': m.onet_code,
                'onet_occupation': m.onet_occupation,
                'csv_lookup_key': m.csv_lookup_key
            }
            for m in results
        ]
    
    def get_skills_for_mos(self, code: str) -> List[str]:
        """Get civilian skills for a MOS code."""
        return self._service.skills_for(code)

