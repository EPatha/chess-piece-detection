#!/usr/bin/env python3
"""Contoh penggunaan chess_board_utils.

Usage:
    python3 example_annotate.py --image path/to/photo.jpg [--fen "fen_string"] [--out out.png]

Langkah interaktif:
- Klik 4 sudut papan dalam urutan TL,TR,BR,BL lalu tekan 'q'.
- Skrip akan menggambar overlay grid dan (jika FEN disediakan) anotasi bidak.
"""

import argparse
import cv2
from chess_board_utils import select_board_corners, compute_perspective_transform, draw_board_overlay, fen_to_piece_map, annotate_pieces


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--image', required=True, help='Path ke foto papan catur')
    p.add_argument('--fen', default=None, help='(opsional) FEN placement string untuk anotasi bidak')
    p.add_argument('--out', default='annotated.png', help='File output untuk menyimpan gambar teranotasi')
    args = p.parse_args()

    img = cv2.imread(args.image)
    if img is None:
        raise SystemExit(f"Gagal memuat gambar: {args.image}")

    print("Pilih 4 sudut papan di jendela gambar. Urut: TL,TR,BR,BL. Tekan 'q' bila selesai, 'r' untuk reset.")
    pts = select_board_corners(img)
    if len(pts) != 4:
        raise SystemExit("Tidak ada 4 titik sudut yang dipilih. Batal.")

    M, Minv, board_pixels = compute_perspective_transform(pts)

    out = draw_board_overlay(img, Minv, board_pixels=board_pixels, alpha=0.5)

    if args.fen:
        piece_map = fen_to_piece_map(args.fen)
        out = annotate_pieces(out, piece_map, Minv, board_pixels=board_pixels)

    cv2.imshow('Annotated', out)
    cv2.imwrite(args.out, out)
    print(f"Simpan hasil ke {args.out}")
    print("Tekan tombol apa saja pada jendela untuk keluar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
