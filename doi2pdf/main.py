import argparse
from typing import Optional
import subprocess
import bs4
import requests
import os


class NotFoundError(Exception):
    pass


SCI_HUB_URL = os.getenv("SCI_HUB_URL", "https://sci-hub.mksa.top/")


def doi2pdf(
    doi: Optional[str] = None,
    *,
    output: Optional[str] = None,
    name: Optional[str] = None,
    url: Optional[str] = None,
    open_pdf: bool = False,
):
    """Retrieves the pdf file from DOI, name or URL of a research paper.
    Args:
        doi (Optional[str]): _description_. Defaults to None.
        output (str, optional): _description_. Defaults to None.
        name (Optional[str], optional): _description_. Defaults to None.
        url (Optional[str], optional): _description_. Defaults to None.
        open_pdf (bool, optional): _description_. Defaults to False.
    """

    if len([arg for arg in (doi, name, url) if arg is not None]) > 1:
        raise ValueError("Only one of doi, name, url must be specified.")

    doi, title, pdf_url = get_paper_metadata(doi, name, url)

    if pdf_url:
        try:
            pdf_content = get_pdf_from_url(pdf_url)
        except NotFoundError:
            pdf_url = retrieve_scihub(doi)
            pdf_content = get_pdf_from_url(pdf_url)

    filename = title.replace(" ", "_") + ".pdf"
    if output is None:
        output = f"/tmp/{filename}"

    with open(output, "wb") as f:
        f.write(pdf_content)

    if open_pdf:
        subprocess.call(["xdg-open", output])


def get_paper_metadata(doi, name, url):
    """Returns metadata of a paper with http://openalex.org/"""
    if name:
        api_res = requests.get(
            f"https://api.openalex.org/works?search={name}&per-page=1&page=1&sort=relevance_score:desc"
        )
    if doi:
        api_res = requests.get(f"https://api.openalex.org/works/https://doi.org/{doi}")
    if url:
        api_res = requests.get(f"https://api.openalex.org/works/{url}")

    if api_res.status_code != 200:
        raise NotFoundError("Paper not found.")

    metadata = api_res.json()
    if metadata.get("results") is not None:
        metadata = metadata["results"][0]

    if metadata.get("doi") is not None:
        doi = metadata["doi"][len("https://doi.org/"):]
    title = metadata["display_name"]
    pdf_url = metadata["open_access"]["oa_url"]
    if pdf_url is None:
        if metadata.get("host_venue") is not None:
            pdf_url = metadata["host_venue"]["url"]
        elif metadata.get("primary_location") is not None:
            pdf_url = metadata['primary_location']['landing_page_url']
        else:
            raise NotFoundError("PDF URL not found.")

    print("Found paper: ", title)
    return doi, title, pdf_url


def get_html(url):
    """Returns bs4 object that you can iterate through based on html elements and attributes."""
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    }
    html = s.get(url, timeout=10, headers=headers, allow_redirects=False)
    html.encoding = "utf-8"
    html.raise_for_status()
    html = bs4.BeautifulSoup(html.text, "html.parser")
    return html


def retrieve_scihub(doi):
    """Returns the URL of the pdf file from the DOI of a research paper thanks to sci-hub."""
    html_sci_hub = get_html(f"{SCI_HUB_URL}{doi}")
    iframe = html_sci_hub.find("iframe", {"id": "pdf"})
    if iframe is None:
        raise NotFoundError("DOI not found.")

    return iframe["src"]


def get_pdf_from_url(url):
    """Returns the content of a pdf file from a URL."""
    res = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        },
    )
    if res.status_code != 200:
        raise NotFoundError("Bad PDF URL.")
    return res.content


def main():
    parser = argparse.ArgumentParser(
        description="Retrieves the pdf file from DOI of a research paper.", epilog=""
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Relative path of the target pdf file.",
        metavar="path",
    )

    parser.add_argument(
        "--doi", type=str, help="DOI of the research paper.", metavar="DOI"
    )

    parser.add_argument(
        "-n", "--name", type=str, help="Name of the research paper.", metavar="name"
    )

    parser.add_argument(
        "--url", type=str, help="URL of the research paper.", metavar="url"
    )

    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the pdf file after downloading.",
    )

    args = parser.parse_args()

    if args.doi is None and args.name is None and args.url is None:
        parser.error("At least one of --doi, --name, --url must be specified.")
    if len([arg for arg in (args.doi, args.name, args.url) if arg is not None]) > 1:
        parser.error("Only one of --doi, --name, --url must be specified.")

    doi2pdf(
        args.doi, output=args.output, name=args.name, url=args.url, open_pdf=args.open
    )


if __name__ == "__main__":
    main()
