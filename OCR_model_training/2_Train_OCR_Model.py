import os
import shutil
import subprocess
import urllib.request
import tarfile
import sys

# list of path used.
base_dir = os.path.abspath(".")
paddleocr_repo = os.path.join(base_dir, "PaddleOCR")
train_txt = os.path.join(base_dir, "train.txt")
output_dir = os.path.join(base_dir, "output", "rec_handwriting")

# Storing pretrain information
pretrained_url = "https://paddleocr.bj.bcebos.com/dygraph_v2.0/en/en_number_mobile_v2.0_rec_slim_train.tar"
pretrained_dir = os.path.join(base_dir, "pretrain_models", "rec_crnn")
pretrained_tar = os.path.join(base_dir, "pretrained_model.tar")
pretrained_model_path = os.path.join(pretrained_dir, "en_number_mobile_v2.0_rec_slim_train/best_accuracy.pdparams").replace("\\", "/")
config_file = os.path.join("configs", "rec", "rec_custom_handwriting.yml")
config_path = os.path.join(paddleocr_repo, config_file)

# standardizing paths for use in YAML
output_dir_posix = output_dir.replace("\\", "/")

# Clone the repository for PaddleOCR if it is not already cloned
if not os.path.exists(paddleocr_repo):
    subprocess.run(["git", "clone", "https://github.com/PaddlePaddle/PaddleOCR"], check=True)
    subprocess.run(["pip", "install", "-r", os.path.join(paddleocr_repo, "requirements.txt")], check=True)

# Downloading the pretrained model
os.makedirs(pretrained_dir, exist_ok=True)
if not os.path.exists(os.path.join(pretrained_dir, "en_number_mobile_v2.0_rec_slim_train")):
    print("Downloading pretrained model...")
    urllib.request.urlretrieve(pretrained_url, pretrained_tar)
    print("Extracting pretrained model...")
    with tarfile.open(pretrained_tar, "r") as tar:
        tar.extractall(path=pretrained_dir)

# Configuration
config_yaml = f"""
Global:
  use_amp: True
  use_gpu: True
  epoch_num: 300
  log_smooth_window: 50
  print_batch_step: 10
  save_model_dir: {output_dir_posix}
  save_epoch_step: 5
  eval_batch_step: 1000
  evaluation_step: 500
  pretrained_model: {pretrained_model_path}
  checkpoints: null
  save_inference_dir: null
  use_visualdl: False
  infer_img: doc/imgs_words_en/word_10.png
  character_dict_path: PaddleOCR/ppocr/utils/dict/en_dict.txt
  max_text_length: 150
  infer_mode: False
  use_space_char: True

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 5 

Architecture:
  model_type: rec
  algorithm: CRNN
  Transform: null
  Backbone:
    name: MobileNetV3
    scale: 1.0
    model_name: small 
  Neck:
    name: SequenceEncoder
    encoder_type: rnn
    hidden_size: 48
  Head:
    name: CTCHead
    fc_decay: 0.00001

Loss:
  name: CTCLoss

PostProcess:
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc

Train:
  dataset:
    name: SimpleDataSet
    data_dir: ./
    label_file_list: [./train.txt]
    transforms:
      - DecodeImage: {{img_mode: BGR, channel_first: False}}
      - RecAug: null
      - CTCLabelEncode: null
      - RecResizeImg: {{image_shape: [3, 32, 320]}}
      - KeepKeys: {{keep_keys: ['image', 'label', 'length']}}
  loader:
    shuffle: True
    batch_size: 128
    batch_size_per_card: 128
    drop_last: True
    num_workers: 16

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: ./
    label_file_list: [./train.txt]
    transforms:
      - DecodeImage: {{img_mode: BGR, channel_first: False}}
      - CTCLabelEncode: null
      - RecResizeImg: {{image_shape: [3, 32, 320]}}
      - KeepKeys: {{keep_keys: ['image', 'label', 'length']}}
  loader:
    shuffle: False
    drop_last: False
    batch_size: 128
    batch_size_per_card: 128
    num_workers: 4
"""

# Save YAML config
os.makedirs(os.path.dirname(config_path), exist_ok=True)
with open(config_path, "w", encoding="utf-8") as f:
    f.write(config_yaml)

# Copy train.txt into PaddleOCR repo
shutil.copy(train_txt, os.path.join(paddleocr_repo, "train.txt"))

# Launch training
print("Starting fine-tuning...")
subprocess.run([
    sys.executable,
    os.path.join(paddleocr_repo, "tools", "train.py"),
    "-c",
    config_path
])