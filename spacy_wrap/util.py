"""
Copyright (C) 2022 Explosion AI - All Rights Reserved
You may use, distribute and modify this code under the
terms of the MIT license.

Original code from:
https://github.com/explosion/spacy-transformers/blob/5a36943fccb66b5e7c7c2079b1b90ff9b2f9d020/spacy_transformers/data_classes.py


The following functions are copied/modified:
- split_by_doc. Changed to fetch logits instead of token embeddings
"""


from typing import List
import torch
from transformers.file_utils import ModelOutput
from thinc.api import torch2xp

from spacy_transformers.data_classes import TransformerData
from spacy_transformers.align import get_token_positions

import numpy as np


def split_by_doc(self) -> List[TransformerData]:
    """
    Split a TransformerData that represents a batch into a list with
    one TransformerData per Doc.

    Original code from:
    https://github.com/explosion/spacy-transformers/blob/5a36943fccb66b5e7c7c2079b1b90ff9b2f9d020/spacy_transformers/data_classes.py

    The following parts are modified:
    - split_by_doc. Changed to fetch logits instead of token embeddings
    """
    flat_spans = []
    for doc_spans in self.spans:
        flat_spans.extend(doc_spans)
    token_positions = get_token_positions(flat_spans)
    outputs = []
    start = 0
    prev_tokens = 0
    for doc_spans in self.spans:
        if len(doc_spans) == 0 or len(doc_spans[0]) == 0:
            outputs.append(TransformerData.empty())
            continue
        start_i = token_positions[doc_spans[0][0]]
        end_i = token_positions[doc_spans[-1][-1]] + 1
        end = start + len(doc_spans)
        doc_tokens = self.wordpieces[start:end]
        doc_align = self.align[start_i:end_i]
        doc_align.data = doc_align.data - prev_tokens
        model_output = ModelOutput()
        logits = self.model_output.logits  # changed to fetch logits
        for key, output in self.model_output.items():
            if isinstance(output, torch.Tensor):
                model_output[key] = torch2xp(output[start:end])
            elif (
                isinstance(output, tuple)
                and all(isinstance(t, torch.Tensor) for t in output)
                and all(t.shape[0] == logits.shape[0] for t in output)
            ):
                model_output[key] = [torch2xp(t[start:end]) for t in output]
        outputs.append(
            TransformerData(
                wordpieces=doc_tokens,
                model_output=model_output,
                align=doc_align,
            )
        )
        prev_tokens += doc_tokens.input_ids.size
        start += len(doc_spans)
    return outputs


def softmax(x):
    return np.exp(x) / sum(np.exp(x))
