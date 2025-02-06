#
# Converts EXR to Ultra HDR
# (C) 2025 Gissio
#
# For: [gainmap.js](https://github.com/MONOGRID/gainmap-js)
#

import argparse
import os
import shutil

import numpy as np
import OpenEXR
from PIL import Image


version = '1.0'


def load_exr(path):
    exr_file = OpenEXR.File(path)
    # exr_file.header())
    exr_channels = exr_file.channels()
    if 'RGB' in exr_channels:
        return exr_channels['RGB'].pixels
    elif 'RGBA' in exr_channels:
        pixels = exr_channels['RGBA'].pixels
        return pixels[:, :, 0:3]
    else:
        return None


def apply_exposure(map, exposure=1):
    return map * exposure


def tonemap_aces(map):
    a = 2.51
    b = 0.03
    c = 2.43
    d = 0.59
    e = 0.14

    return (map * (a * map + b)) / (map * (c * map + d) + e)


def tonemap_reinhard(map):
    return map / (map + 1)


def apply_gamma(map, gamma=2.2):
    return np.power(map, gamma)


def apply_gammacorrection(map, gamma=2.2):
    return np.power(map, 1.0 / gamma)


def saturate(map):
    return np.clip(map, 0, 1)


def get_pil_image(map):
    return Image.fromarray(
        np.clip(255 * map, 0, 255).astype(np.uint8))


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Tool for converting EXR to gainmap.js Ultra HDR files.')
    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('--exposure', type=float, default=1,
                        help='applies exposure')
    parser.add_argument('--sdr-tonemapping',
                        choices=['none', 'reinhard', 'aces'],
                        help='applies tonemapping for the SDR map')
    parser.add_argument('--sdr-quality', type=int, default=70,
                        help='sets the JPEG quality factor for the SDR map')
    parser.add_argument('--gain-quality', type=int, default=70,
                        help='sets the JPEG quality factor for the gain map')
    parser.add_argument('--gain-max',
                        type=float,
                        help='sets the maximum value for the gain map')
    parser.add_argument('--gain-gamma', type=float, default=1,
                        help='sets the gamma for the gain map')

    args = parser.parse_args()

    # Load input file
    input_map = load_exr(args.input_file)
    input_map = apply_exposure(input_map, args.exposure)

    # Process max gain if not set
    if args.gain_max == None:
        gain_max = np.max(input_map)
    else:
        gain_max = args.gain_max
    gain_max_log = np.log2(gain_max)
    gain_gamma = args.gain_gamma

    print(f'gain-max: {gain_max}')

    # Build SDR map
    sdr_map = input_map
    if args.sdr_tonemapping == 'reinhard':
        sdr_map = tonemap_reinhard(sdr_map)
    elif args.sdr_tonemapping == 'aces':
        sdr_map = tonemap_aces(sdr_map)
    sdr_map = saturate(sdr_map)
    sdr_map_gammacorrected = apply_gammacorrection(sdr_map)
    sdr_image = get_pil_image(sdr_map_gammacorrected)

    sdr_filename = '__uhdr_sdr.jpg'
    sdr_image.save(sdr_filename,
                quality=args.sdr_quality,
                optimize=True)

    # Build gain map (only is HDR required)
    if gain_max > 1:
        gain_map = (input_map + 1e-6) / (sdr_map + 1e-6)
        gain_map = np.log2(gain_map) / gain_max_log
        gain_map = saturate(gain_map)
        gain_map_gammacorrected = apply_gamma(gain_map, gain_gamma)
        gain_image = get_pil_image(gain_map_gammacorrected)

        gain_filename = '__uhdr_gain.jpg'
        gain_image.save(gain_filename,
                        quality=args.gain_quality,
                        optimize=True)

        # Build metadata
        metadata_filename = '__uhdr_metadata.cfg'
        metadata_file = open(metadata_filename, 'wt')
        metadata_file.write(f'--maxContentBoost 6.0 6.0 6.0\n')
        metadata_file.write(f'--minContentBoost 1.0 1.0 1.0\n')
        metadata_file.write(f'--gamma {gain_gamma} {gain_gamma} {
            gain_gamma}\n')
        metadata_file.write(f'--offsetSdr 0.0 0.0 0.0\n')
        metadata_file.write(f'--offsetHdr 0.0 0.0 0.0\n')
        metadata_file.write(f'--hdrCapacityMin 0.0\n')
        metadata_file.write(f'--hdrCapacityMax {gain_max_log}\n')
        metadata_file.write(f'--useBaseColorSpace 1\n')
        metadata_file.close()

        # Build Ultra HDR JPEG file
        os.system(f'ultrahdr_app -m 0 -i "{sdr_filename}" -g "{
            gain_filename}" -f "{metadata_filename}" -z "{args.output_file}"')

    else:
        shutil.copy(sdr_image, args.output_file)

    # Clean-up
    if os.path.exists(sdr_filename):
        os.remove(sdr_filename)
    if os.path.exists(gain_filename):
        os.remove(gain_filename)
    if os.path.exists(metadata_filename):
        os.remove(metadata_filename)


if __name__ == "__main__":
    main()
