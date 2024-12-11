"""Module provides test functions for mcs.py  module."""

import os
import sys
from pdftollm import PdfCrauler
sys.path.insert(0, './tests')

SENTENCE_SEPARATOR = '. ' 

def test_aug_amp_control():
    """
    Test function to verify the functionality of the PdfCrauler class.

    This function tests the build_flat_txt_doc method of the class by
    parsing pdf-file.

    Args:
        None

    Returns:
        None
    """
    
    file_name = './pdf_docs/Норникель_Внутрення_цена_на_углерод.pdf'

    pc = PdfCrauler(file_name)
    complete_text, page_counter, table_counter, image_counter \
        = pc.build_flat_txt_doc(SENTENCE_SEPARATOR)
    print(complete_text, page_counter, table_counter, image_counter)

    assert len(complete_text) == 106860
    assert page_counter == 19
    assert table_counter == 7
    assert image_counter == 49

