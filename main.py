import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
from xml.dom import minidom

OWNER = "rjaakash"
REPO = "peachmeow"

REPO_URL = f"https://github.com/{OWNER}/{REPO}/releases"

API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"

HEADERS = {"Accept": "application/vnd.github.html+json"}


def prettify_xml(element):
    rough_string = ET.tostring(element, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def extract_brand(tag_name):
    return tag_name.split("-v")[0].strip()


def create_feed(brand, releases):
    feed = ET.Element(
        "feed", {"xmlns": "http://www.w3.org/2005/Atom", "xml:lang": "en-US"}
    )

    ET.SubElement(feed, "id").text = f"tag:github.com,2008:{REPO_URL}"

    ET.SubElement(feed, "title").text = brand

    ET.SubElement(feed, "updated").text = releases[0]["published_at"]

    ET.SubElement(
        feed,
        "link",
        {
            "type": "text/html",
            "rel": "alternate",
            "href": REPO_URL,
        },
    )

    for release in releases:
        entry = ET.SubElement(feed, "entry")

        ET.SubElement(entry, "id").text = (
            f"tag:github.com,2008:Repository/{release['id']}/{release['tag_name']}"
        )

        ET.SubElement(entry, "updated").text = release["published_at"]

        ET.SubElement(
            entry,
            "link",
            {"rel": "alternate", "type": "text/html", "href": release["html_url"]},
        )

        ET.SubElement(entry, "title").text = release["name"]

        content = ET.SubElement(entry, "content", {"type": "html"})

        content.text = release["body_html"]

        entry_author = ET.SubElement(entry, "author")

        ET.SubElement(entry_author, "name").text = "RJ"

    return prettify_xml(feed)


def main():
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()

    releases = response.json()

    grouped = defaultdict(list)

    for release in releases:
        brand = extract_brand(release["tag_name"])
        grouped[brand].append(release)

    for brand, items in grouped.items():
        items.sort(key=lambda r: r["published_at"], reverse=True)

        xml_content = create_feed(brand, items)

        with open(f"{brand}.xml", "w", encoding="utf-8") as f:
            f.write(xml_content)


if __name__ == "__main__":
    main()
