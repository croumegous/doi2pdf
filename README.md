# doi2pdf 
`doi2pdf` is a command line tool to download PDFs of reasearch paper from DOI, name or url, written in Python.  
It can be used either as a command line tool or as inside a Python script.


## Installation

```bash
pip install doi2pdf
```


## CLI usage
```bash
doi2pdf --name "Attention is all you need" --output "Transformer.pdf" --open
doi2pdf --url "https://arxiv.org/abs/1706.03762" --output "Transformer.pdf" --open
doi2pdf --doi "10.48550/arXiv.2203.15556" --output "Chinchilla.pdf" --open
```


Can also be used as a library.

```python
from doi2pdf import doi2pdf

doi2pdf("10.48550/arXiv.2203.15556", output="Chinchilla.pdf")
```


## Troobleshooot

- If error `DOI not found` appears it means sci hub could not retrieve the paper, you might need to override default sci-hub URL with a mirror, like so:

```bash
SCI_HUB_URL=https://sci-hub.wf/ doi2pdf --name "Attention is all you need" --open
```

- If error `Paper not found` appears, you might want to try another way to retrieve the research paper, using DOI instead of name or name instead of URL.

