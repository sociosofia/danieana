from __future__ import annotations
import argparse
from .io import read_jsonl, write_json


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state",default="data/state/results.jsonl")
    ap.add_argument("--ready",default="data/output/auto_ready.json")
    ap.add_argument("--review",default="data/output/review.json")
    ap.add_argument("--hold",default="data/output/hold.json")
    args=ap.parse_args()
    latest={}
    for row in read_jsonl(args.state):
        latest[row["question_id"]]=row
    buckets={"AUTO_READY":[],"REVIEW":[],"HOLD":[]}
    for row in latest.values():
        buckets.setdefault(row.get("status","REVIEW"),[]).append(row)
    write_json(args.ready,{"count":len(buckets["AUTO_READY"]),"items":buckets["AUTO_READY"]})
    write_json(args.review,{"count":len(buckets["REVIEW"]),"items":buckets["REVIEW"]})
    write_json(args.hold,{"count":len(buckets["HOLD"]),"items":buckets["HOLD"]})

if __name__=="__main__":
    main()
