import argparse
from pathlib import Path

def str2bool(v: str) -> bool:
    """Parses a string value for a true-like or false-like value to be turned into a `bool`

    Meant to be used with `argparse` for command line inputs. Raises appropriate error to parser.

    Parameters
    ----------
    v : str
        Input should be a bool-like string.

        Something like "yes", "true", "1", for True, or "no", "false", "0" for False.

    Returns
    -------
    v : bool
        Output value is a Python `bool`, strictly `True` or `False`.

    Raises
    ------
    argparse.ArgumentTypeError
        Could not convert value supplied. 
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
