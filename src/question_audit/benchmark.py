from __future__ import annotations
import argparse
from .io import load_json, read_jsonl, write_json


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--gold",default="data/benchmark_gold.json")
    ap.add_argument("--state",default="data/state/results.jsonl")
    ap.add_argument("--out",default="reports/benchmark.json")
    args=ap.parse_args()
    gold=load_json(args.gold)
    gold_by={str(x["question_id"]):x for x in gold["items"]}
    pred={}
    for row in read_jsonl(args.state): pred[str(row["question_id"])]=row
    overlap=[qid for qid in gold_by if qid in pred]
    if not overlap:
        write_json(args.out,{"evaluated":0,"note":"No overlap between gold and current results."})
        return
    answer_ok=sum(pred[q]["answer_letter"]==gold_by[q]["correct_letter"] for q in overlap)
    auto=[q for q in overlap if pred[q].get("status")=="AUTO_READY"]
    auto_ok=sum(pred[q]["answer_letter"]==gold_by[q]["correct_letter"] for q in auto)
    door_gold=[q for q in overlap if gold_by[q].get("door_id")]
    door_ok=sum(pred[q].get("door_id")==gold_by[q].get("door_id") for q in door_gold)
    write_json(args.out,{
        "evaluated":len(overlap),
        "answer_accuracy":round(answer_ok/len(overlap),4),
        "auto_ready_count":len(auto),
        "auto_ready_precision":round(auto_ok/len(auto),4) if auto else None,
        "door_evaluated":len(door_gold),
        "door_accuracy":round(door_ok/len(door_gold),4) if door_gold else None,
        "release_gate":{
            "recommended":"AUTO_READY precision >= 0.97 before unattended publication",
            "met": bool(auto and auto_ok/len(auto)>=0.97)
        }
    })

if __name__=="__main__":
    main()
