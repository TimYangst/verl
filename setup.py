# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# setup.py is the fallback installation script when pyproject.toml does not work
import os
from pathlib import Path

from setuptools import find_packages, setup

version_folder = os.path.dirname(os.path.join(os.path.abspath(__file__)))

with open(os.path.join(version_folder, "verl/version/version")) as f:
    __version__ = f.read().strip()

install_requires = [
    "accelerate",
    "codetiming",
    "datasets",
    "dill",
    "hydra-core",
    "numpy<2.0.0",
    "pandas",
    "peft",
    "pyarrow>=19.0.0",
    "pybind11",
    "pylatexenc",
    "ray[default]>=2.41.0",
    "torchdata",
    "tensordict>=0.8.0,<=0.10.0,!=0.9.0",
    "transformers",
    "wandb",
    "packaging>=20.0",
    "tensorboard",
]

TEST_REQUIRES = ["pytest", "pre-commit", "py-spy", "pytest-asyncio", "pytest-rerunfailures"]
PRIME_REQUIRES = ["pyext"]
GEO_REQUIRES = ["mathruler", "torchvision", "qwen_vl_utils"]
GPU_REQUIRES = ["liger-kernel", "flash-attn"]
MATH_REQUIRES = ["math-verify"]  # Add math-verify as an optional dependency
VLLM_REQUIRES = ["tensordict>=0.8.0,<=0.10.0,!=0.9.0", "vllm>=0.8.5,<=0.12.0"]
TRTLLM_REQUIRES = ["tensorrt-llm>=1.2.0rc6"]
SGLANG_REQUIRES = [
    "tensordict>=0.8.0,<=0.10.0,!=0.9.0",
    "sglang[srt,openai]==0.5.8",
    "torch==2.9.1",
]
TRL_REQUIRES = ["trl<=0.9.6"]
MCORE_REQUIRES = ["mbridge"]
TRANSFERQUEUE_REQUIRES = ["TransferQueue==0.1.6"]

# ---- VeOmni training stack (opt-in, uv-friendly) -----------------------------
# These three extras together reproduce the modelchef veomni-recipes nightly
# environment for `actor_rollout_ref.actor.strategy=veomni` training, pinned to
# torch 2.9.1+cu129 / B200-class GPUs. They are intentionally separate from the
# existing GPU/VLLM/SGLANG extras so that `pip install verl[gpu]` /
# `pip install verl[vllm]` / `pip install verl[sglang]` keep their pre-existing
# behavior.
#
# Recommended invocation (with uv):
#   uv sync --extra veomni --extra veomni-sglang     # default rollout
#   uv sync --extra veomni --extra veomni-vllm       # vllm rollout
# `veomni-vllm` and `veomni-sglang` are mutually exclusive (declared in
# pyproject.toml [tool.uv].conflicts) because they pin different transformers,
# cuda-python, torchcodec, flashinfer and llguidance versions.
VEOMNI_REQUIRES = [
    "veomni==0.1.9a2",
    # NOTE: We intentionally inline the cu129 stack here rather than using
    # `veomni[gpu]==0.1.9a2`. veomni[gpu] hard-pulls `flash-attn-3`, but the
    # only PyPI release of flash-attn-3 (0.0.0) is yanked, and uv applies
    # [tool.uv.sources] inconsistently for transitive deps. Listing the deps
    # directly lets us pin via [tool.uv.sources] / override-dependencies.
    "torch==2.9.1+cu129",
    "torchvision==0.24.1+cu129",
    "torchaudio==2.9.1+cu129",
    "torchcodec==0.9.1",
    "triton==3.5.1",
    "liger-kernel",
    "flash-attn",
    # The training shell scripts (e.g. examples/grpo_trainer/run_qwen3_5-35b-a3b_veomni.sh)
    # were validated against this exact flash-linear-attention release.
    "flash-linear-attention==0.4.1",
    "cuda-python==12.9.1",
    "hf_transfer",
]
VEOMNI_VLLM_REQUIRES = [
    "vllm==0.14.1",
    # vllm 0.14.1 caps transformers at <5; veomni itself does not pin
    # transformers, so we land on a 4.x line that satisfies vllm.
    "transformers==4.57.3",
]
VEOMNI_SGLANG_REQUIRES = [
    # Mirrors modelchef's `sglang-hf530` extra: sglang 0.5.9 + transformers
    # 5.3.0 + flashinfer 0.6.3. sglang's own metadata pins transformers==4.57.1
    # but the modelchef nightly stack force-overrides to 5.3.0; we replicate the
    # override in pyproject.toml [tool.uv].override-dependencies.
    "sglang==0.5.9",
    "transformers==5.3.0",
    "flashinfer-python==0.6.3",
]

extras_require = {
    "test": TEST_REQUIRES,
    "prime": PRIME_REQUIRES,
    "geo": GEO_REQUIRES,
    "gpu": GPU_REQUIRES,
    "math": MATH_REQUIRES,
    "vllm": VLLM_REQUIRES,
    "sglang": SGLANG_REQUIRES,
    "trl": TRL_REQUIRES,
    "mcore": MCORE_REQUIRES,
    "trtllm": TRTLLM_REQUIRES,
    "transferqueue": TRANSFERQUEUE_REQUIRES,
    "veomni": VEOMNI_REQUIRES,
    "veomni-vllm": VEOMNI_VLLM_REQUIRES,
    "veomni-sglang": VEOMNI_SGLANG_REQUIRES,
}


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="verl",
    version=__version__,
    package_dir={"": "."},
    packages=find_packages(where="."),
    url="https://github.com/verl-project/verl",
    license="Apache 2.0",
    author="Bytedance - Seed - MLSys",
    author_email="zhangchi.usc1992@bytedance.com, gmsheng@connect.hku.hk",
    description="verl: Volcano Engine Reinforcement Learning for LLM",
    install_requires=install_requires,
    extras_require=extras_require,
    package_data={
        "": ["version/*"],
        "verl": [
            "trainer/config/*.yaml",
            "trainer/config/*/*.yaml",
            "experimental/*/config/*.yaml",
        ],
    },
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
