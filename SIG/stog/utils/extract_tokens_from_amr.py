from stog.data.dataset_readers import AbstractMeaningRepresentationDatasetReader
import sys
from stog.utils import logging

logger = logging.init_logger()
def extract_sig_token(file_path):
    dataset_reader = AbstractMeaningRepresentationDatasetReader()
    for instance in dataset_reader.read(file_path):
        sig_tokens = instance.fields["sig_tokens"]["decoder_tokens"]
        yield " ".join(sig_tokens)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""Usage:
    python {} [sig_file]

The output will in stdout.
              """)
    for filename in sys.argv[1:]:
        for line in extract_sig_token(filename):
            sys.stdout.write(line + "\n")



