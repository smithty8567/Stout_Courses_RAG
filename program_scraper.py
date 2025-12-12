import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin


def get_soup(url):
    time.sleep(0.4)
    headers = {"USER_AGENT": "UWStoutBulletinCrawler (ML student project; contact: peplinskiM1952@my.uwstout.edu)"}
    r = requests.get(url, headers=headers, timeout=20)
    return BeautifulSoup(r.text, "lxml")


def parse_program(bulletin_url):
    """
    Parse a UW–Stout bulletin program page to extract program details.

    Args:
        bulletin_url (str): URL of the bulletin program page.

    Returns:
        dict: A dictionary containing program name, description, program website,
              and lists of required courses (Separated by Stout Core and Major Studies).
    """
    soup = get_soup(bulletin_url)
    program = {"url": bulletin_url}

    name_tag = soup.select_one("h1#acalog-content")
    if name_tag:
        program_name = name_tag.get_text(strip=True)
    else:
        program_name = "Unknown Program"
    program["program_name"] = program_name

    desc_tag = soup.select_one("div.program_description")
    if desc_tag:
        stripped_descriptions = []
        for description in desc_tag.stripped_strings:
            stripped_descriptions.append(description.strip())
        description = " ".join(stripped_descriptions)
    else:
        description = ""
    program["description"] = description

    link_tag = soup.select_one("a[href*='uwstout.edu/programs/']")
    if link_tag:
        program["program_website"] = link_tag.get("href")
    else:
        program["program_website"] = None

    core_blocks = soup.select("div.acalog-core")

    stout_core_descriptions = []
    major_studies_descriptions = []

    in_stout_core = False
    seen_stout_core = False

    major_start_keywords = [
        "major requirements",
        "major studies",
        "core requirements",
        "program requirements",
        "department requirements",
        "professional requirements",
        "concentrations",
    ]

    for block in core_blocks:
        header = block.select_one("h2, h3, h4, strong, b")
        if header:
            header_description = header.get_text(strip=True)
        else:
            header_description = ""
        header = header_description.lower()

        if "stout core" in header:
            in_stout_core = True
            seen_stout_core = True
            continue

        if in_stout_core:
            for keyword in major_start_keywords:
                if keyword in header:
                    in_stout_core = False
                    break

        course_elements = block.select("li.acalog-course a[onclick*='showCourse']")
        courses = []
        for course_element in course_elements:
            course_name = course_element.get_text(strip=True)
            courses.append(course_name)

        if len(courses) == 0:
            continue

        course_list = ", ".join(courses)
        section_line = f"{header_description}: {course_list}."

        if in_stout_core:
            stout_core_descriptions.append(section_line)
        elif seen_stout_core:
            major_studies_descriptions.append(section_line)
        else:
            major_studies_descriptions.append(section_line)

    if stout_core_descriptions:
        stout_core_section = "Stout Core: " + " ".join(stout_core_descriptions)
    else:
        stout_core_section = ""

    if major_studies_descriptions:
        major_studies_section = "Major Studies: " + " ".join(major_studies_descriptions)
    else:
        major_studies_section = ""

    combined_description = (stout_core_section + " " + major_studies_section).strip()
    program["required_courses"] = combined_description

    return program


def parse_bulletin_concentrations(program_url):
    """
    Parse bulletin subpages for a program to find concentration-specific pages.

    Args:
        program_url (str): The URL of a base bulletin program page.

    Returns:
        list: A list of dictionaries, each containing concentration name,
              description, course sections, and bulletin subpage links.
    """
    soup = get_soup(program_url)

    links = []
    link_tags = soup.select("a[href*='preview_program.php?catoid=']")
    for a in link_tags:
        link_description = a.get_text()
        if "Concentration" in link_description:
            full_url = urljoin(program_url, a["href"])
            links.append(full_url)

    concentrations = []

    for link in links:
        sub_soup = get_soup(link)

        concentration_name_tag = sub_soup.select_one("h1#acalog-content")
        if concentration_name_tag:
            concentration_name = concentration_name_tag.get_text(strip=True)
        else:
            concentration_name = "Unknown Concentration"

        desc_tag = sub_soup.select_one("div.program_description")
        if desc_tag:
            desc_parts = []
            for tag in desc_tag.stripped_strings:
                desc_parts.append(tag.strip())
            desc = " ".join(desc_parts)
        else:
            desc = ""

        course_sections = []
        blocks = sub_soup.select("div.acalog-core")

        for block in blocks:
            header = block.select_one("h2, h3, h4, strong, b")
            if not header:
                continue

            header_description = header.get_text(strip=True)

            course_elements = block.select("li.acalog-course a[onclick*='showCourse']")
            courses = []
            for anchor in course_elements:
                course_name = anchor.get_text(strip=True)
                courses.append(course_name)

            if len(courses) == 0:
                continue

            course_list = ", ".join(courses)
            section_description = f"{header_description}: {course_list}."
            course_sections.append(section_description)

        required = " ".join(course_sections)

        concentration_program = {
            "concentration": concentration_name,
            "bulletin_description": desc,
            "bulletin_courses": required,
            "bulletin_link": link,
        }

        concentrations.append(concentration_program)

    return concentrations


def uwstout_descriptions(program_website, concentrations, base_program_name=None):
    """
    Match bulletin concentrations to their corresponding UW–Stout website pages
    and extract additional descriptions.

    Args:
        program_website (str): Base UW–Stout program website URL.
        concentrations (list): List of concentration dictionaries from bulletin parsing.
        base_program_name (str, optional): The main program’s name for filtering matches.

    Returns:
        list: Updated list of concentration dictionaries, each including a UW–Stout
              site link and an additional description if available.
    """
    if not program_website:
        return concentrations

    program_website = program_website.rstrip("/")

    if "/programs/" not in program_website:
        if "uwstout.edu/" in program_website:
            after_domain = program_website.split("uwstout.edu/", 1)[-1]
            segment = after_domain.split("/")[0].strip("/")
            program_website = f"https://www.uwstout.edu/programs/{segment}"
    else:
        parts = program_website.split("/")
        if len(parts) >= 2 and parts[-2] != "programs":
            program_website = "/".join(parts[:5])

    if base_program_name:
        base_name = base_program_name.lower()
        base_name = re.sub(r"[^a-z0-9 ]", "", base_name)

        for word in ["bs", "ba", "ms", "minor", "major"]:
            base_name = base_name.replace(word, "")
        base_name = base_name.strip()
    else:
        base_name = ""

    soup = get_soup(program_website)

    link_map = {}
    link_tags = soup.select("a[href*='concentration']")

    for anchor in link_tags:
        href = anchor.get("href")
        description = anchor.get_text(" ", strip=True).lower()

        if not href:
            continue

        if href.startswith("/"):
            href = f"https://www.uwstout.edu{href}"
        elif "uwstout.edu" not in href:
            href = urljoin(program_website, href)

        key = re.sub(r"[^a-z0-9\- ]", "", description)
        key = key.replace(" concentration", "")
        key = key.replace("&", "and")
        key = key.strip()

        link_map[key] = href

    if len(link_map) == 0:
        print(f"No concentration links found on {program_website}")
        return concentrations

    print(f"{program_website} — found {len(link_map)} concentration links:")
    for key, value in link_map.items():
        print(f"   {key} : {value}")

    for concentration in concentrations:
        concentration_name = concentration["concentration"].lower()

        concentration_name = re.sub(r"[^a-z0-9 ]", "", concentration_name)
        concentration_name = concentration_name.replace(" concentration", "").strip()
        for word in ["bs", "ba", "ms", "minor", "major"]:
            concentration_name = concentration_name.replace(word, "")
        concentration_name = concentration_name.strip()

        if base_name:
            concentration_name = concentration_name.lower()
            base_lower = base_name.lower()
            if base_lower in concentration_name:
                idx = concentration_name.find(base_lower)
                concentration_name = concentration_name[:idx] + concentration_name[idx + len(base_name):]
                concentration_name = concentration_name.strip()

        matched_url = None
        concentration_name_words = concentration_name.split()

        for key, href in link_map.items():
            all_words_match = True
            for word in concentration_name_words:
                if len(word) > 1 and word not in key:
                    all_words_match = False
                    break
            if all_words_match:
                matched_url = href
                break
            any_word_match = False
            for word in concentration_name_words:
                if word in key:
                    any_word_match = True
                    break
            if any_word_match:
                matched_url = href
                break

        if matched_url is not None:
            print(f"Matched {concentration_name}: {matched_url}")
            sub_soup = get_soup(matched_url)
            paragraphs = []
            for p in sub_soup.select("div.l-content--main p"):
                description = p.get_text(" ", strip=True)
                paragraphs.append(description)
            full_description = " ".join(paragraphs)
            concentration["uwstout_link"] = matched_url
            concentration["uwstout_description"] = full_description
        else:
            concentration["uwstout_link"] = program_website
            concentration["uwstout_description"] = ""

    return concentrations


def scrape_program(bulletin_url):
    """
    Scrapes a single bulletin program page, combining its main description and
    any associated concentrations

    Args:
        bulletin_url (str): URL of the bulletin program page.

    Returns:
        list: List of program or concentration records with names, descriptions,
              and required course data.
    """
    base_program = parse_program(bulletin_url)

    program_name = base_program.get("program_name", "")
    if not program_name:
        program_name = ""

    is_minor = False
    lower_name = program_name.lower()
    if "minor" in lower_name:
        is_minor = True

    if is_minor:
        program_website = base_program.get("program_website")
        if program_website:
            website_soup = get_soup(program_website)
            paragraphs = []
            paragraph_tags = website_soup.select("div.l-content--main p")
            for paragrpah in paragraph_tags:
                description = paragrpah.get_text(" ", strip=True)
                paragraphs.append(description)
            if len(paragraphs) > 0:
                full_description = " ".join(paragraphs)
                base_program["description"] = full_description

    concentrations = parse_bulletin_concentrations(bulletin_url)
    concentrations = uwstout_descriptions(
        base_program.get("program_website"),
        concentrations,
        base_program_name=base_program.get("program_name"),
    )

    records = []

    if len(concentrations) == 0:
        record = {
            "url": base_program["url"],
            "program_name": base_program.get("program_name", ""),
            "concentration": None,
            "description": base_program.get("description", ""),
            "required_courses": base_program.get("required_courses", "")
        }
        records.append(record)
        return records

    for concentration in concentrations:
        full_concentration_name = concentration.get("concentration", "")
        concentration_name = None

        name = full_concentration_name.lower()
        if "concentration" in name:
            open_paren = name.find("(")
            keyword_index = name.find("concentration")

            if open_paren != -1 and open_paren < keyword_index:
                concentration_name = full_concentration_name[open_paren + 1:keyword_index].strip()
            else:
                words = full_concentration_name.split()
                idx = -1
                for i, word in enumerate(words):
                    if word.lower() == "concentration":
                        idx = i
                        break

                if idx > 0:
                    concentration_name = " ".join(words[:idx]).strip()
                elif idx + 1 < len(words):
                    concentration_name = " ".join(words[idx + 1:]).replace("in", "", 1).strip()

        uwstout_desc = concentration.get("uwstout_description")
        bulletin_desc = concentration.get("bulletin_description")
        base_description = base_program.get("description", "")

        if uwstout_desc:
            description = uwstout_desc
        elif bulletin_desc:
            description = bulletin_desc
        else:
            description = base_description

        merged_courses = base_program.get("required_courses", "")
        concentration_courses = concentration.get("bulletin_courses")

        if concentration_courses:
            merged_courses = merged_courses + " Additional concentration courses: " + concentration_courses

        record = {
            "url": concentration.get("bulletin_link", base_program["url"]),
            "program_name": base_program.get("program_name", ""),
            "concentration": concentration_name,
            "description": description,
            "required_courses": merged_courses
        }
        records.append(record)

    return records


def scrape_all_programs(bulletin_main_url, out_file="programs.json"):
    """
    Scrapes all UW–Stout bulletin program pages linked from the starting page.
    (This includes program pages that need to get cleaned later such as Stout Core or Honors College)

    Args:
        bulletin_main_url (str): The bulletin index URL containing all program links.
        out_file (str): Name of the output JSON file for saving results.

    Returns:
        None
    """
    soup = get_soup(bulletin_main_url)

    program_links = []
    link_tags = soup.select("a[href*='preview_program.php?catoid=']")
    for anchor in link_tags:
        href = anchor.get("href")
        if "poid=" in href:
            full_url = urljoin("https://bulletin.uwstout.edu", href)
            program_links.append(full_url)

    print(f"Found {len(program_links)} program pages.")

    all_program = []

    total_programs = len(program_links)
    for i, link in enumerate(program_links, start=1):
        print(f"\n[{i}/{total_programs}] Scraping program: {link}")
        program_records = scrape_program(link)
        for record in program_records:
            all_program.append(record)
        time.sleep(0.3)

    with open(out_file, "w", encoding="utf-8") as file:
        json.dump(all_program, file, indent=2, ensure_ascii=False)

    print(f"\nScrape completed to {out_file}")


if __name__ == "__main__":
    start_url = "https://bulletin.uwstout.edu/content.php?catoid=29&navoid=773&print"
    scrape_all_programs(start_url)
