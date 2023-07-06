from time import strftime
import re
from typing import Optional
import mwparserfromhell
import pywikibot as pwb
from pywikibot.textlib import Section

### configuration ###
ARCHIVE_TEMPLATES = [ 'deleted', 'not deleted', 'merged', 'done', 'not done', 'notdone' ]
CURRENT_RFD_PAGE = 'Wikidata:Requests for deletions'
ARCHIVE_PAGE = f'Wikidata:Requests for deletions/Archive/{strftime("%Y/%m/%d")}'


def eval_body_parts(body:list[Section]) -> tuple[list[Section], list[Section]]:
    part_headline = re.compile(r'^==[^=]') # second-level headline

    kept_parts = []
    archived_parts = []
    for i, part in enumerate(body, start=1):
        keep = True
        wrong_part_level = False
        has_child_parts = False

        # always keep parts that are not second-level headlines (i.e. not "== part ==")
        if part_headline.search(part.title) is None:
            wrong_part_level = True

        # always keep parts that have child parts (i.e. with third-level parts as childs)
        if i < len(body):
            if part_headline.search(part.title) is not None and body[i].title[:3]=='===':
                has_child_parts = True

        # check whether one of the archive_templates is found in the part
        for template in mwparserfromhell.parse(part.content).filter_templates():
            if template.name.lower() in ARCHIVE_TEMPLATES:
                keep = False
                break

        if keep is True or wrong_part_level is True or has_child_parts is True:
            kept_parts.append(part)
        else:
            archived_parts.append(part)

    return kept_parts, archived_parts


def new_rfd_text(header:str, footer:str, parts:list[Section]) -> str:
    wikitext = header
    for part in parts:
        wikitext += part.title
        wikitext += part.content
    wikitext += footer

    return wikitext


def new_rfd_archive_text(archive:pwb.Page, parts:list[Section]) -> str:
    if archive.exists() is False:
        wikitext = '{{Archive|category=Archived requests for deletion}}\n\n'
    else:
        wikitext = archive.text + '\n\n'

    for part in parts:
        wikitext += part.title
        wikitext += part.content

    return wikitext


def print_log(page:pwb.page.BasePage, err:Optional[Exception]):
    if err is None:
        print(f'Made edit to page "{page.title()}"')
    else:
        print(f'An exception occurred while saving page "{page.title()}": {err}')


def print_output(body:list[Section], kept_parts:list[Section], \
                 archived_parts:list[Section], archive_exists:bool) -> None:
    print(f'== {strftime("%Y-%m-%d, %H:%M:%S")} ==')
    print(f'Archive: "{ARCHIVE_PAGE}"')
    print(f'Templates that trigger archiving: {", ".join(ARCHIVE_TEMPLATES)}\n')

    print(f'Total parts: {len(body)}')
    print(f'Kept parts: {len(kept_parts)}')
    print(f'Archived parts: {len(archived_parts)}\n')

    if archive_exists is False:
        print(f'Created new archive page "{ARCHIVE_PAGE}"\n')


def main() -> None:
    ### basic variables ###
    site = pwb.Site('wikidata', 'wikidata')
    site.login()

    ### actual processing ###
    rfd = pwb.Page(site, CURRENT_RFD_PAGE)
    rfd_archive = pwb.Page(site, ARCHIVE_PAGE)

    sections = pwb.textlib.extract_sections(rfd.get(), site)
    header:str = sections[0]
    body:list[Section] = sections[1] # list of namedtuples
    footer:str = sections[2]

    kept_parts, archived_parts = eval_body_parts(body)

    rfd.text = new_rfd_text(header, footer, kept_parts)
    rfd_archive.text = new_rfd_archive_text(rfd_archive, archived_parts)

    ### some output ###
    print_output(body, kept_parts, archived_parts, rfd_archive.exists())

    ### save or show changes ###
    if len(archived_parts) == 0:
        print('Nothing to do.')
        return

    rfd_archive.save(
        summary=f'Archived {len(archived_parts)} sections from [[{CURRENT_RFD_PAGE}]] #msynbotTask6',
        minor=False,
        quiet=True,
        callback=print_log
    )
    rfd.save(
        summary=f'Archive {len(archived_parts)} sections to [[{ARCHIVE_PAGE}]] #msynbotTask6',
        minor=False,
        quiet=True,
        callback=print_log
    )


if __name__=='__main__':
    main()
