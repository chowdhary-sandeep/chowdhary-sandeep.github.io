import os, json, sys
import numpy as np
import pandas as pd
from typing import List, Dict, Any

from sbert_local import setup_local_model
# Reuse server loaders for consistent normalization and staff support
try:
    import server as backend
except Exception as _e:
    backend = None

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(APP_ROOT, 'Early Career Scientists Expertise Sheet.xlsx')
STAFF_EXCEL_PATH = os.path.join(APP_ROOT, 'staff_expertise_clean.xlsx')
DATA_DIR = os.path.join(APP_ROOT, 'data')
CARD_VECS_PATH = os.path.join(DATA_DIR, 'card_vectors.npz')
TOKEN_VECS_PATH = os.path.join(DATA_DIR, 'token_vectors.npz')
COLUMN_MAP_JSON = os.path.join(DATA_DIR, 'column_map.json')

# Parent GitHub Pages repo path
PARENT_ROOT = os.path.abspath(os.path.join(APP_ROOT, '..'))
PARENT_DATA_DIR = os.path.join(PARENT_ROOT, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PARENT_DATA_DIR, exist_ok=True)

def _split_list_cell(v):
    if v is None or (isinstance(v, float) and np.isnan(v)): return []
    s = str(v).strip()
    if not s: return []
    for sep in ['\n','; ',',','|','•','·',' / ',' – ',' — ']:
        if sep in s:
            parts = [p.strip(' \t-•·') for p in s.split(sep)]
            return [p for p in parts if p]
    return [s]

def _infer_columns(cols: List[str]) -> Dict[str, str | None]:
    lc = {c.lower(): c for c in cols}
    def find(patterns: List[str]):
        for p in patterns:
            for lwr, orig in lc.items():
                if p in lwr: return orig
        return None
    # Load user overrides if available
    try:
        with open(COLUMN_MAP_JSON, 'r', encoding='utf-8') as f:
            over = json.load(f)
    except Exception:
        over = {}
    base = {
        'name': find(['name','full name','person']),
        'program': find(['program','programme']),
        'group': find(['group','unit','team','department']),
        'background': find(['background','bio','about','discipline','degree','education','field','training']),
        'topic': find(['topic','research topic','research focus','interests','expertise','keywords','domain','area']),
        'methods': find(['method','methods','technique','approach','methodology','methods used']),
        'software': find(['software','tool','tools','programming','languages']),
        'offer': find(['offer','can offer','can you offer','i can help','can help','can offer help','skills offered','expertise offered']),
        'seek': find(['seek','wants help','want help','need help','looking for','skills sought','mentorship needs'])
    }
    for k,v in over.items():
        if v in cols: base[k] = v
    return base

def _card_text(rec: Dict[str, Any]) -> str:
    parts = [rec.get('background',''), rec.get('topic','')] + rec.get('methods',[]) + rec.get('software',[]) + rec.get('offer',[]) + rec.get('seek',[])
    return ' | '.join([str(p) for p in parts if p]) or rec.get('name','')

def load_records() -> List[Dict[str, Any]]:
    if not os.path.exists(EXCEL_PATH):
        print('Excel not found at', EXCEL_PATH); sys.exit(1)
    try:
        sheets = pd.read_excel(EXCEL_PATH, engine='openpyxl', sheet_name=None)
    except Exception:
        sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)
    records: List[Dict[str, Any]] = []
    for _, df in sheets.items():
        if df is None or df.empty: continue
        df = df.fillna('')
        df.columns = [str(c).strip() for c in df.columns]
        cmap = _infer_columns(list(df.columns))
        for _, row in df.iterrows():
            name = str(row.get(cmap['name']) or '').strip()
            if not name: continue
            rec = {
                'name': name,
                'program': str(row.get(cmap['program']) or '').strip(),
                'group': str(row.get(cmap['group']) or '').strip(),
                'background': str(row.get(cmap['background']) or '').strip(),
                'topic': str(row.get(cmap['topic']) or '').strip(),
                'methods': _split_list_cell(row.get(cmap['methods'])) if cmap['methods'] else [],
                'software': _split_list_cell(row.get(cmap['software'])) if cmap['software'] else [],
                'offer': _split_list_cell(row.get(cmap['offer'])) if cmap['offer'] else [],
                'seek': _split_list_cell(row.get(cmap['seek'])) if cmap['seek'] else [],
            }
            records.append(rec)
    # dedupe by name
    merged = {}
    for r in records:
        nm = r['name']
        if nm not in merged: merged[nm] = r
        else:
            m = merged[nm]
            for k in ['program','group','background','topic']:
                if not m.get(k) and r.get(k): m[k] = r[k]
            for k in ['methods','software','offer','seek']:
                m[k] = sorted(list({*(m.get(k) or []), *(r.get(k) or [])}))
    return list(merged.values())

def save_json(path: str, obj: Any):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def main():
    model = setup_local_model('all-MiniLM-L6-v2')
    # Load ECR records (always)
    if backend and hasattr(backend, 'load_all_records'):
        recs = backend.load_all_records(include_staff=False)
    else:
        recs = load_records()

    # Always save records JSON for static site
    save_json(os.path.join(DATA_DIR, 'ecr_records.json'), recs)
    save_json(os.path.join(PARENT_DATA_DIR, 'ecr_records.json'), recs)

    # If model is available, compute and save embeddings
    if model is not None:
        names = [r['name'] for r in recs]
        texts = [_card_text(r) for r in recs]
        print(f'Encoding {len(texts)} cards…')
        card_vecs = model.encode(texts, show_progress_bar=True)
        np.savez_compressed(CARD_VECS_PATH, names=np.array(names, dtype=object), vectors=np.array(card_vecs, dtype=np.float32))
        save_json(os.path.join(DATA_DIR, 'card_vectors.json'), { n: [float(x) for x in v] for n, v in zip(names, card_vecs) })
        save_json(os.path.join(PARENT_DATA_DIR, 'card_vectors.json'), { n: [float(x) for x in v] for n, v in zip(names, card_vecs) })

        # Token vectors
        tokens = sorted(list({ t for r in recs for t in ([r.get('topic','')] + r.get('offer',[]) + r.get('seek',[]) + r.get('methods',[]) + r.get('software',[])) if isinstance(t,str) and t.strip() }))
        if tokens:
            print(f'Encoding {len(tokens)} tokens…')
            token_vecs = model.encode(tokens, show_progress_bar=False)
            np.savez_compressed(TOKEN_VECS_PATH, tokens=np.array(tokens, dtype=object), vectors=np.array(token_vecs, dtype=np.float32))
            save_json(os.path.join(DATA_DIR, 'token_vectors.json'), { t: [float(x) for x in v] for t, v in zip(tokens, token_vecs) })
            save_json(os.path.join(PARENT_DATA_DIR, 'token_vectors.json'), { t: [float(x) for x in v] for t, v in zip(tokens, token_vecs) })
    else:
        print('Warning: SBERT model not available. Skipping embeddings; static site will work without semantic sort.')

    # Staff dataset (optional)
    staff_recs: List[Dict[str, Any]] = []
    if os.path.exists(STAFF_EXCEL_PATH):
        print(f'Staff Excel file found at: {STAFF_EXCEL_PATH}')
        try:
            if backend and hasattr(backend, 'load_all_records'):
                print('Using backend.load_all_records for staff data')
                staff_recs = backend.load_all_records(include_staff=True)
            elif backend and hasattr(backend, 'load_staff_expertise_records'):
                print('Using backend.load_staff_expertise_records for staff data')
                staff_recs = backend.load_staff_expertise_records()
            else:
                print('Backend not available, trying direct Excel loading for staff')
                # Fallback: try to load staff data directly
                import pandas as pd
                df = pd.read_excel(STAFF_EXCEL_PATH, engine='openpyxl', sheet_name=0)
                print(f'Loaded staff Excel with {len(df)} rows')
                # Simple conversion to records format
                for _, row in df.iterrows():
                    person_name = str(row.get('PERSON_NAME', '')).strip()
                    expertise_name = str(row.get('EXPERTISE_NAME', '')).strip()
                    if person_name and expertise_name and person_name.lower() not in ['nan', 'none', ''] and expertise_name.lower() not in ['nan', 'none', '']:
                        # Find existing record or create new one
                        existing = next((r for r in staff_recs if r['name'] == person_name), None)
                        if existing:
                            if expertise_name not in existing['offer']:
                                existing['offer'].append(expertise_name)
                        else:
                            staff_recs.append({
                                'name': person_name,
                                'program': '',
                                'group': str(row.get('PERSON_MAIN_COST_CENTER', '')).strip(),
                                'background': '',
                                'topic': '',
                                'methods': [],
                                'software': [],
                                'offer': [expertise_name],
                                'seek': [],
                                'validated': False,
                                'tags': []
                            })
        except Exception as e:
            print('Warning: failed to load staff expertise records:', e)
            import traceback
            traceback.print_exc()
    if staff_recs:
        # Always save staff records
        save_json(os.path.join(DATA_DIR, 'staff_records.json'), staff_recs)
        save_json(os.path.join(PARENT_DATA_DIR, 'staff_records.json'), staff_recs)
        if model is not None:
            staff_names = [r['name'] for r in staff_recs]
            staff_texts = [_card_text(r) for r in staff_recs]
            print(f'Encoding {len(staff_texts)} staff cards…')
            staff_vecs = model.encode(staff_texts, show_progress_bar=True)
            save_json(os.path.join(DATA_DIR, 'staff_card_vectors.json'), { n: [float(x) for x in v] for n, v in zip(staff_names, staff_vecs) })
            save_json(os.path.join(PARENT_DATA_DIR, 'staff_card_vectors.json'), { n: [float(x) for x in v] for n, v in zip(staff_names, staff_vecs) })

    print('Done. Saved JSON artifacts to', DATA_DIR, 'and mirrored to', PARENT_DATA_DIR)

if __name__ == '__main__':
    main()


