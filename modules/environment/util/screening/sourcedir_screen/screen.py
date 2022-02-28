import argparse
import os
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-data-dir",
        type=Path,
        default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/processing/output"),
    )
    parser.add_argument(
        "--module", choices=["mxnet", "sklearn", "torch"], default="mxnet"
    )
    args = parser.parse_args()
    print(vars(args))

    if args.module == "mxnet":
        import mxnet as pkg
    elif args.module == "sklearn":
        import sklearn as pkg
    else:
        import torch as pkg

    with (args.output_data_dir / "screenings.jsonl").open("w") as f:
        f.write(f'{{"module": "{pkg.__name__}", "version": "{pkg.__version__}"}}\n')

        for path in ("/opt/ml/input/data/train", "/opt/ml/processing/input"):
            flist = list(Path(path).glob("**/*"))
            f.write(f'{{"{path}": {flist}}}\n')
