from typing import Tuple

import torch
from torch.fft import fftn, fftshift, ifftn, ifftshift


def fourier_filter(x_in: torch.Tensor, threshold: int, scale: int) -> torch.Tensor:
    """Fourier filter as introduced in FreeU (https://arxiv.org/abs/2309.11497).

    This version of the method comes from here:
    https://github.com/huggingface/diffusers/pull/5164#issuecomment-1732638706
    """
    x = x_in
    B, C, H, W = x.shape

    # Non-power of 2 images must be float32
    if (W & (W - 1)) != 0 or (H & (H - 1)) != 0:
        x = x.to(dtype=torch.float32)

    # FFT
    x_freq = fftn(x, dim=(-2, -1))
    x_freq = fftshift(x_freq, dim=(-2, -1))

    B, C, H, W = x_freq.shape
    mask = torch.ones((B, C, H, W), device=x.device)

    crow, ccol = H // 2, W // 2
    mask[..., crow - threshold : crow + threshold, ccol - threshold : ccol + threshold] = scale
    x_freq = x_freq * mask

    # IFFT
    x_freq = ifftshift(x_freq, dim=(-2, -1))
    x_filtered = ifftn(x_freq, dim=(-2, -1)).real

    return x_filtered.to(dtype=x_in.dtype)


def fourier_filter_3d(x_in: torch.Tensor, threshold: int, scale: int) -> torch.Tensor:
    """Fourier filter for 3D data as introduced in FreeU (https://arxiv.org/abs/2309.11497)."""
    x = x_in
    B, C, D, H, W = x.shape

    # Non-power of 2 volumes must be float32
    if (W & (W - 1)) != 0 or (H & (H - 1)) != 0 or (D & (D - 1)) != 0:
        x = x.to(dtype=torch.float32)

    # FFT
    x_freq = fftn(x, dim=(-3, -2, -1))
    x_freq = fftshift(x_freq, dim=(-3, -2, -1))

    B, C, D, H, W = x_freq.shape
    mask = torch.ones((B, C, D, H, W), device=x.device)

    cd, crow, ccol = D // 2, H // 2, W // 2
    # Apply threshold to create a cube of ones in the center of the mask
    mask[
        ..., cd - threshold : cd + threshold, crow - threshold : crow + threshold, ccol - threshold : ccol + threshold
    ] = scale
    x_freq = x_freq * mask

    # IFFT
    x_freq = ifftshift(x_freq, dim=(-3, -2, -1))
    x_filtered = ifftn(x_freq, dim=(-3, -2, -1)).real

    # Ensure the output is the same dtype as the input
    return x_filtered.to(dtype=x_in.dtype)


def apply_freeu(
    resolution_idx: int, hidden_states: torch.Tensor, res_hidden_states: torch.Tensor, **freeu_kwargs
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Applies the FreeU mechanism as introduced in https:
    //arxiv.org/abs/2309.11497. Adapted from the official code repository: https://github.com/ChenyangSi/FreeU.

    Args:
    ----
        resolution_idx (`int`): Integer denoting the UNet block where FreeU is being applied.
        hidden_states (`torch.Tensor`): Inputs to the underlying block.
        res_hidden_states (`torch.Tensor`): Features from the skip block corresponding to the underlying block.
        s1 (`float`): Scaling factor for stage 1 to attenuate the contributions of the skip features.
        s2 (`float`): Scaling factor for stage 2 to attenuate the contributions of the skip features.
        b1 (`float`): Scaling factor for stage 1 to amplify the contributions of backbone features.
        b2 (`float`): Scaling factor for stage 2 to amplify the contributions of backbone features.
    """
    if resolution_idx == 0:
        num_half_channels = hidden_states.shape[1] // 2
        hidden_states[:, :num_half_channels] = hidden_states[:, :num_half_channels] * freeu_kwargs["b1"]
        res_hidden_states = fourier_filter_3d(res_hidden_states, threshold=1, scale=freeu_kwargs["s1"])
    if resolution_idx == 1:
        num_half_channels = hidden_states.shape[1] // 2
        hidden_states[:, :num_half_channels] = hidden_states[:, :num_half_channels] * freeu_kwargs["b2"]
        res_hidden_states = fourier_filter_3d(res_hidden_states, threshold=1, scale=freeu_kwargs["s2"])

    return hidden_states, res_hidden_states
