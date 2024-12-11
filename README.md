# pdftollm
Application makes decomposition of pdf-file to textual chunks and attributed pictures for ColPALI and LLM.

Output text chunks are placed to a directory defined by 
Output picture has name like:
```
{EXTRACTED_IMAGES_PATH}/{base_filename}_image_p{page_counter}_i{image_counter}.png
```                                  

## Usage

### Help
```
./pdftollm.py -h
```

### Config File 
Default  config file is: "pdftollm.cfg":


| Variable name | Default value | Description |
|----|----|----|
|reference_docs_path| './pdf_docs' | Select folder with reference pdf docs. |
|extracted_chunks_path| './txt_from_pdf_docs' | Select folder with output txt docs. 
|extracted_images_path| './pict_from_pdf_docs' | Select folder with output txt docs.| 
|source_tag| 'source' | Select reference text separator.|
|quote_tag| 'quote'| Select reference text separator.|
|print_context| True  # Print context which will be added to prompt.| 
|drop_words | ['Документ предоставлен КонсультантПлюс\n', 'Документ предоставлен', 'www.consultant.ru', 
             'КонсультантПлюс', 'надежная правовая поддержка', 
             'r"Дата сохранения: \\d{2}\\.\\d{2}\\.\\d{4}"',
             'https://tiflocentre.ru/documents/gost-34428-2018.php', '07.02.2022, 08:11','1/61',
             'Используя наш сайт, вы соглашаетесь', 'с тем, что мы используем cookies. Ок']|

### Parse single PDF-file
```
python pdf_to_txt.py -i ../pdf_docs/K2Tex_x_TeДо_Российский_рынок_ИТ_2024_30_стр.pdf
```
Result:
```
Symbols in document: 159679
Page_counter: 30
Document name from page headers: <В>
page_count: 30
Beginning page not found.
beginig_page: None
30 pages found.
```
Extracted text is placed to a directory defined in variable <converted_docs_path> of config.

Extracted pictures are placed to a directory defined in variable <extracted_images_path> of config.
Each picture if it was covered by text is annotated by this text or text 'None'. Annotation is added to the picture as a meta data with key "Description'. Reading metadata.
<u>Example 1</u>:
```
exiftool -Description ../extracted_images/K2Tex_x_TeДо_Российский_рынок_ИТ_2024_30_стр_image_p22_n26.png
```
Result:
```
Description                     : ИТ-продуктами на рынке. Важно, чтобы новое ПО могло интегрироваться с уже существующими системами и инструментами, что позволяет бизнесам избежать больших затрат на полную замену инфраструктуры..Компания активно работает над обеспечением совместимости наших решений с популярными ИТ-продуктами других компаний-разработчиков, для этого в «Группе Астра» запущена программа технологического партнерства Ready for Astra, чтобы дать нашим клиентам свободу выбора и гибкость в построении их ИТ-ландшафта. Мы создаем бандлы и программные комплексы, совместно с производителями «железа» и софта презентуем ПАК..Антон Шмаков, технический директор «Группы Астра».Fplus в первую очередь сосредоточен на развитии функционала производимых устройств, поэтому тесно сотрудничает с компанией Baum. Мы формируем доверенную экосистему продуктов (аппаратная платформа, операционная система, виртуализация, база данных, средства кибербезопасности, прикладной софт) с «единым окном» сервисной поддержки..На рынке присутствует множество программных решений. Мы пошли по пути тестирования самых популярных из них на наших аппаратных решениях, чтобы предложить конечному пользователю готовый комплексный продукт..

```
### Parse group of PDF-files

Set desirable path in  variable reference_docs_path of config-file. 
Run parser:

```
./pdftollm.py
```

### Output image files metadata 
To the output images parser adds metadata with keys.

All key names:
 - Description - text which was found in bounding box of picture.
 - DocFile - file name of pdf-document where picture was captured.
 - ImageFile - self name of image file.
 - ImageIndex - global (in document) index of image begins from 0.
 - ParentImageFile - file name of image of page containing this image as a part.
 - Page - page of document where picture was captured. Page numbering begins from 0.
 - Bbox - bounding box of picture. Format: (x0, y1, x1, y0)
 Example: `(0, 291, 960, 457)`.
 
<u>Example 2</u>:
```
exiftool  ./pict_from_pdf_docs/2411.04952v1_image_p1_t1.png
ExifTool Version Number         : 12.40
File Name                       : 2411.04952v1_image_p1_t1.png
Directory                       : ./pict_from_pdf_docs
File Size                       : 40 KiB
File Modification Date/Time     : 2024:12:11 13:55:03+03:00
File Access Date/Time           : 2024:12:11 13:59:50+03:00
File Inode Change Date/Time     : 2024:12:11 13:55:03+03:00
File Permissions                : -rw-rw-r--
File Type                       : PNG
File Type Extension             : png
MIME Type                       : image/png
Image Width                     : 2076
Image Height                    : 531
Bit Depth                       : 8
Color Type                      : Palette
Compression                     : Deflate/Inflate
Filter                          : Adaptive
Interlace                       : Noninterlaced
Bbox                            : (117.90868238976628, 384.69728, 491.62392, 480.35882710553017)
Page                            : 1
Palette                         : (Binary data 768 bytes, use -b option to extract)
Image Size                      : 2076x531
Megapixels                      : 1.1

```



## Output txt data markup
### tag 'document'
Shows path to source document:

```
<document>
../pdf_docs/K2Tex_x_TeДо_Российский_рынок_ИТ_2024_30_стр.pdf
</document>
```

## Tests

```
 python3 -m pytest 
```
