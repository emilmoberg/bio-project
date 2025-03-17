# main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import requests
import numpy as np
from Bio import motifs
from Bio.motifs.matrix import FrequencyPositionMatrix
from Bio.Seq import Seq
from Bio import SeqIO
from io import StringIO

app = FastAPI()

# Update this list for your actual frontend origins
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

JASPAR_BASE_URL = "http://jaspar.genereg.net/api/v1"


@app.get("/api/search_tfs")
def search_tfs(query: str, page: int = 1, page_size: int = 10):
    """
    Search for transcription factors in JASPAR database.
    Returns paginated results with matrix info and logos.
    Handles both matrix ID searches (e.g. MA0079.1) and name searches.
    """
    # Check if query matches matrix ID format (e.g. MA0079.1)
    is_matrix_id = bool(query.strip().upper().startswith('MA') and '.' in query)
    
    # Construct search URL based on query type
    if is_matrix_id:
        # For matrix IDs, use exact match endpoint
        url = f"{JASPAR_BASE_URL}/matrix/{query.strip()}"
        r = requests.get(url)
        if r.status_code == 200:
            # If found, return as single result
            item = r.json()
            return {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{
                    "matrix_id": item.get("matrix_id"),
                    "name": item.get("name"),
                    "version": item.get("version"),
                    "collection": item.get("collection"),
                    "sequence_logo": item.get("sequence_logo"),
                    "url": item.get("url")
                }]
            }
        elif r.status_code == 404:
            # If not found, try regular search as fallback
            url = f"{JASPAR_BASE_URL}/matrix/?search={query}&page_size={page_size}&page={page}"
    else:
        # For name searches, use regular search endpoint
        url = f"{JASPAR_BASE_URL}/matrix/?search={query}&page_size={page_size}&page={page}"
    
    r = requests.get(url)
    if r.status_code != 200:
        return JSONResponse(
            status_code=500, 
            content={"error": "JASPAR search failed"}
        )

    data = r.json()
    results = data.get("results", [])
    
    simplified = []
    for item in results:
        simplified.append({
            "matrix_id": item.get("matrix_id"),
            "name": item.get("name"),
            "version": item.get("version"),
            "collection": item.get("collection"),
            "sequence_logo": item.get("sequence_logo"),
            "url": item.get("url")
        })

    return {
        "count": data.get("count", 0),
        "next": data.get("next"),
        "previous": data.get("previous"),
        "results": simplified
    }


@app.post("/api/scan")
def scan_sequence(payload: dict):
    """
    Expects JSON:
    {
      "sequence": "ACGTACGTACGT...",
      "tf_id": "MA0002.1"
    }

    Example data from JASPAR for MA0002.1 (RUNX1) now looks like:
    {
      'matrix_id': 'MA0002.1',
      'name': 'RUNX1',
      ...
      'pfm': {
         'A': [10.0, 12.0, 4.0, ...],
         'C': [...],
         'G': [...],
         'T': [...]
       }
    }

    We'll parse that properly and scan the user-supplied sequence.
    """
    raw_input = payload.get("sequence", "")
    tf_id = payload.get("tf_id", "")
    
    if not raw_input or not tf_id:
        return JSONResponse(
            status_code=400, 
            content={"error": "Missing sequence or tf_id."}
        )

    # Parse FASTA if it starts with '>'
    sequence_name = None
    if raw_input.startswith('>'):
        try:
            fasta = StringIO(raw_input)
            record = next(SeqIO.parse(fasta, 'fasta'))
            sequence = str(record.seq)
            sequence_name = record.id or record.description
        except StopIteration:
            return JSONResponse(
                status_code=400,
                content={"error": "Empty FASTA sequence"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid FASTA format: {str(e)}"}
            )
    else:
        sequence = raw_input.strip()

    # Validate sequence
    sequence = sequence.upper()
    if not sequence:
        return JSONResponse(
            status_code=400,
            content={"error": "Empty sequence"}
        )
    
    if not all(c in 'ACGT' for c in sequence):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid sequence. Only ACGT allowed."}
        )

    # Fetch the TF info from JASPAR
    url = f"{JASPAR_BASE_URL}/matrix/{tf_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve TF {tf_id} from JASPAR"}
        )

    data = r.json()

    print(data)

    # data["pfm"] is now a dict with keys "A", "C", "G", "T", each an array of counts
    pfm_dict = data.get("pfm")
    if not pfm_dict:
        return JSONResponse(status_code=400, content={"error": "No PFM data found."})

    # Construct Biopython motif    
    fpm = FrequencyPositionMatrix("ACGT", pfm_dict)
    pwm = fpm.normalize(pseudocounts=0.1)
    pssm = pwm.log_odds()
    
    # Determine the motif length (all nucleotide lists in pfm_dict are assumed to be the same length).
    motif_length = len(pfm_dict["A"])  # integer representing motif length
    positions = []    # List[int]: will hold the starting index of each window.
    scores_list = []  # List[float]: will hold the computed score for each window.
    
    print("motif_length", motif_length)

    # Iterate over every possible window in the sequence where the motif can fit.
    for i in range(len(sequence) - motif_length + 1):
        window = sequence[i : i + motif_length]  # Extract a window of length equal to motif_length.
        # Compute the score using the PSSM.
        # pssm.calculate() computes the log-odds score for the window.
        score = pssm.calculate(window)
        positions.append(i)
        scores_list.append(float(score))
        print("i", i, "window", window, "score", score)
    
    print("scores_list", scores_list)
    print("positions", positions)

    # Find top hits (scores above 0)
    hits = []
    for pos, score in zip(positions, scores_list):
        if score > 0:  # Only include positive scores
            hits.append({
                "start": pos,
                "end": pos + motif_length,
                "score": round(score, 3),  # Round to 3 decimal places for cleaner output
                "sequence": sequence[pos:pos + motif_length]
            })
    
    # Sort hits by score in descending order
    top_hits = sorted(hits, key=lambda x: x["score"], reverse=True)
    
    return {
        "name": sequence_name,
        "sequence": sequence,
        "scores": scores_list,
        "positions": positions,
        "topHits": top_hits
    }


# Run with:
#   uvicorn main:app --reload
