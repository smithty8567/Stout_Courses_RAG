import scrapy as sc
import re


class ProgramSpider(sc.Spider):
    name = "BulletinScanner"
    allowed_domains = ["bulletin.uwstout.edu"]
    start_urls = ["https://bulletin.uwstout.edu/content.php?catoid=29&navoid=773"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "USER_AGENT": "UWStoutBulletinCrawler (ML student project; contact: peplinskiM1952@my.uwstout.edu)"
    }

    def parse(self, response):
        program_links = response.css('a[href*="preview_program.php"]::attr(href)').getall()
        self.log(f"Found {len(program_links)} program links")
        for href in program_links:
            href = href + "&print"
            yield response.follow(href, callback=self.parse_program)

    def extract_required_courses(self, response):
        """
        Extract grouped course listings by section header.
        Looks at all .acalog-core blocks and only keeps ones that
        actually contain li.acalog-course with showCourse links.
        """
        blocks = response.css("div.acalog-core")

        sections = []
        for block in blocks:
            header = block.css("h2::text, h3::text, h4::text, h5::text, strong::text, b::text").get()
            if not header:
                continue

            header = header.strip()
            if any(k in header.lower() for k in [
                "footer", "help", "contact", "apply", "uw-stout",
                "breadcrumb", "bachelor degree requirements"
            ]):
                continue

            if len(header.split()) > 12:
                continue

            course_texts = block.css("li.acalog-course a[onclick*='showCourse']::text").getall()
            course_texts = [c.strip() for c in course_texts if c.strip()]

            if not course_texts:
                continue

            seen = set()
            unique_courses = []
            for c in course_texts:
                norm = re.sub(r"\s+", " ", c.lower())
                if norm not in seen:
                    seen.add(norm)
                    unique_courses.append(c)

            if unique_courses:
                courses_str = ", ".join(unique_courses)
                sections.append(f"{header}: {courses_str}.")

        return " ".join(sections)

    def parse_program(self, response):
        program_title = response.css("h1#acalog-content::text").get()
        program_title = program_title.strip() if program_title else "No Title"

        text_parts = response.css("div.program_description *::text").getall()
        program_text = " ".join(t.strip() for t in text_parts if t.strip())

        required_courses_sentence = self.extract_required_courses(response)

        concentration_links = response.css(
            'a[href*="preview_program.php"][onclick*="Concentration"]::attr(href)'
        ).getall()

        if concentration_links:
            for href in concentration_links:
                href = href + "&print"
                yield response.follow(
                    href,
                    callback=self.parse_concentration,
                    meta={
                        "program_name": program_title,
                        "parent_text": program_text,
                        "parent_courses": required_courses_sentence,
                    },
                )
            return

        yield {
            "url": response.url,
            "program_name": program_title,
            "concentration": None,
            "text": program_text,
            "required_courses": required_courses_sentence,
        }

    def parse_concentration(self, response):
        base_program = response.meta.get("program_name")
        parent_text = response.meta.get("parent_text", "")
        parent_courses = response.meta.get("parent_courses", "")

        concentration_name = response.css("h1#acalog-content::text").get()
        concentration_name = concentration_name.strip() if concentration_name else "Unknown Concentration"

        text_parts = response.css("div.program_description *::text").getall()
        concentration_text = " ".join(t.strip() for t in text_parts if t.strip()) or parent_text

        concentration_courses = self.extract_required_courses(response)

        if parent_courses and concentration_courses:
            combined_courses = f"{parent_courses.strip()} Additional concentration courses: {concentration_courses.strip()}"
        elif parent_courses:
            combined_courses = parent_courses.strip()
        else:
            combined_courses = concentration_courses.strip()

        yield {
            "url": response.url,
            "program_name": base_program,
            "concentration": concentration_name,
            "text": concentration_text,
            "required_courses": combined_courses,
        }
