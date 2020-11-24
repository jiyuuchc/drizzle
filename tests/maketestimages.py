#!/usr/bin/python

import numpy as np
import math
import scipy.ndimage
import skimage.draw

_rng = np.random.default_rng()

def get_gauss_psf(psf_sigma = 6.0):
    psf_size = math.ceil(psf_sigma * 3)
    filter = np.exp(-np.arange(-psf_size,psf_size+1, dtype=np.float32)**2 / 2 / psf_sigma / psf_sigma)
    filter /= filter.sum()

    filter2 = filter[..., np.newaxis] * filter[np.newaxis, ...]
    return filter2

def gen_pb_seq(s= 250, n_steps = 50, scale = 25, alpha_p = 0.2, alpha_n = 2e-4):
    img_size = (s,s)
    img = np.zeros(img_size, dtype = np.float32)
    rr,cc,val = skimage.draw.line_aa(int(s*0.5), int(s*0.2), int(s*0.45), int(s*0.8))
    img[rr,cc] = val * scale
    rr,cc,val = skimage.draw.line_aa(int(s*0.5), int(s*0.2), int(s*0.55), int(s*0.8))
    img[rr,cc] = val * scale

    img_p = _rng.poisson(img)

    imgs = np.zeros((n_steps,) + img_size, dtype = np.float32)
    imgs[0,...] = img_p
    img_n = np.zeros_like(img_p)

    for i in range(1, n_steps):
        delta = _rng.binomial(img_p, alpha_p)
        delta -= _rng.binomial(img_n, alpha_n)
        img_p -= delta
        img_n += delta
        imgs[i,...] = img_p

    return imgs

def gen_photon_seq(seq, psf, brightness = 1000):
    imgs_c = np.zeros_like(seq)
    for idx in range(seq.shape[0]):
        tmp = scipy.ndimage.convolve(seq[idx,...], psf, mode = 'constant')
        imgs_c[idx,...] = _rng.poisson(tmp * brightness).astype(np.float32)

    return imgs_c

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate a test image sequence.')
    parser.add_argument('pathname', metavar='<pathname>', nargs='?', default='test_imgs', help='a file to save the results to')
    args = parser.parse_args()

    _rng = np.random.default_rng(42)
    psf = get_gauss_psf()
    seq = gen_pb_seq()
    imgs = gen_photon_seq(seq, psf)

    np.savez_compressed(args.pathname, imgs=imgs, truth=seq)
