"""Utility functions for speech expansion."""


def expand_chess_text(san):
    """Convert SAN (e.g. Nf3) to spoken text."""
    text = san.replace('N', 'Knight ').replace('B', 'Bishop ').replace('R', 'Rook ').replace('Q', 'Queen ').replace('K', 'King ')
    if text[0].islower():
        text = "Pawn to " + text
    text = text.replace('x', ' captures ').replace('+', ' check').replace('#', ' checkmate')
    text = text.replace('O-O-O', 'Long Castles').replace('O-O', 'Short Castles')
    return text
