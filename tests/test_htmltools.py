import re

from edgar.htmltools import (extract_elements,
                             table_html_to_dataframe,
                             html_to_text, get_table_elements,
                             get_text_elements, html_sections, dataframe_to_text, ChunkedDocument)
from pathlib import Path
from rich import print
import pandas as pd
from edgar import Filing
from edgar.company_reports import EightK

pd.options.display.max_columns = 12
pd.options.display.max_colwidth = 100
pd.options.display.width = 1000

Nvidia_2021_10k = Path("data/Nvidia.10-K.html").read_text()


def test_html2df():
    table_html = """
    <table>
  <thead>
    <tr>
        <td>id</td><td>name</td><td>age</td>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td>1</td><td>John</td><td>20</td>
    </tr>
    <tr>
        <td>2</td><td>Smith</td><td>30</td>
    </tr>
  </tbody>
</table>
    """
    df = table_html_to_dataframe(table_html)
    assert len(df) == 3
    print(df)


def test_tricky_table_html2_dataframe():
    table_html = """<table><br><tbody><br><tr><td></td><td></td><td>Item 5.02</td><td></td><td></td><td></td><td>Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers.</td><td></td><td></td></tr><br></tbody><br></table>"""
    df = table_html_to_dataframe(table_html)
    print(df)


def test_extract_elements():
    elements = extract_elements(Nvidia_2021_10k)

    table_elements = get_table_elements(elements)
    assert all([e.table is not None for e in table_elements])

    text_elements = get_text_elements(elements)
    assert all([e.type == "text" for e in text_elements])

    assert len(table_elements) + len(text_elements) == len(elements)


def test_dataframe_to_text():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    text = dataframe_to_text(df)
    assert "1" in text


def test_html2text():
    tenk_text = html_to_text(Nvidia_2021_10k)

    # Include tables
    tenk_text_with_tables = html_to_text(Nvidia_2021_10k, ignore_tables=False)

    assert len(tenk_text_with_tables) > len(tenk_text)
    print(tenk_text_with_tables)


def test_get_table_elements():
    filing = Filing(company='Tesla, Inc.', cik=1318605, form='10-K',
                    filing_date='2023-01-31', accession_no='0000950170-23-001409')
    elements = extract_elements(filing.html())
    table_elements = get_table_elements(elements)
    assert len(table_elements) > 50
    print(len(table_elements))


def test_html_sections_includes_all_tables():
    filing = Filing(form='8-K', filing_date='2023-10-10', company='ACELRX PHARMACEUTICALS INC', cik=1427925,
                    accession_no='0001437749-23-027971')
    html_text = filing.html()
    sections = html_sections(html_text)
    for section in sections:
        if "Item" in section:
            print(section)


def test_html_sections_from_html_with_table_with_no_tbody():
    filing = Filing(form='3', filing_date='2023-10-10', company='BAM Partners Trust', cik=1861643,
                    accession_no='0001104659-23-108367')
    sections = filing.sections()
    assert sections


def test_that_items_are_ordered_in_chunked_document_for_filing():
    nvidia_10k_html = Path("data/Nvidia.10-K.html").read_text()
    chunked_documents = ChunkedDocument(nvidia_10k_html)

    # Test the repr
    repr_ = repr(chunked_documents)
    print()
    print(repr_)

    items = chunked_documents.list_items()
    print(items)
    assert items[-1] != 'Item 9A'
    assert chunked_documents['ITEM 1']
    assert chunked_documents['Item 1'] == chunked_documents['ITEM 1']
    assert chunked_documents['ITEM 1']

    print(chunked_documents['ITEM 1'])


def test_chunk_document_for_10k_amendment():
    filing = Filing(form='10-K/A', filing_date='2023-11-16', company='America Great Health',
                    cik=1098009, accession_no='0001185185-23-001212')
    tenk = filing.obj()
    chunked_document: ChunkedDocument = tenk.doc
    assert chunked_document.list_items() == ['Item 15']
    assert 'EXPLANATORY NOTE' in chunked_document['Item 15']
    assert 'Investment in Purecell Group' in chunked_document['Item 15']

    assert chunked_document['Item 1'] is None
    assert chunked_document['Item 2'] is None
    assert chunked_document['Item 3'] is None


def test_detect_iems_for_eightk_with_bold_tags():
    # This 8-K has one item, but it is not bein detected because the item is in bold tags
    filing = Filing(form='8-K', filing_date='2023-12-15', company='1 800 FLOWERS COM INC', cik=1084869,
                    accession_no='0001437749-23-034498')
    eightk: EightK = filing.obj()
    assert len(eightk.items) == 1
    assert '1-800-FLOWERS.COM, Inc. (the “Company”) held its Annual Meeting of' in eightk['Item 5.07']
