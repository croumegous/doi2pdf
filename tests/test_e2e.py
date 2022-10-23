import pytest
from doi2pdf import doi2pdf
from os import path


@pytest.mark.parametrize(
    "doi,name,url,output",
    [
        ("10.48550/arXiv.2203.15556", None, None, "/tmp/Training_Compute-Optimal_Large_Language_Models.pdf"),
        (None, "Training Compute-Optimal Large Language Models", None, "/tmp/Training_Compute-Optimal_Large_Language_Models.pdf"),
        (None, "Attention is all you need", None, "/tmp/Transformer.pdf"),
        (None, None, "https://www.science.org/doi/10.1126/science.1166301", "/tmp/science.pdf"),
    ],
)
def test_doi2pdf_ok(doi, name, url, output):
    doi2pdf(doi, name=name, url=url, output=output)    
    assert path.exists(output)


@pytest.mark.parametrize(
    "doi,name,url",
    [
        ("10.48550/arXiv.2203.99999", None, None),
        ("10.48550/arXiv.2203.15556", "Training Compute-Optimal Large Language Models", None),
        (None, None, None),
    ],
)
def test_doi2pdf_error(doi, name, url):
    with pytest.raises(Exception):
        doi2pdf(doi, name=name, url=url)  