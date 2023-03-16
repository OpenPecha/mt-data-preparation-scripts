from pathlib import Path
import subprocess

DATA_PATH = Path("../raw-alignments/aligned-output/wisdom-publications")
OUTOUT_PATH = Path("mt-repos")


def load_alignment(fn):
    content = fn.read_text()
    if not content:
        return []

    for seg_pair in content.splitlines():
        if not seg_pair:
            continue

        if "\t" in seg_pair:
            try:
                bo_seg, en_seg = seg_pair.split("\t", 1)
            except Exception as e:
                print(f"Error: {e} in {fn}")
                raise

        else:
            bo_seg = seg_pair
            en_seg = "\n"
        yield bo_seg, en_seg

def create_mt_repo(alignment, n, source_file):
    mt_repo_path = OUTOUT_PATH / f"MT{n:03d}"
    mt_repo_path.mkdir(exist_ok=True, parents=True)

    text_bo = ""
    text_en = ""
    for bo_seg, en_seg in alignment:
        text_bo += bo_seg + "\n"
        text_en += en_seg + "\n"

    text_bo_fn = mt_repo_path / f"mt{n:03d}-bo.txt"
    text_en_fn = mt_repo_path / f"mt{n:03d}-en.txt"
    readme_fn = mt_repo_path / "README.md"
    text_bo_fn.write_text(text_bo)
    text_en_fn.write_text(text_en)
    readme_fn.write_text(f"Source: {source_file}")


    return mt_repo_path

def publish(repo_path, org):
    print("pushing", repo_path, "...")
    subprocess.call(["git", "init"], cwd=repo_path)
    subprocess.call("git add .", shell=True, cwd=repo_path)
    subprocess.call("git commit -m 'Initial commit'", shell=True, cwd=repo_path)
    subprocess.call(f"gh repo create MonlamAI/{repo_path.name} --private --source=. --remote=origin --push", shell=True, cwd=repo_path)


def main():
    mt_repo_cur_id = 2
    for fn in DATA_PATH.iterdir():
        alignment = load_alignment(fn)
        mt_repo_path = create_mt_repo(alignment, mt_repo_cur_id, source_file=fn)
        publish(mt_repo_path, org="MonlamAI")
        mt_repo_cur_id += 1


if __name__ == "__main__":
    exit(main())
