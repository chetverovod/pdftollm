"""Module provides test functions for mcs.py  module."""

import sys
from pdftollm import PdfCrawler
sys.path.insert(0, './tests')

SENTENCE_SEPARATOR = '. '


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

    file_name = './tests/2411.04952v1.pdf'

    pc = PdfCrawler(file_name)
    complete_text, page_counter, table_counter, image_counter \
        = pc.build_flat_txt_doc(SENTENCE_SEPARATOR)
    print(complete_text, page_counter, table_counter, image_counter)

    if pc.crop_txt is True:
        assert len(complete_text) == 51236
    else:
        assert len(complete_text) == 108562
    assert page_counter == 13
    assert table_counter == 27
    assert image_counter == 159


def test_pdf_crawler_long_doc():
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

    if pc.crop_txt is True:
        assert len(complete_text) == 53024
    else:
        assert len(complete_text) == 133040
    assert page_counter == 20
    assert table_counter == 2
    assert image_counter == 21

