"""Utility functions for annotating and mapping an 8x8 chessboard in images.

Assumptions:
- The user provides the four board corner points in the image in this order:
  top-left, top-right, bottom-right, bottom-left (clockwise).
- The destination (warped) board is a square of size `board_pixels` (default 800).
- The warped board's top-left corresponds to square a8 (i.e. files left->right a->h, ranks top->bottom 8->1).

Functions:
- select_board_corners(image): interactive helper to click the 4 corners
- compute_perspective_transform(src_pts): returns transform matrix M and inverse Minv
- pixel_to_square(point, M): map an (x,y) in the original image to algebraic square like 'e4'
- square_to_pixel(square, Minv): map a square to the pixel center in the original image
- draw_board_overlay(image, Minv): draws an 8x8 grid + labels onto the original image
- annotate_pieces(image, piece_map, Minv): draw piece markers (piece_map: {square: label})
"""

from typing import Tuple, List, Dict
import cv2
import numpy as np


def select_board_corners(img: np.ndarray) -> List[Tuple[int, int]]:
    """Let user click 4 points (TL, TR, BR, BL) on the image. Returns list of 4 (x,y).

    Click order must be clockwise starting at top-left. Press 'r' to reset, 'q' when done.
    """
    pts: List[Tuple[int, int]] = []
    clone = img.copy()

    def mouse_cb(event, x, y, flags, param):
        nonlocal pts, clone
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(pts) < 4:
                pts.append((x, y))
                cv2.circle(clone, (x, y), 4, (0, 255, 0), -1)
                cv2.putText(clone, str(len(pts)), (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    win = "Select 4 board corners (TL,TR,BR,BL)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, mouse_cb)

    while True:
        display = clone.copy()
        h, w = display.shape[:2]
        cv2.putText(display, "Click 4 corners (TL,TR,BR,BL). r=reset, q=quit/ok",
                    (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(win, display)
        key = cv2.waitKey(20) & 0xFF
        if key == ord('r'):
            pts = []
            clone = img.copy()
        elif key == ord('q'):
            break

    cv2.destroyWindow(win)
    return pts


def compute_perspective_transform(src_pts: List[Tuple[int, int]], board_pixels: int = 800) -> Tuple[np.ndarray, np.ndarray, int]:
    """Compute perspective transform from image points to a top-down square board.

    src_pts: list of 4 (x,y) in order TL,TR,BR,BL
    Returns (M, Minv, board_pixels)
    """
    if len(src_pts) != 4:
        raise ValueError("src_pts must be 4 points (TL,TR,BR,BL)")
    src = np.array(src_pts, dtype=np.float32)
    dst = np.array([[0, 0], [board_pixels, 0], [board_pixels, board_pixels], [0, board_pixels]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    return M, Minv, board_pixels


def warp_board(img: np.ndarray, M: np.ndarray, board_pixels: int = 800) -> np.ndarray:
    return cv2.warpPerspective(img, M, (board_pixels, board_pixels))


def _point_transform(pt: Tuple[float, float], M: np.ndarray) -> Tuple[float, float]:
    """Apply perspective transform to a single (x,y) point using cv2.perspectiveTransform."""
    arr = np.array([[pt]], dtype=np.float32)  # shape (1,1,2)
    res = cv2.perspectiveTransform(arr, M)
    x, y = float(res[0, 0, 0]), float(res[0, 0, 1])
    return x, y


def pixel_to_square(pt: Tuple[float, float], M: np.ndarray, board_pixels: int = 800) -> str:
    """Map image pixel (x,y) to algebraic square string like 'e4'.

    Orientation assumption: warped board top-left = a8, top-right = h8, bottom-left = a1.
    If your camera/view uses a different orientation, swap or rotate accordingly.
    """
    square_size = board_pixels / 8.0
    xw, yw = _point_transform(pt, M)  # point in warped board coords
    col = int(xw // square_size)
    row = int(yw // square_size)
    # clamp
    col = max(0, min(7, col))
    row = max(0, min(7, row))
    file = "abcdefgh"[col]
    rank = 8 - row
    return f"{file}{rank}"


def square_to_pixel(square: str, Minv: np.ndarray, board_pixels: int = 800) -> Tuple[int, int]:
    """Return center pixel (x,y) in original image corresponding to given algebraic square.

    Expects square like 'e4'. Uses same orientation assumption as pixel_to_square.
    """
    if len(square) not in (2, 3):
        raise ValueError("square must be like 'e4'")
    file_char = square[0].lower()
    rank = int(square[1:])
    file_idx = ord(file_char) - ord('a')
    if not (0 <= file_idx <= 7 and 1 <= rank <= 8):
        raise ValueError(f"Invalid square: {square}")
    square_size = board_pixels / 8.0
    row_idx = 8 - rank
    cx = (file_idx + 0.5) * square_size
    cy = (row_idx + 0.5) * square_size
    x_orig, y_orig = _point_transform((cx, cy), Minv)
    return int(round(x_orig)), int(round(y_orig))


def draw_board_overlay(img: np.ndarray, Minv: np.ndarray, board_pixels: int = 800,
                       line_color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2,
                       label: bool = True, alpha: float = 0.6) -> np.ndarray:
    """Draw an 8x8 grid with optional file/rank labels and project it back onto the image.

    Returns a new image with overlay blended.
    """
    h, w = img.shape[:2]
    overlay = np.zeros((board_pixels, board_pixels, 3), dtype=np.uint8)
    sq = board_pixels // 8
    # draw grid lines
    for i in range(9):
        x = int(i * sq)
        cv2.line(overlay, (x, 0), (x, board_pixels), line_color, 1)
        y = int(i * sq)
        cv2.line(overlay, (0, y), (board_pixels, y), line_color, 1)

    if label:
        # files a-h along top and bottom
        for i, ch in enumerate('abcdefgh'):
            x = int((i + 0.02) * sq)
            cv2.putText(overlay, ch, (x, int(0.05 * sq)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, line_color, 2)
            cv2.putText(overlay, ch, (x, int(board_pixels - 0.02 * sq)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, line_color, 2)
        # ranks 8-1 on left and right
        for i in range(8):
            rank = 8 - i
            y = int((i + 0.7) * sq)
            cv2.putText(overlay, str(rank), (int(0.02 * sq), y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, line_color, 2)
            cv2.putText(overlay, str(rank), (int(board_pixels - 0.06 * sq), y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, line_color, 2)

    # warp overlay back to original image space
    warped_overlay = cv2.warpPerspective(overlay, Minv, (w, h))
    # blend
    out = img.copy()
    mask = (warped_overlay.sum(axis=2) > 0)
    out[mask] = cv2.addWeighted(out, 1.0 - alpha, warped_overlay, alpha, 0)[mask]
    return out


def annotate_pieces(img: np.ndarray, piece_map: Dict[str, str], Minv: np.ndarray,
                    board_pixels: int = 800, circle_color=(0, 0, 255)) -> np.ndarray:
    """Draw markers and short labels for pieces given a mapping {square: label}.

    label is a short string (e.g., 'K', 'p', 'N', or unicode symbols if available).
    """
    out = img.copy()
    for square, label in piece_map.items():
        try:
            cx, cy = square_to_pixel(square, Minv, board_pixels)
        except ValueError:
            continue
        cv2.circle(out, (cx, cy), 18, circle_color, 2)
        cv2.putText(out, label, (cx - 10, cy + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, circle_color, 2, cv2.LINE_AA)
    return out


def fen_to_piece_map(fen: str) -> Dict[str, str]:
    """Simple FEN piece placement parser -> {square: pieceChar}.

    Only parses the piece placement field (first field) of FEN.
    Uppercase = White, lowercase = Black. Empty squares are skipped.
    """
    part = fen.strip().split()[0]
    rows = part.split('/')
    if len(rows) != 8:
        raise ValueError("FEN must have 8 '/'-separated rows in placement field")
    piece_map: Dict[str, str] = {}
    ranks = list(range(8, 0, -1))
    for r_idx, row in enumerate(rows):
        file_idx = 0
        for ch in row:
            if ch.isdigit():
                file_idx += int(ch)
            else:
                file = 'abcdefgh'[file_idx]
                rank = ranks[r_idx]
                square = f"{file}{rank}"
                piece_map[square] = ch
                file_idx += 1
    return piece_map


if __name__ == '__main__':
    print("This module provides utility functions for chessboard annotation. Import and use in scripts.")
