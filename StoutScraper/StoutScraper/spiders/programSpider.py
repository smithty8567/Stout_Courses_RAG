import scrapy as sc

class ProgramSpider(sc.Spider):
    name = "BulletinScanner"
    allowed_domains = ["bulletin.uwstout.edu"]
    start_urls = ["https://bulletin.uwstout.edu/content.php?catoid=29&navoid=773"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "USER_AGENT": "UWStoutBulletinCrawler (ML student project; contact: peplinskiM1952@my.uwstout.edu)"
    }

    def parse(self, response):
        # find all links that lead to a program page
        program_links = response.css('a[href*="preview_program.php"]::attr(href)').getall()

        self.log(f"Found {len(program_links)} program links")
        for href in program_links[:5]:
            self.log(f"Example link: {href}")
        # follow each link
        for href in program_links:
            href = href+"&print"
            yield response.follow(href, callback=self.parse_program)

    def parse_program(self, response):
        self.log(f"Visiting program page: {response.url}")
        program_title = response.css("h1#acalog-content::text").get()
        program_title = program_title.strip() if program_title else "No Title"

        concentration_links = response.css(
            'a[href*="preview_program.php"][onclick*="Concentration"]::attr(href)'
        ).getall()

        text_parts = response.css("div.program_description *::text").getall()
        program_text = " ".join(t.strip() for t in text_parts if t.strip())

        if concentration_links:
            for href in concentration_links:
                href = href+"&print"
                yield response.follow(
                    href,
                    callback=self.parse_concentration,
                    meta={"program_name": program_title,
                          "program_text": program_text},
                )
            return

        yield {
            "url": response.url,
            "program_name": program_title,
            "concentration": None,
            "text": program_text,
        }

    def parse_concentration(self, response):
        base_program = response.meta.get("program_name")

        concentration_name = response.css("h1#acalog-content::text").get()
        concentration_name = concentration_name.strip() if concentration_name else "Unknown Concentration"

        text_parts = response.css("div.program_description *::text").getall()
        concentration_text = " ".join(t.strip() for t in text_parts if t.strip())

        if not concentration_text:
            concentration_text = response.meta.get("parent_text", "")

        yield {
            "url": response.url,
            "program_name": base_program,
            "concentration": concentration_name,
            "text": concentration_text,
        }