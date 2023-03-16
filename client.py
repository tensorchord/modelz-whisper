from http import HTTPStatus

import requests
from datasets import load_dataset


def main():
    ds = load_dataset(
        "hf-internal-testing/librispeech_asr_dummy", "clean", split="validation"
    )
    sample = ds[0]["audio"]
    with open(sample["path"], "rb") as f:
        resp = requests.post("http://localhost:8000/inference", data=f)
    if resp.status_code == HTTPStatus.OK:
        print(resp.json())
    else:
        print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
