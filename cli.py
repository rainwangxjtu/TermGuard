import argparse
from termguard.pipeline import run_pipeline_from_files


def main():
    p = argparse.ArgumentParser(description="TermGuard: terminology consistency checker (EN->ZH)")
    p.add_argument("--en", required=True, help="Path to English text file")
    p.add_argument("--zh", required=True, help="Path to Chinese translation text file")
    p.add_argument("--glossary", default=None, help="Optional glossary CSV with columns en_term,zh_term")
    p.add_argument("--out", default="outputs/run", help="Output directory")
    args = p.parse_args()

    result = run_pipeline_from_files(
        en_path=args.en,
        zh_path=args.zh,
        glossary_path=args.glossary,
        out_dir=args.out
    )

    print("\n✅ TermGuard finished.")
    print(f"- Report CSV : {result['report_csv']}")
    print(f"- Report JSON: {result['report_json']}")
    print(f"- Patched ZH : {result['patched_path']}")
    print(f"- Flags      : {len(result['flags'])}")


if __name__ == "__main__":
    main()
