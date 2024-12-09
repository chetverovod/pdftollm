# pdftollm
Application makes decomposition of pdf-file to textual chunks and attributed pictures.

## Usage

### Help
```
./pdf_to_txt.py -h
```

### Config File 
Default  config file is: "pdf_to_txt.cfg":


| Variable name | Default value | Description |
|----|----|----|
|reference_docs_path| '../pdf_docs' | Select folder with reference pdf docs. |
|converted_docs_path | '../txt_from_pdf_docs' | Select folder with output txt docs. 
|extracted_images_path| '../extracted_images' | Select folder with output txt docs.| 
|source_tag| 'source' | Select reference text separator.|
|quote_tag| 'quote'| Select reference text separator.|
| print_context| True  # Print context which will be added to prompt.| 
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
./pdf_to_txt.py
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
exiftool -Description -docfile -imagefile -page -bbox ../extracted_images/Норникель_Внутрення_цена_на_углерод_image_p2_n5.png
Description                     : NiНикель (высокосортный)17%№1PtПлатина12%№1CuМедь2%№1PdПалладий43%№1RhРодий8%№1CoКобальт2%№1EBITDAмлрд долл.6,9Рентабельность EBITDA%48CAPEXмлрд долл.3,0ЧОКмлрд долл.3,1Разработка литиевого (Li) месторождения
DocFile                         : Норникель_Внутрення_цена_на_углерод.pdf
ImageFile                       : Норникель_Внутрення_цена_на_углерод_image_p2_n5.png
Page                            : 2
Bbox                            : (64, 72, 480, 497)
```



## Output txt data markup
### tag 'document'
Shows path to source document:

```
<document>
../pdf_docs/K2Tex_x_TeДо_Российский_рынок_ИТ_2024_30_стр.pdf
</document>
```

