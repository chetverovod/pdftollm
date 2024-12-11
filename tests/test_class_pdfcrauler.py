"""Module provides test functions for mcs.py  module."""

import os
import sys
from pdftollm import PdfCrawler
sys.path.insert(0, './tests')

SENTENCE_SEPARATOR = '. ' 


def test_pdf_crawler():
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

    pc = PdfCrawler(file_name)
    complete_text, page_counter, table_counter, image_counter \
        = pc.build_flat_txt_doc(SENTENCE_SEPARATOR)
    print(complete_text, page_counter, table_counter, image_counter)

    assert len(complete_text) == 106860
    assert page_counter == 19
    assert table_counter == 7
    assert image_counter == 49


def test_pdf_crawler_short_doc():
    """
    Test function to verify the functionality of the PdfCrauler class.

    This function tests the build_flat_txt_doc method of the class by
    parsing pdf-file.

    Args:
        None

    Returns:
        None
    """
    
    file_name = './tests/2407.01449v3.pdf'

    pc = PdfCrawler(file_name)
    complete_text, page_counter, table_counter, image_counter \
        = pc.build_flat_txt_doc(SENTENCE_SEPARATOR)
    print(complete_text, page_counter, table_counter, image_counter)

    assert len(complete_text) == 133040
    assert page_counter == 20
    assert table_counter == 2
    assert image_counter == 21

