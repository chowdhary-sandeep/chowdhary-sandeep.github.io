import os, sys, json, threading
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Prefer user's local SBERT loader
try:
    from sbert_local import setup_local_model
except Exception:
    setup_local_model = None

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(APP_ROOT, 'Early Career Scientists Expertise Sheet.xlsx')
STAFF_EXCEL_PATH = os.path.join(APP_ROOT, 'staff_expertise_clean.xlsx')
DATA_DIR = os.path.join(APP_ROOT, 'data')
VALIDATED_JSON = os.path.join(DATA_DIR, 'validated.json')
OVERRIDES_JSON = os.path.join(DATA_DIR, 'overrides.json')
COLUMN_MAP_JSON = os.path.join(DATA_DIR, 'column_map.json')
os.makedirs(DATA_DIR, exist_ok=True)

def _load_json(path: str, default):
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except FileNotFoundError:
        with open(path, 'w', encoding='utf-8') as f: json.dump(default, f)
        return default
    except Exception:
        return default

def _save_json(path: str, obj: Any):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

validated_map: Dict[str, bool] = _load_json(VALIDATED_JSON, {})
overrides_map: Dict[str, Dict[str, Any]] = _load_json(OVERRIDES_JSON, {})
column_map_overrides: Dict[str, str] = _load_json(COLUMN_MAP_JSON, {})

# SBERT resources (lazy)
_model = None
_embed_lock = threading.Lock()
_card_text_cache: Dict[str, str] = {}
_card_vec_cache: Dict[str, np.ndarray] = {}

# Precomputed embeddings (loaded from disk if available)
CARD_VECS_PATH = os.path.join(DATA_DIR, 'card_vectors.npz')
TOKEN_VECS_PATH = os.path.join(DATA_DIR, 'token_vectors.npz')
_pre_card_names: List[str] | None = None
_pre_card_mat: np.ndarray | None = None
_name_to_idx: Dict[str, int] | None = None
_pre_token_strings: List[str] | None = None
_pre_token_mat: np.ndarray | None = None
_token_to_idx: Dict[str, int] | None = None

def get_model():
    global _model
    if _model is None:
        if setup_local_model is None: raise RuntimeError('SBERT loader not available')
        _model = setup_local_model('all-MiniLM-L6-v2')  # same as user's helper
        if _model is None: raise RuntimeError('SBERT model failed to load')
    return _model

def load_precomputed_embeddings() -> None:
    global _pre_card_names, _pre_card_mat, _name_to_idx, _pre_token_strings, _pre_token_mat, _token_to_idx
    try:
        if os.path.exists(CARD_VECS_PATH):
            npz = np.load(CARD_VECS_PATH, allow_pickle=True)
            _pre_card_names = [str(x) for x in npz['names'].tolist()]
            _pre_card_mat = np.array(npz['vectors']).astype(np.float32)
            _name_to_idx = {n: i for i,n in enumerate(_pre_card_names)}
        if os.path.exists(TOKEN_VECS_PATH):
            npz = np.load(TOKEN_VECS_PATH, allow_pickle=True)
            _pre_token_strings = [str(x) for x in npz['tokens'].tolist()]
            _pre_token_mat = np.array(npz['vectors']).astype(np.float32)
            _token_to_idx = {t.lower(): i for i,t in enumerate(_pre_token_strings)}
    except Exception as e:
        _pre_card_names = None; _pre_card_mat = None; _name_to_idx = None
        _pre_token_strings = None; _pre_token_mat = None; _token_to_idx = None
        print(f"Warning: failed to load precomputed embeddings: {e}")
    
# Load precomputed vectors once on import
load_precomputed_embeddings()

def _split_list_cell(v: Any) -> List[str]:
    if v is None or (isinstance(v, float) and np.isnan(v)): return []
    s = str(v).strip()
    if not s: return []
    # try multiple separators commonly used in spreadsheets
    seps = ['\n', ';', ',', '|', '•', '·', ' / ', ' – ', ' — ']
    for sep in seps:
        if sep in s:
            parts = [p.strip(' \t-•·') for p in s.split(sep)]
            parts = [p for p in parts if p]
            return parts
    return [s]

def _first_nonempty(row: pd.Series, keys: List[str]) -> Any:
    for k in keys:
        if k in row and pd.notna(row[k]) and str(row[k]).strip(): return row[k]
    return ''

def _infer_columns(cols: List[str]) -> Dict[str, str | None]:
    lc = {c.lower(): c for c in cols}
    def find(patterns: List[str]) -> str | None:
        for p in patterns:
            for lwr, orig in lc.items():
                if p in lwr: return orig
        return None
    base = {
        'name': find(['name','full name','person']),
        'program': find(['program','programme']),
        'group': find(['group','unit','team','department']),
        'background': find(['background','bio','about','discipline','degree','education','field','training']),
        'topic': find(['topic','research topic','research focus','interests','expertise','keywords','domain','area']),
        'methods': find(['method','methods','technique','approach','methodology','methods used']),
        'software': find(['software','tool','tools','programming','languages']),
        'offer': find(['offer','can offer','can you offer','i can help','can help','can offer help','skills offered','expertise offered']),

    }
    # Apply persistent overrides if provided
    for k,v in column_map_overrides.items():
        if v in cols: base[k] = v
    return base

def _normalize_record_with_map(row: pd.Series, cmap: Dict[str, str | None]) -> Dict[str, Any]:
    name = (row.get(cmap['name']) if cmap['name'] else _first_nonempty(row, ['name','Name']))
    program = row.get(cmap['program']) if cmap['program'] else _first_nonempty(row, ['program','Program'])
    group = row.get(cmap['group']) if cmap['group'] else _first_nonempty(row, ['group','Group'])
    background = row.get(cmap['background']) if cmap['background'] else _first_nonempty(row, ['background','Background'])
    topic = row.get(cmap['topic']) if cmap['topic'] else _first_nonempty(row, ['topic','Topics'])
    methods = _split_list_cell(row.get(cmap['methods'])) if cmap['methods'] else _split_list_cell(_first_nonempty(row, ['methods','Methods']))
    software = _split_list_cell(row.get(cmap['software'])) if cmap['software'] else _split_list_cell(_first_nonempty(row, ['software','Software','Tools']))
    offer = _split_list_cell(row.get(cmap['offer'])) if cmap['offer'] else _split_list_cell(_first_nonempty(row, ['offer','Offers','Can offer help','Can offer','Offer help']))
    seek = _split_list_cell(row.get(cmap['seek'])) if cmap['seek'] else _split_list_cell(_first_nonempty(row, ['seek','Seeks','Wants help','Need help']))
    rec = {
        'name': str(name).strip(), 'program': str(program or '').strip(), 'group': str(group or '').strip(),
        'background': str(background or '').strip(), 'topic': str(topic or '').strip(),
        'methods': methods, 'software': software, 'offer': offer, 'seek': seek
    }
    ov = overrides_map.get(rec['name'])
    if ov:
        for k,v in ov.items(): rec[k] = v
    rec['validated'] = bool(validated_map.get(rec['name'], False))
    return rec

def load_excel_records(excel_path: str, add_ecr_tag: bool = False) -> List[Dict[str, Any]]:
    if not os.path.exists(excel_path): raise FileNotFoundError('Excel file not found at ' + excel_path)
    # Read all sheets; some rows may be in different tabs
    try:
        sheets = pd.read_excel(excel_path, engine='openpyxl', sheet_name=None)
    except Exception:
        sheets = pd.read_excel(excel_path, sheet_name=None)  # fallback
    records: List[Dict[str, Any]] = []
    for sheet_name, df in sheets.items():
        if df is None or df.empty: continue
        df = df.fillna('')
        df.columns = [str(c).strip() for c in df.columns]
        cmap = _infer_columns(list(df.columns))
        for _,row in df.iterrows():
            rec = _normalize_record_with_map(row, cmap)
            if rec['name']: 
                if add_ecr_tag:
                    rec['tags'] = rec.get('tags', []) + ['ECR']
                records.append(rec)
    # Deduplicate by name, merge arrays
    merged: Dict[str, Dict[str, Any]] = {}
    for r in records:
        nm = r['name']
        if nm not in merged:
            merged[nm] = r
        else:
            m = merged[nm]
            for k in ['program','group','background','topic']:
                if not m.get(k) and r.get(k): m[k] = r[k]
                            for k in ['methods','software','offer']:
                m[k] = sorted(list({*(m.get(k) or []), *(r.get(k) or [])}))
            m['validated'] = m.get('validated', False) or r.get('validated', False)
            # Merge tags
            if 'tags' in r and 'tags' in m:
                m['tags'] = sorted(list(set(m['tags'] + r['tags'])))
            elif 'tags' in r:
                m['tags'] = r['tags']
    return list(merged.values())

def load_staff_expertise_records() -> List[Dict[str, Any]]:
    """Load staff expertise records with 1-1 mapping of expertise to person"""
    print(f"Loading staff expertise from: {STAFF_EXCEL_PATH}")
    if not os.path.exists(STAFF_EXCEL_PATH): 
        print("Staff file does not exist")
        return []
    
    try:
        # Try to read the first sheet only, as it likely contains all the data
        df = pd.read_excel(STAFF_EXCEL_PATH, engine='openpyxl', sheet_name=0)
        print(f"Loaded sheet with {len(df)} rows")
    except Exception as e:
        print(f"Error reading staff file: {e}")
        try:
            df = pd.read_excel(STAFF_EXCEL_PATH, sheet_name=0)
        except Exception as e2:
            print(f"Error with fallback reader: {e2}")
            return []
    
    if df is None or df.empty:
        print("Staff file is empty")
        return []
    
    df = df.fillna('')
    df.columns = [str(c).strip() for c in df.columns]
    print(f"Columns in staff file: {list(df.columns)}")
    
    # Look for specific columns - exact matching first, then flexible
    person_col = None
    expertise_col = None
    expertise_group_col = None
    
    for col in df.columns:
        col_lower = col.lower().strip()
        print(f"Checking column: '{col}' (lowercase: '{col_lower}')")
        
        # Exact match first for PERSON_NAME
        if col_lower == 'person_name':
            person_col = col
            print(f"Found person column (exact match): '{col}'")
        
        # Exact match first for EXPERTISE_NAME
        if col_lower == 'expertise_name':
            expertise_col = col
            print(f"Found expertise column (exact match): '{col}'")
            
        # Exact match first for EXPERTISE_GROUP
        if col_lower == 'expertise_group':
            expertise_group_col = col
            print(f"Found expertise group column (exact match): '{col}'")
    
    # If exact matches not found, try flexible matching
    if not person_col:
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'person' in col_lower and 'name' in col_lower:
                person_col = col
                print(f"Found person column (flexible match): '{col}'")
                break
    
    if not expertise_col:
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'expertise' in col_lower and 'name' in col_lower:
                expertise_col = col
                print(f"Found expertise column (flexible match): '{col}'")
                break
                
    if not expertise_group_col:
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'expertise' in col_lower and 'group' in col_lower:
                expertise_group_col = col
                print(f"Found expertise group column (flexible match): '{col}'")
                break
    
    if not person_col or not expertise_col:
        print(f"ERROR: Could not find required columns!")
        print(f"Looking for columns containing 'person' and 'expertise'")
        print(f"Available columns: {list(df.columns)}")
        return []
    
    print(f"Using columns: person='{person_col}', expertise='{expertise_col}', group='{expertise_group_col}'")
    
    # Process each row as a person-skill pair with expertise grouping
    person_skills: Dict[str, Dict[str, List[str]]] = {}  # person -> {group -> [skills]}
    valid_rows = 0
    
    for idx, row in df.iterrows():
        person_name = str(row[person_col]).strip()
        expertise_name = str(row[expertise_col]).strip()
        expertise_group = str(row[expertise_group_col]).strip() if expertise_group_col else 'General'
        cost_center = str(row.get('PERSON_MAIN_COST_CENTER', '')).strip() if 'PERSON_MAIN_COST_CENTER' in df.columns else ''
        
        # Skip empty or invalid rows
        if (not person_name or not expertise_name or 
            person_name.lower() in ['nan', 'none', ''] or 
            expertise_name.lower() in ['nan', 'none', '']):
            continue
            
        # Clean up group name
        if not expertise_group or expertise_group.lower() in ['nan', 'none', '']:
            expertise_group = 'General'
        
        # Add expertise to person's skill list grouped by expertise group
        if person_name not in person_skills:
            person_skills[person_name] = {}
        
        if expertise_group not in person_skills[person_name]:
            person_skills[person_name][expertise_group] = []
        
        if expertise_name not in person_skills[person_name][expertise_group]:
            person_skills[person_name][expertise_group].append(expertise_name)
        
        valid_rows += 1
    
    print(f"Processed {valid_rows} valid person-skill pairs")
    print(f"Found {len(person_skills)} unique people")
    
    # Convert to records format with grouped skills
    records = []
    for person_name, skill_groups in person_skills.items():
        # Flatten all skills for the main offer list
        all_skills = []
        for group_skills in skill_groups.values():
            all_skills.extend(group_skills)
        
        # Get the cost center for this person (use first occurrence)
        person_cost_center = ''
        for idx, row in df.iterrows():
            if str(row[person_col]).strip() == person_name:
                cost_center = str(row.get('PERSON_MAIN_COST_CENTER', '')).strip()
                if cost_center and cost_center.lower() not in ['nan', 'none', '']:
                    person_cost_center = cost_center
                    break
        
        records.append({
            'name': person_name,
            'program': '',
            'group': person_cost_center,  # Use cost center as group field
            'background': '',
            'topic': '',
            'methods': [],
            'software': [],
            'offer': sorted(all_skills),  # All their expertise as offer skills

            'validated': False,
            'tags': [],  # No ECR tag for staff
            'expertise_groups': skill_groups  # Store grouped skills for network visualization
        })
    
    print(f"Created {len(records)} staff records")
    return records

# Global cache for both datasets
_ecr_records_cache = None
_staff_records_cache = None

def load_all_records(include_staff: bool = False) -> List[Dict[str, Any]]:
    """Load ECR records or staff records from cache (preloaded at startup)"""
    global _ecr_records_cache, _staff_records_cache
    
    if include_staff:
        if _staff_records_cache is None:
            print("Loading staff records into cache...")
            _staff_records_cache = load_staff_expertise_records()
            print(f"Cached {len(_staff_records_cache)} staff records")
        return _staff_records_cache
    else:
        if _ecr_records_cache is None:
            print("Loading ECR records into cache...")
            _ecr_records_cache = load_excel_records(EXCEL_PATH, add_ecr_tag=True)
            print(f"Cached {len(_ecr_records_cache)} ECR records")
        return _ecr_records_cache

def _card_text(rec: Dict[str, Any]) -> str:
    # Aggregate meaningful fields for embedding
    parts = [rec.get('background',''), rec.get('topic','')] + rec.get('methods',[]) + rec.get('software',[]) + rec.get('offer',[])
    text = ' | '.join([str(p) for p in parts if p])
    return text or rec.get('name','')

def _ensure_embedding_for(records: List[Dict[str, Any]]):
    model = get_model()
    to_compute = []
    for rec in records:
        nm = rec['name']
        if nm not in _card_text_cache: _card_text_cache[nm] = _card_text(rec)
        if nm not in _card_vec_cache: to_compute.append(nm)
    if not to_compute: return
    texts = [_card_text_cache[nm] for nm in to_compute]
    with _embed_lock:
        vecs = model.encode(texts, show_progress_bar=False)
    for nm,vec in zip(to_compute, vecs): _card_vec_cache[nm] = np.asarray(vec, dtype=np.float32)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None: return 0.0
    an = np.linalg.norm(a); bn = np.linalg.norm(b)
    if an == 0 or bn == 0: return 0.0
    return float(np.dot(a,b) / (an*bn))

class ValidateBody(BaseModel):
    name: str
    validated: bool

class UpdateBody(BaseModel):
    name: str
    program: str | None = None
    group: str | None = None
    background: str | None = None
    topic: str | None = None
    methods: List[str] | None = None
    software: List[str] | None = None
    offer: List[str] | None = None
    seek: List[str] | None = None

class SimilarityBody(BaseModel):
    text: str
    top_k: int = 100

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=False, allow_methods=['*'], allow_headers=['*'])

@app.get('/api/data')
def api_data(include_staff: bool = False):
    print(f"API call: include_staff={include_staff}")
    records = load_all_records(include_staff=include_staff)
    print(f"Loaded {len(records)} records")
    # minimal placeholder substitution for missing attrs (frontend also handles '??')
    for r in records:
        for k in ['program','group','background','topic']:
            if not r.get(k): r[k] = ''
                        for k in ['methods','software','offer']:
            if not r.get(k): r[k] = []
        if not r.get('tags'): r['tags'] = []
    return {'records': records}

@app.get('/')
def api_root():
    return {'ok': True, 'message': 'ECR backend running', 'endpoints': ['/api/data','/api/validate','/api/update','/api/similarity']}

@app.get('/api/columns')
def api_columns():
    if not os.path.exists(EXCEL_PATH): raise HTTPException(404, 'Excel not found')
    try:
        sheets = pd.read_excel(EXCEL_PATH, engine='openpyxl', sheet_name=None, nrows=0)
    except Exception:
        sheets = pd.read_excel(EXCEL_PATH, sheet_name=None, nrows=0)
    out = { name: [str(c).strip() for c in (df.columns if df is not None else [])] for name,df in sheets.items() }
    return {'sheets': out, 'column_map_overrides': column_map_overrides}

class ColumnMapBody(BaseModel):
    name: str | None = None
    program: str | None = None
    group: str | None = None
    background: str | None = None
    topic: str | None = None
    methods: str | None = None
    software: str | None = None
    offer: str | None = None
    seek: str | None = None

@app.post('/api/column-map')
def api_set_column_map(body: ColumnMapBody):
    data = {k:v for k,v in body.dict().items() if v}
    if not data: return {'ok': True}
    column_map_overrides.update(data)
    _save_json(COLUMN_MAP_JSON, column_map_overrides)
    return {'ok': True, 'column_map_overrides': column_map_overrides}

@app.post('/api/validate')
def api_validate(body: ValidateBody):
    validated_map[body.name] = bool(body.validated)
    _save_json(VALIDATED_JSON, validated_map)
    return {'ok': True}

@app.post('/api/update')
def api_update(body: UpdateBody):
    nm = body.name
    if not nm: raise HTTPException(400, 'name required')
    ov = overrides_map.get(nm, {})
    for k,v in body.dict().items():
        if k == 'name' or v is None: continue
        ov[k] = v
    overrides_map[nm] = ov
    _save_json(OVERRIDES_JSON, overrides_map)
    # Invalidate caches for this card
    if nm in _card_text_cache: del _card_text_cache[nm]
    if nm in _card_vec_cache: del _card_vec_cache[nm]
    return {'ok': True}

@app.post('/api/similarity')
def api_similarity(body: SimilarityBody, include_staff: bool = False):
    seed = (body.text or '').strip()
    if not seed: return {'scores': []}
    records = load_all_records(include_staff=include_staff)
    # Try precomputed token vector first
    load_precomputed_embeddings()
    seed_vec = None
    if _token_to_idx and _pre_token_mat is not None:
        idx = _token_to_idx.get(seed.lower())
        if idx is not None:
            seed_vec = _pre_token_mat[idx]
    if seed_vec is None:
        # Try computing on the fly if model available
        try:
            model = get_model()
            with _embed_lock:
                seed_vec = model.encode([seed], show_progress_bar=False)[0]
            seed_vec = np.asarray(seed_vec, dtype=np.float32)
        except Exception:
            # Fallback: simple token-match scoring
            seed_l = seed.lower()
            scores = []
            for r in records:
                text = _card_text(r).lower()
                hit = seed_l in text
                scores.append({'name': r['name'], 'score': 1.0 if hit else 0.0})
            scores.sort(key=lambda x: (-x['score'], x['name']))
            return {'scores': scores[:max(1, body.top_k)]}

    # Card vectors from precompute if available
    name_to_vec: Dict[str, np.ndarray] = {}
    if _name_to_idx and _pre_card_mat is not None and _pre_card_names is not None:
        for r in records:
            nm = r['name']
            idx = _name_to_idx.get(nm)
            if idx is not None:
                name_to_vec[nm] = _pre_card_mat[idx]
    # If some missing and model is available, compute missing
    missing = [r for r in records if r['name'] not in name_to_vec]
    if missing:
        try:
            _ensure_embedding_for(missing)
            for r in missing:
                name_to_vec[r['name']] = _card_vec_cache.get(r['name'])
        except Exception:
            pass

    scores = []
    for r in records:
        nm = r['name']
        vec = name_to_vec.get(nm)
        s = cosine_sim(seed_vec, vec) if isinstance(vec, np.ndarray) else 0.0
        scores.append({'name': nm, 'score': s})
    scores.sort(key=lambda x: x['score'], reverse=True)
    return {'scores': scores[:max(1, body.top_k)]}

if __name__ == '__main__':
    # Try to precompute embeddings if SBERT is available
    try:
        # Precompute for both datasets separately (this will populate the cache)
        print("Preloading ECR records...")
        ecr_recs = load_all_records(include_staff=False)
        print("Preloading staff records...")
        staff_recs = load_all_records(include_staff=True)
        print(f"ECR records for precomputation: {len(ecr_recs)}")
        print(f"Staff records for precomputation: {len(staff_recs)}")
        
        # Build per-card text list for ECR
        ecr_names = [r['name'] for r in ecr_recs]
        ecr_texts = [_card_text(r) for r in ecr_recs]
        
        # Build per-card text list for staff
        staff_names = [r['name'] for r in staff_recs]
        staff_texts = [_card_text(r) for r in staff_recs]
        # Save names now even if vectors fail
        os.makedirs(DATA_DIR, exist_ok=True)
        # Compute with model if available
        if setup_local_model is not None:
            m = setup_local_model('all-MiniLM-L6-v2')
            if m is not None:
                print("Computing ECR embeddings...")
                ecr_vecs = m.encode(ecr_texts, show_progress_bar=True)
                np.savez_compressed(CARD_VECS_PATH, names=np.array(ecr_names, dtype=object), vectors=np.array(ecr_vecs, dtype=np.float32))
                
                print("Computing staff embeddings...")
                staff_vecs = m.encode(staff_texts, show_progress_bar=True)
                np.savez_compressed(os.path.join(DATA_DIR, 'staff_card_vectors.npz'), names=np.array(staff_names, dtype=object), vectors=np.array(staff_vecs, dtype=np.float32))
                
                # Also precompute frequent tokens from both datasets
                all_recs = ecr_recs + staff_recs
                tokens = sorted(list({ t for r in all_recs for t in ([r.get('topic','')] + r.get('offer',[]) + r.get('methods',[]) + r.get('software',[])) if isinstance(t,str) and t.strip() }))
                if tokens:
                    print(f"Computing token embeddings for {len(tokens)} tokens...")
                    tvecs = m.encode(tokens, show_progress_bar=False)
                    np.savez_compressed(TOKEN_VECS_PATH, tokens=np.array(tokens, dtype=object), vectors=np.array(tvecs, dtype=np.float32))
                print('Precomputation complete.')
    except Exception as e:
        print(f'Precompute skipped: {e}')

    # Dev server
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)


