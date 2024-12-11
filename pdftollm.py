#!/usr/bin/env python3

import os
import re
from os import listdir
from os.path import isfile, join
import pdfplumber
import config
import argparse
from collections import defaultdict
from PIL import Image
from PIL.PngImagePlugin import PngInfo 

# Load settings from configuration file.
cfg = config.Config('pdftollm.cfg')
REF_DOCS_PATH = cfg['reference_docs_path']
EXTRACTED_CHUNKS_PATH = cfg['extracted_chunks_path']
EXTRACTED_IMAGES_PATH = cfg['extracted_images_path']
IMAGES_RESOLUTION = cfg['images_resolution']
SOURCE_TAG = cfg['source_tag']
QUOTE_TAG = cfg['quote_tag']
DROP_WORDS = cfg['drop_words']
PARAGRAPH_TAG = 'paragraph'
PARAGRAPH_BORDER = '----paragraph_border----'
PAGE_HEADER_END = 'page_header_end'
PAGE_NUMBER_TAG = 'page_number'  # page number
END_OF_PAGE_TAG = 'end_of_page'
DOCUMENT = 'document'
PAGE_SEPARATOR = '<------------------page_separator-------------------->'
SENTENCE_SEPARATOR = '. ' 
STAB = 'blabla'
CROP_TXT = cfg['crop_txt']

def find_max_integer_key(dictionary):
    max_value = max(dictionary.values())
    for key, value in dictionary.items():
        if value == max_value:
            return key


def count_phrase_frequency(text, page_counter, print_top_n=-1):
    #print_top_n = 30
    t = re.sub(r'\n+', '\n', text)
    t = re.sub(r'_{1,}', ' ', t)
    t = re.sub(r'\…{1,}', ' ', t)
    t = re.sub(r'\.{2,}', '. ', t)
    t = re.sub(r'\s+', ' ', t)

    sentences = t.split(SENTENCE_SEPARATOR)
    #print('page_counter:', page_counter)
    #print('len(sentences):', len(sentences))
    #print('\n\n'.join(sentences))
    phrase_counts = defaultdict(lambda: 0)

    for sentence in sentences:
        words = sentence.split()
        for i in range(len(words)):
            for j in range(i + 1, len(words) + 1):
                phrase = ' '.join(words[i:j])
                phrase_counts[phrase] += 1

    ph = {}
    for phrase, count in phrase_counts.items():
        #if (count > (page_counter - 7)) and (count < (page_counter + 5)):
        if (count > (page_counter/2)) and (count < (page_counter + 5)):
        #if (count > 0):
            words = phrase.split(' ')
            if words[0][0].isupper():
                upper = 1.5
            else:
                upper = 1
            score = len(words) * count * upper
            ph[phrase] = score
    if len(ph) > 0:
        doc_name = find_max_integer_key(ph)
        if print_top_n > 0:
            for phrase, count in sorted(ph.items(), key=lambda item: item[1],
                                        reverse=True)[:print_top_n]:
                print(f'score: {count}  phrase: "{phrase}"')
    else:
        doc_name = 'not found'
    return doc_name


def replace_drop_words_by_stab(txt: str, drop_words_list: list[str], stab: str = STAB) -> str:
    for word in drop_words_list:
        if 'r"' in word:
            word = word.replace('r"', '"')
            word = word.replace('"', '')
            # Создаем регулярное выражение для поиска
            pattern = rf"{word}"
            # Заменяем все вхождения
            txt = re.sub(pattern, ' ', txt)
        else:
            txt = txt.replace(word, stab)
    return txt


def replace_underscore_lines_with_linebreaks(text):
    l_text = text.split('\n')
    res = []
    for t in l_text:
        new_text = re.sub(r'^_{2,}', " ", t)

        res.append(new_text)
    l_text = res
    empty_count = 0
    res = []
    for t in l_text:
        new_text = re.sub(r'_{2,}', ' ', t)
        if f'<{PARAGRAPH_BORDER}>' in new_text or new_text == '':
            empty_count += 1
        else:
            empty_count = 0
        if empty_count < 2:
            res.append(new_text)

    return '\n'.join(res)


def replace_space_lines_with_linebreaks(text):
    l_text = text.split('\n')
    res = []
    for t in l_text:
        new_text = re.sub(r'^\s*$', "", t)

        res.append(new_text)
    l_text = res
    empty_count = 0
    res = []
    for t in l_text:
        new_text = re.sub(r'\s+', ' ', t)
        if f'<{PARAGRAPH_BORDER}>' in new_text or new_text == '':
            empty_count += 1
        else:
            empty_count = 0
        if empty_count < 2:
            res.append(new_text)

    return '\n'.join(res)


def set_paragraph_borders(text):
    l_text = text.split('\n\n')
    res = f'<{PARAGRAPH_BORDER}>'.join(l_text)
    return res


def mark_chunks_on_page(text: str, source_name: str = '') -> str:
    header = "header not defined"
    parts = text.split(f"<{PAGE_HEADER_END}>")
    if len(parts) < 2:
        page_body = parts[0]
    else:
        if source_name == '':
            header = parts[0].strip()
            header = header.replace(f'<{PARAGRAPH_BORDER}>', ' ')
            header = re.sub(r'\x20+', ' ', header)
        else:
            header = source_name
        page_body = parts[1]    
    temp = re.sub(r'\x20+\n', '\n', page_body)
    temp = re.sub(r'\n\n+', f'<{PARAGRAPH_BORDER}>\n', temp)
    page_body = re.sub(r'\x20+', ' ', temp)

    page = "page not defined"

    pattern = rf'<{PAGE_NUMBER_TAG} (-?\d+)>'
    if len(page_body) > 0:
        match = re.search(pattern, page_body)
        if match:
            page = f"страница {match.group(1)}"
        l_text = page_body.split(f'<{PAGE_NUMBER_TAG}>')
        l_text = l_text[0].split(f'<{PARAGRAPH_BORDER}>')
    else:
        l_text = ["No textual data"]     
    src = header
    src = src.replace('\n', ' ')
    src = src.replace('  ', ' ')
    src = src.replace('  ', ' ')
    page = page.replace('\n', ' ')
    page = page.replace('  ', ' ')
    page = page.replace('  ', ' ')

    res = []
    for t in l_text:
        t = t.strip()
        if len(t) == 0:
            continue
        new_text = (
                    f"\n<{PARAGRAPH_TAG}>\n<{SOURCE_TAG}>\n{src}\n{page}\n"
                    f"</{SOURCE_TAG}>\n<{QUOTE_TAG}>\n{t}\n</{QUOTE_TAG}>"
                    f"\n</{PARAGRAPH_TAG}>\n"
                   )
        pattern = rf'<{PAGE_NUMBER_TAG} (-?\d+)>'
        new_text = re.sub(pattern, "", new_text) 
        new_text = new_text.replace(f'<{END_OF_PAGE_TAG}>', '')
        new_text = new_text.replace('  ', ' ')
        res.append(new_text)
    res = ''.join(res)
    return res


def smart_mark_page_numbers(text):
    pattern = r'Страница (\d+) из (\d+)'
    replacement = rf'\n<{PAGE_NUMBER_TAG} \1>\n<{END_OF_PAGE_TAG}>'
    res = re.sub(pattern, replacement, text)
    return res


def simple_mark_page_numbers(text, page_number: int):
    pattern = r'Страница (\d+) из (\d+)'
    replacement = ""
    res = re.sub(pattern, replacement, text)
    addon = f'\n<{PAGE_NUMBER_TAG} {page_number}>\n<{END_OF_PAGE_TAG}>'
    res = f'{res}{addon}'
    return res


def mark_page_headers(text, pattern: str = r'(.+\.\.\.\s)'):
    replacement = rf'\1\n<{PAGE_HEADER_END}>'
    res = re.sub(pattern, replacement, text)
    return res


def mark_page_headers_2(text, patt, words_limit=20):
    p = patt.split(' ')
    # Если в паттерне много слов, то обработка затянется. Нам это не нужно.
    words_limit = 20
    if len(p) > words_limit:
        p = p[0:words_limit]
    m = '\\n*\\s*\\n*\\s*'.join(p)
    pattern = re.compile(f'(\\n*\\s*\\n*\\s*{m})')
    replacement = rf'{patt}\n<{PAGE_HEADER_END}>'
    res = re.sub(pattern, replacement, text)
    return res


def snap_y(page_height, yin):
    y = page_height - yin
    y = max(0, y)
    y = int(min(page_height, y))
    return y


def snap_x(page_width, xin):
    x = min(xin, page_width)
    x = int(max(0, x))
    return x


def bbox_inside(box1: tuple, box2: tuple):
    """ Is b0x2 inside box1? """
    res = (box1[0] <= box2[0]) and (box1[1] <= box2[1]) \
        and (box1[2] >= box2[2]) and (box1[3] >= box2[3])
    return res


def bbox_area(box: tuple):
    """ Is b0x2 area calculation  (x0, y1, x1, y0). """
    res = abs((box[2] - box[0])*(box[1] - box[3]))
    return res


def cropped_text_of_page(page, list_of_bboxes) -> str:
    cropped_text = ''
    for obj in page.chars:
        txt = obj['text']
        y1 = obj['y1']
        y0 = obj['y0']
        x0 = obj['x0']
        x1 = obj['x1']
        txt_bbox = (x0, y1, x1, y0)
        add_char = True
        for ex in list_of_bboxes:
            if bbox_inside(ex, txt_bbox):
                add_char = False
                break
        if add_char is True:
            cropped_text = f"{cropped_text}{txt}"
    cropped_text = replace_drop_words_by_stab(cropped_text, DROP_WORDS, "")
    return cropped_text


class PdfCrawler():
    def __init__(self, filename: str) -> None:
        self.DESC_KEY = "Description"
        self.BBOX_KEY = "Bbox"
        self.docfile_key = "DocFile"
        self.imagefile_key = "ImageFile"
        self.parent_imagefile_key = "ParentImageFile"
        self.page_key = "Page"
        self.image_index_key = "ImageIndex"
        self.image_was_saved_key = "image_was_saved_key"
        # List of boundary boxes on current page for text removing.
        self.bboxes_to_exclude = []
        self.table_strategy = {
            #  "vertical_strategy": "text",
            #  "vertical_strategy": "explicit",
            #  "horizontal_strategy": "explicit"
        }
        self.table_counter = 0
        self.page_was_saved = False
        self.page_counter = 0
        self.image_counter = 0
        self.table_counter = 0
        self.complete_text = ''
        self.filename = filename
        self.page_image_bboxes = []
        #if not self.filename.endswith(".pdf"):
        #    return -1
        self.doc_original_filename = ''
        self.base_filename = ''
        self.page_image_filename = ''
        self.page_image_filename_base = ''
        self.image_was_saved = False
        self.page_image_bbox = ()

    def save_tables(self, page) -> int:
        t = page.find_tables(table_settings=self.table_strategy)
        if len(t) > 0:
            table_was_saved = False
            for i in t:
                table_meta = PngInfo()
                table_bbox = i.bbox
                table_filename = (f'{self.page_image_filename_base}'
                                  f'_t{self.table_counter}.png')
                self.table_counter += 1
                bbox = page.bbox
                if not bbox_inside(bbox, table_bbox):
                    table_bbox = bbox
                if bbox_area(table_bbox) > 0:     
                    cropped_page = page.crop(table_bbox)
                    image_obj = cropped_page.to_image(resolution=IMAGES_RESOLUTION)
                    image_obj.save(table_filename)
                    self.bboxes_to_exclude.append(table_bbox)
                    table_was_saved = True
                if table_was_saved:
                    table_meta.add_text(self.BBOX_KEY, str(table_bbox))
                    table_meta.add_text(self.page_key, str(self.page_counter))
                    img = Image.open(table_filename)
                    img.save(table_filename, pnginfo=table_meta)

            tables = page.extract_tables(table_settings=self.table_strategy)
            for e in tables:
                table_md = '|'
                line = '|'
                for c, row in enumerate(e):
                    for cell in row:
                        s = str(cell)
                        s = s.replace("\n", " ")
                        table_md = f'{table_md} {s} |'
                        line = f'{line}---|'
                    if c == 0:
                        table_md = f'{table_md}\n{line}'
                    table_md = f'{table_md}\n'
            print(f'<table {self.table_counter}>')
            print(table_md)
            print('</table>')
        return len(t)
    
    def save_image_of_whole_page(self, page) -> int:
        self.page_was_saved = False
        self.page_image_filename_base = (f'{EXTRACTED_IMAGES_PATH}/'
                                         f'{self.base_filename}_image'
                                         f'_p{self.page_counter}')
        self.page_image_filename = (f'{self.page_image_filename_base}.png')
        self.page_image_bbox = (0, page.height, page.width, 0)
        image_obj = page.to_image(resolution=IMAGES_RESOLUTION)
        image_obj.save(self.page_image_filename)
        self.page_was_saved = True
    

    def save_images(self, page) -> int:
        for image in page.images:
            self.image_filename = (f'{self.page_image_filename_base}'
                              f'_i{self.image_counter}.png')
            y1 = snap_y(page.height, image['y1'])
            y0 = snap_y(page.height, image['y0'])

            x0 = snap_x(page.width, image['x0'])
            x1 = snap_x(page.width, image['x1'])

            image_bbox = (x0, y1, x1, y0)
            state_dict = {
                            self.imagefile_key: self.image_filename,
                            self.BBOX_KEY: image_bbox,
                            self.DESC_KEY: "",
                            self.page_key: self.page_counter,
                            self.docfile_key: self.doc_original_filename,
                            self.parent_imagefile_key: os.path.basename(self.page_image_filename),
                            self.image_index_key: self.image_counter,
                            self.image_was_saved_key: False
                         }
            print(f"\n<{self.image_filename}>: (x0, y1, x1, y0): "
                  f"{image_bbox}")
            bbox = page.bbox
            if not bbox_inside(bbox, image_bbox):
                image_bbox = bbox
            if bbox_area(image_bbox) > 0:     
                cropped_page = page.crop(image_bbox)
                image_obj = cropped_page.to_image(resolution=IMAGES_RESOLUTION)
                image_obj.save(self.image_filename)
                state_dict[self.image_was_saved] = True
                self.bboxes_to_exclude.append(image_bbox)

            self.page_image_bboxes.append(state_dict)
            self.image_counter += 1

    def scan_text_over_images(self, page):
        for obj in page.chars:
            txt = obj['text']
            y1 = snap_y(page.height, obj['y1'])
            y0 = snap_y(page.height, obj['y0'])

            x0 = snap_x(page.width, obj['x0'])
            x1 = snap_x(page.width, obj['x1'])
            txt_bbox = (x0, y1, x1, y0)
            #print(f"\n<{txt}>: (x0, y1, x1, y0): {txt_bbox}")
            for d in self.page_image_bboxes:
                if bbox_inside(d[self.BBOX_KEY], txt_bbox):
                    d[self.DESC_KEY] = f"{d[self.DESC_KEY]}{txt}"

    def append_text_to_clip_images(self):
        for d in self.page_image_bboxes:
            meta = PngInfo()

            if len(d[self.DESC_KEY]) > 0:
                meta.add_text(self.DESC_KEY, d[self.DESC_KEY])
            else:
                meta.add_text(self.DESC_KEY, "None")
            meta.add_text(self.BBOX_KEY, str(d[self.BBOX_KEY]))
            meta.add_text(self.page_key, str(d[self.page_key]))
            meta.add_text(self.imagefile_key, os.path.basename(d[self.imagefile_key]))
            meta.add_text(self.parent_imagefile_key, d[self.parent_imagefile_key])
            meta.add_text(self.image_index_key, str(d[self.image_index_key]))
            meta.add_text(self.docfile_key, d[self.docfile_key])
            if d[self.image_was_saved_key]:
                img = Image.open(d[self.imagefile_key])
                img.save(d[self.imagefile_key], pnginfo=meta)
    
    def append_text_to_page_image(self, page) -> str:
         # if CROP_TXT is True:
        if CROP_TXT is not True:
            txt = cropped_text_of_page(page, self.bboxes_to_exclude)
        else:
            txt = page.extract_text(layout=True)
            txt = replace_drop_words_by_stab(txt, DROP_WORDS, "")

        meta = PngInfo()
        if len(txt) > 0:
            clean = re.sub(r'\s+', ' ', txt).strip()
            meta.add_text(self.DESC_KEY, clean)
        else:
            meta.add_text(self.DESC_KEY, "None")

        meta.add_text(self.BBOX_KEY, str(self.page_image_bbox))
        meta.add_text(self.page_key, str(self.page_counter))
        meta.add_text(self.imagefile_key, os.path.basename(self.page_image_filename))
        meta.add_text(self.docfile_key, self.doc_original_filename)
        meta.add_text(self.parent_imagefile_key, "self")
        meta.add_text(self.image_index_key, "-1")
        if self.page_was_saved:
            img = Image.open(self.page_image_filename)
            img.save(self.page_image_filename, pnginfo=meta)
        return txt

    def build_flat_txt_doc(self,
                           page_separator: str = '\n\n') -> int:
        self.complete_text = ''
        self.doc_original_filename = os.path.basename(self.filename)
        self.base_filename = self.doc_original_filename.replace(".pdf", "")
        with pdfplumber.open(self.filename) as pdf:
            for page in pdf.pages:
                self.bboxes_to_exclude = []
                
                self.save_image_of_whole_page(page)

                self.image_was_saved = False
                if len(page.images) > 0:
                    self.save_images(page)
                self.scan_text_over_images(page)
                self.append_text_to_clip_images() 
                print(self.page_image_bboxes)
                tables_on_page = self.save_tables(page)
                print(f'page: {self.page_counter} tables: {tables_on_page}')
                txt = self.append_text_to_page_image(page)
                txt = f'{txt}{page_separator}'
                self.complete_text = f'{self.complete_text}{txt}'

                self.page_counter += 1
        return self.complete_text, self.page_counter, self.table_counter, self.image_counter


def get_page_numbers_list(filename: str) -> list[int]:
    if not filename.endswith(".pdf"):
        raise ValueError(f'Not a pdf file: {filename}')
    with pdfplumber.open(filename) as pdf:
        pages = pdf.pages
        WORST_RATE = -1E7
        top_rate = (0, WORST_RATE - 1)
        PAGE_COUNT = len(pages)
        score_list = []
        for n in range(-PAGE_COUNT, PAGE_COUNT + 1):
            score = 0
            p = n
            for _, page in enumerate(pages):
                page_txt = page.extract_text(layout=True)
                if f'{p}' in page_txt:
                    score += 1
                else:
                    score -= 1
                p += 1
            if score > 0:
                rate = (n, round(score/PAGE_COUNT, 3))
                if rate[1] > top_rate[1]:
                    top_rate = rate
                score_list.append(rate)

    print(f"Page_count: {PAGE_COUNT}")
    if top_rate[1] < WORST_RATE:
        print('Beginning page not found.')
        begining_page = None                
    else:
        begining_page = top_rate[0]                
    print(f'Beginig_page_number: {begining_page}')
    return begining_page


def build_single_txt_doc(filename: str, mode: str = '',
                         page_separator: str = '\n\n') -> int:
    if not filename.endswith(".pdf"):
        raise ValueError(f'Not a pdf file: {filename}')
    print(f"\nInput document file: {filename}")
    page_counter = 0
    pc = PdfCrawler(filename)
    complete_text, page_counter, table_counter, image_counter \
        = pc.build_flat_txt_doc(SENTENCE_SEPARATOR)
    print(f'Symbols in document: {len(complete_text)}')
    print(f'Page_counter: {page_counter}')
    print(f'Image_counter: {image_counter}')
    print(f'Table_counter: {table_counter}')
    doc_name = count_phrase_frequency(complete_text, page_counter)

    complete_text = ''
    source_name = ''
    output_filename = filename.replace(".pdf", ".txt")

    base_filename = os.path.basename(filename).replace(".pdf", ".txt")
    output_filename = f"{EXTRACTED_CHUNKS_PATH}/{base_filename}"
    print(f'Output document name: <{output_filename}>')

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f"<{DOCUMENT}>\n{filename}\n</{DOCUMENT}>\n")
    print(f'Input document name from page headers: <{doc_name}>')
    current_page = get_page_numbers_list(filename)
    with pdfplumber.open(filename) as pdf:
        pages = pdf.pages
        local_page_counter = 0
        for index, page in enumerate(pages):
            txt = page.extract_text(layout=True)

            if mode == 'flat':
                txt = replace_drop_words_by_stab(txt, DROP_WORDS, "")
            else:
                txt = replace_drop_words_by_stab(txt, DROP_WORDS)
                if index == 0:
                    txt = re.sub(r'\s+', ' ', txt)
                    source_name = txt.replace(STAB, ' ')
                    source_name = re.sub(r'_{2,}', ' ', source_name)
                    txt = f'{doc_name}\n<{PAGE_HEADER_END}>\n{txt}\nСтраница 0 из 0\n'
                txt = replace_space_lines_with_linebreaks(txt)
                txt = txt.replace(STAB, ' ')
                if current_page is None:
                    txt = smart_mark_page_numbers(txt)
                else:
                    txt = simple_mark_page_numbers(txt, current_page)
                    current_page += 1
                txt = mark_page_headers_2(txt, doc_name)
                txt = set_paragraph_borders(txt)
                txt = mark_chunks_on_page(txt, source_name)
            txt = f'{txt}\n{page_separator}'
            complete_text = f'{complete_text}{txt}'
            local_page_counter += 1
            page_counter += 1
            with open(output_filename, "a", encoding="utf-8") as f:
                f.write(f"\n{txt}\n")
        print(f"{local_page_counter} pages found.")
    return complete_text, page_counter


def build_txt(mode: str = '', page_separator: str = '') -> int:
    files = [f for f in listdir(REF_DOCS_PATH) if isfile(join(REF_DOCS_PATH, f))]
    c = 0
    for path in files:
        if path.endswith(".pdf"):
            c += 1
    print(f"{c} pdf files found.")
    for path in files:
        relative_path = REF_DOCS_PATH + '/' + path
        filename = os.path.abspath(relative_path)
        extentions = filename.split(".")

        # Игнорируем не pdf-файлы.
        if extentions[-1] != "pdf":
            continue
        if page_separator == '':
            build_single_txt_doc(filename, mode)
        else:
            build_single_txt_doc(filename, mode, page_separator)


def parse_args():
    """CLI options parsing."""

    prog_name = os.path.basename(__file__).split(".")[0]

    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="Converter pbf to txt.",
        epilog="Text at the bottom of help",
    )
    parser.add_argument("-c", dest="config_file", help="Configuration"
                        " file path.")
    parser.add_argument("-m", dest="output_mode", help="Outputs data format."
                        " If set 'flat' the out data will be as is.")
    parser.add_argument("-i", dest="input_file_path", help="Input"
                        " pdf-file path.")
    parser.add_argument("-f", dest="frequency",
                        action=argparse.BooleanOptionalAction,
                        help="Prints frequency of words in input"
                        " pdf-file.")
    return parser.parse_args()


def main():
    """Start converter."""

    args = parse_args()
    if args.input_file_path is None:
        if args.output_mode == 'flat':
            build_txt(args.output_mode, PAGE_SEPARATOR)
        else:
            build_txt()
            return
    else:
        if args.frequency is True:
            top_size = 10
            print(f"Frequency of words in input pdf-file top {top_size}:")
            complete_txt, page_counter = build_flat_txt_doc(
                args.input_file_path, f"{SENTENCE_SEPARATOR}\n\n")
            doc_name = count_phrase_frequency(complete_txt, page_counter,
                                              top_size)
            print(f'document name: <{doc_name}>')
            return

        if args.output_mode == 'flat':
            build_single_txt_doc(args.input_file_path, args.output_mode,
                                 PAGE_SEPARATOR)
            return
        else:
            build_single_txt_doc(args.input_file_path)
            return


if __name__ == "__main__":
    main()
