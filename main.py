import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import argparse
from collections import OrderedDict
from urllib.parse import urlparse


def get_blog_links(url):
    """
    Retrieve blog links from a given URL.

    :param url: The URL to scrape for blog links
    :type url: str
    :return: A list of dictionaries containing the title and URL of the scraped links
    :rtype: list
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if href.startswith("http"):
            links.append({"title": link.text, "url": href})

    return links


def deduplicate_links(links):
    """
    Deduplicate links with the same root domain.

    :param links: A list of dictionaries containing the title and URL of the links
    :type links: list
    :return: A deduplicated list of dictionaries containing the title and URL of the links
    :rtype: list
    """
    deduplicated_links = OrderedDict()
    for link in links:
        root_domain = urlparse(link["url"]).netloc
        if root_domain not in deduplicated_links:
            deduplicated_links[root_domain] = link

    return list(deduplicated_links.values())


def generate_opml(links, title):
    """
    Generate OPML from a list of links.

    :param links: A list of dictionaries containing the title and URL of the links
    :type links: list
    :param title: The title to use for the OPML
    :type title: str
    :return: An OPML-formatted string
    :rtype: str
    """
    opml = ET.Element("opml", {"version": "2.0"})
    head = ET.SubElement(opml, "head")
    title_element = ET.SubElement(head, "title")
    title_element.text = title

    body = ET.SubElement(opml, "body")

    for link in links:
        outline = ET.SubElement(
            body,
            "outline",
            {"type": "rss", "text": link["title"], "xmlUrl": link["url"]},
        )

    return ET.tostring(opml, encoding="unicode", method="xml")


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Scrape blogroll links and generate an OPML file."
    )
    parser.add_argument(
        "url", metavar="URL", type=str, help="The URL to scrape for blog links"
    )
    args = parser.parse_args()

    # Scrape blog links from the specified URL
    links = get_blog_links(args.url)
    # Deduplicate links based on their root domain
    deduplicated_links = deduplicate_links(links)
    # Parse the URL to extract the root domain for the OPML title
    url_parsed = urlparse(args.url)
    root_domain = url_parsed.netloc.split(".")[0]
    # Create the OPML title using the root domain
    opml_title = f"{root_domain} blogroll"
    # Generate the OPML content using the deduplicated links and title
    opml = generate_opml(deduplicated_links, opml_title)

    # Save the OPML content to a file with the title as the filename
    with open(f"{opml_title}.ompl", "w", encoding="utf-8") as file:
        file.write(opml)


if __name__ == "__main__":
    main()
