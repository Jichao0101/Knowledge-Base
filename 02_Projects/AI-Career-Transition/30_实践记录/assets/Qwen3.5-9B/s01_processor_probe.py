"""Offline, CPU-only input sizing for the existing full-image smoke sample."""
import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
import transformers
from transformers import AutoProcessor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--sample', required=True)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()
    model = Path(args.model).resolve()
    sample_path = Path(args.sample).resolve()
    sample = json.loads(sample_path.read_text(encoding='utf-8'))
    if isinstance(sample, list):
        if len(sample) != 1:
            raise ValueError('Expected exactly one smoke sample')
        sample = sample[0]
    image_path = Path(sample['image'])
    if not image_path.is_absolute():
        image_path = sample_path.parent / image_path
    with Image.open(image_path) as source:
        image = source.convert('RGB')
    processor = AutoProcessor.from_pretrained(str(model), local_files_only=True)
    instruction = (
        'Classify the eye state of the person in this image. '
        'Left and right refer to positions in the image, not anatomical sides. '
        'Use exactly one of: open, closed, occluded, narrow. '
        'Return only a JSON object with keys image_left_eye and image_right_eye. '
        'Do not output bounding boxes or explanations.'
    )
    messages = [{'role': 'user', 'content': [
        {'type': 'image'}, {'type': 'text', 'text': instruction}
    ]}]
    prompt = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    inputs = processor(text=[prompt], images=[image], return_tensors='pt',
                       padding=False, truncation=False)
    grids = inputs['image_grid_thw'].tolist()
    ip = processor.image_processor
    patch, merge = int(ip.patch_size), int(ip.merge_size)
    visual_tokens = sum(int(t * h * w) // (merge * merge) for t, h, w in grids)
    image_token = getattr(processor, 'image_token', '<|image_pad|>')
    image_token_id = processor.tokenizer.convert_tokens_to_ids(image_token)
    actual_image_tokens = int((inputs['input_ids'] == image_token_id).sum())
    if actual_image_tokens != visual_tokens:
        raise ValueError(f'Visual token mismatch: grid={visual_tokens}, input={actual_image_tokens}')
    length = int(inputs['attention_mask'].sum())
    report = {
        'status': 'processor_only_no_model_inference',
        'utc': datetime.now(timezone.utc).isoformat(),
        'transformers': transformers.__version__,
        'model': str(model), 'sample': str(sample_path), 'image': str(image_path),
        'sample_sha256': hashlib.sha256(sample_path.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'instruction': instruction, 'enable_thinking': False,
        'resize_policy': 'local_processor_defaults_no_crop_no_truncation',
        'processor_size': getattr(ip, 'size', None),
        'original_wh': list(image.size), 'image_grid_thw': grids,
        'processed_wh': [[int(w * patch), int(h * patch)] for t, h, w in grids],
        'patch_size': patch, 'merge_size': merge,
        'visual_tokens': visual_tokens, 'input_tokens': length,
        'other_input_tokens': length - visual_tokens,
        'generation_reserve_tokens': 128,
        'required_context_with_reserve': length + 128,
        'fits_trial_4096_context': length + 128 <= 4096,
        'tensor_shapes': {k: list(v.shape) for k, v in inputs.items() if hasattr(v, 'shape')},
    }
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    target = out / ('processor_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    text = json.dumps(report, ensure_ascii=False, indent=2)
    with target.open('x', encoding='utf-8') as f:
        f.write(text + '\n')
    print(text)
    print(f'\nSaved: {target}')


if __name__ == '__main__':
    main()
