"""Shared constants for the chess vision application."""

# Edge detection thresholds
EDGE_THRESHOLD = 150
EDGE_DIFFERENCE_THRESHOLD = 50

# Piece values for ambiguity resolution
PIECE_VALUES = {
    6: 9,  # QUEEN
    4: 5,  # ROOK
    3: 3,  # BISHOP
    2: 3,  # KNIGHT
    1: 1,  # PAWN
}

# Lichess Brown Theme Colors (BGR format for OpenCV)
COLOR_LIGHT = (181, 217, 240)  # #F0D9B5
COLOR_DARK = (99, 136, 181)    # #B58863
