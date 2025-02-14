from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import requests
import numpy as np
from Bio.motifs import Motif
from Bio import motifs
from Bio import SeqIO
from io import StringIO

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

JASPAR_BASE_URL = "http://jaspar.genereg.net/api/v1"

@app.get("/api/search_tfs")
def search_tfs(query: str, page: int = 1, page_size: int = 10):
    url = f"{JASPAR_BASE_URL}/matrix/?search={query}&page_size={page_size}&page={page}"
    r = requests.get(url)
    if r.status_code != 200:
        return JSONResponse(status_code=500, content={"error": "JASPAR search failed"})
    
    data = r.json()
    results = data.get("results", [])
    simplified = [{
        "matrix_id": item.get("matrix_id"),
        "name": item.get("name"),
        "family": item.get("family"),
        "tax_group": item.get("tax_group"),
    } for item in results]

    return {
        "count": data.get("count", 0),
        "page": page,
        "page_size": page_size,
        "results": simplified
    }

@app.post("/api/scan")
def scan_sequence(payload: dict):
    raw_input = payload.get("sequence", "")
    tf_id = payload.get("tf_id", "")
    
    if not raw_input or not tf_id:
        return JSONResponse(
            status_code=400, 
            content={"error": "Missing sequence or tf_id."}
        )

    # Parse FASTA if it starts with '>'
    if raw_input.startswith('>'):
        fasta = StringIO(raw_input)
        try:
            sequence = str(next(SeqIO.parse(fasta, 'fasta')).seq)
        except:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid FASTA format"}
            )
    else:
        sequence = raw_input.strip()

    # Fetch PFM from JASPAR
    url = f"{JASPAR_BASE_URL}/matrix/{tf_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return JSONResponse(
            status_code=500, 
            content={"error": "Failed to retrieve TF from JASPAR"}
        )

    data = r.json()
    pfm = data.get("pfm", {}).get("pfm", None)
    if not pfm:
        return JSONResponse(
            status_code=400, 
            content={"error": "No PFM data found for TF"}
        )

    # Process PFM data
    pfm_array = np.array(pfm)
    pfm_array_T = pfm_array.T

    motif_counts = {
        "A": pfm_array_T[0].tolist(),
        "C": pfm_array_T[1].tolist(),
        "G": pfm_array_T[2].tolist(),
        "T": pfm_array_T[3].tolist(),
    }

    # Create and normalize motif
    motif_obj = motifs.Motif(alphabet="ACGT")
    motif_obj.counts = motif_counts
    pwm = motif_obj.counts.normalize(pseudocounts=0.8)

    # Scan sequence
    window_size = motif_obj.length
    scores = []
    
    def score_subseq(subseq):
        score = 0.0
        for i, base in enumerate(subseq):
            if base in pwm:
                p = pwm[base][i]
                score += np.log2(p if p > 0 else 1e-9)
            else:
                score += -9999
        return score

    for i in range(len(sequence) - window_size + 1):
        subseq = sequence[i : i + window_size]
        score = score_subseq(subseq)
        scores.append(score)

    if not scores:
        return {
            "scores": [],
            "positions": [],
            "topHits": []
        }

    # Calculate top hits
    max_score = max(scores)
    threshold = 0.8 * max_score
    top_hits = [
        {
            "start": i,
            "end": i + window_size,
            "score": sc
        }
        for i, sc in enumerate(scores)
        if sc >= threshold
    ]

    return {
        "scores": scores,
        "positions": list(range(len(scores))),
        "topHits": top_hits
    } 