#!/usr/bin/env python3
from orger import Mirror
from orger.inorganic import node, link, docview_link, literal
from orger.common import dt_heading, error

from datetime import datetime

# parse epub to generate link for nov.el
from ebooklib import epub

class KoreaderView(Mirror):
    def get_items(self) -> Mirror.Results:
        import my.koreader as koreader

        for book in sorted(
                koreader.annotated_books(),
                key=lambda p: datetime.min if isinstance(p, Exception) or p.created is None else p.created.replace(tzinfo=None),
        ):
            if isinstance(book, Exception):
                yield error(book)
                continue

            def chit(book: koreader.Book):
                for a in book.annotations:
                    parts = []
                    highlight = ''
                    pos0, pos0_dict, pos1, pos1_dict = a.pos0, a.pos0_dict, a.pos1, a.pos1_dict
                    if isinstance(a, koreader.Annotation):
                        highlight = (a.notes or '').strip()

                    elif isinstance(a, koreader.Highlight):
                        highlight = (a.text or '').strip()

                    # author    = (a.author    or '').strip()
                    # comment   = (a.comment   or '').strip()
                    if highlight:
                        parts.append(literal(highlight))
                    # if author:
                    #     parts.append(f'by {author}')
                    # if comment:
                    #     parts.append(comment)
                    body = '\n'.join(parts)

                    # TODO: txt 파일에 대한 링크도 준비. TXT 파일의 경우 char
                    # point인것 같은데, org의 링크는 라인넘버만 지원한다.

                    page_link = None
                    if pos0_dict:
                        page1 = pos0_dict['page'] + 1
                        # TODO Use position for dockview or pdf-tools
                        page_link = docview_link(path=book.path, title=f'page {page1}', page1=page1)
                    else:
                        # TODO: Kindle 포맷 지원?
                        # TODO Link: https://github.com/wasamasa/nov.el/blob/master/nov.el#L837
                        # nov.el uses character point for position
                        # python으로 만들 때는 epub를 직접 파싱해서 불러들여야 할 것으로 보임.
                        page_link = link(url=book.path, title=f'{book.title}')

                    yield node(
                         dt_heading(a.created, page_link),
                        body=body,
                    )

            book_link = docview_link(path=book.path, title=book.title)  # todo would be nice to extract metadata for title
            yield node(
                dt_heading(book.created, book_link),
                children=list(chit(book))
            )


if __name__ == '__main__':
    # import logging
    # from orger.common import setup_logger
    # setup_logger(koreader.logger, level=logging.DEBUG)
    KoreaderView.main()
